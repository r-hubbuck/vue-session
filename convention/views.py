"""
Convention app views.

NOTE: Address and phone number management has been consolidated in the accounts app.
The following functions have been REMOVED from this file:
- set_primary_address: Use POST /api/accounts/addresses/{id}/set_primary/ instead
- set_primary_phone: Use POST /api/accounts/phone-numbers/{id}/set_primary/ instead  
- update_member_address_checkin: Use PUT /api/accounts/addresses/{id}/ instead

All address CRUD operations should go through the accounts.AddressViewSet which
includes the database sync logic to keep the older database in sync.
"""
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.throttling import UserRateThrottle
from django.shortcuts import get_object_or_404
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.db import transaction, IntegrityError
import bleach
import re

from .models import (
    Convention,
    ConventionRegistration,
    ConventionCommitteePreference,
    ConventionGuest,
    ConventionMeal,
    ConventionTravel,
    ConventionAccommodation,
    Airport,
)
from .serializers import (
    ConventionSerializer,
    ConventionRegistrationDetailSerializer,
    ConventionRegistrationCreateSerializer,
    MemberPersonalInfoSerializer,
    ConventionCommitteePreferenceSerializer,
    ConventionGuestSerializer,
    ConventionMealSerializer,
    ConventionTravelSerializer,
    ConventionAccommodationSerializer,
    EmergencyContactSerializer,
    AirportSerializer,
    AdminConventionTravelListSerializer,
    AdminConventionTravelUpdateSerializer,
    CheckInListSerializer,
    RegistrationStatusUpdateSerializer,
)
from accounts.models import Person, Address, PhoneNumber
import logging

# Set up logging for audit trail
logger = logging.getLogger(__name__)

# Get DOMAIN setting (same as used in other emails)
DOMAIN = getattr(settings, 'DOMAIN', 'localhost:8000')


# Custom rate throttle for admin endpoints
class AdminRateThrottle(UserRateThrottle):
    """
    Rate limiting for admin endpoints - 100 requests per hour.
    Matches the pattern used elsewhere in the application.
    """
    rate = '100/hour'


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_convention(request):
    """
    Get the current active convention.
    """
    try:
        convention = Convention.objects.filter(is_active=True).latest('year')
        serializer = ConventionSerializer(convention)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Convention.DoesNotExist:
        return Response(
            {'message': 'No active convention found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_convention_meals(request):
    """
    Get active meal options for the current convention.
    """
    try:
        convention = Convention.objects.filter(is_active=True).latest('year')
    except Convention.DoesNotExist:
        return Response([], status=status.HTTP_200_OK)

    meals = ConventionMeal.objects.filter(convention=convention, is_active=True)
    serializer = ConventionMealSerializer(meals, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def my_registration(request):
    """
    GET: Get the current user's registration for the active convention.
    POST: Create a new registration for the active convention.
    """
    if not (hasattr(request.user, 'person') and request.user.person is not None):
        return Response(
            {'message': 'User must have an associated person record'},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        convention = Convention.objects.filter(is_active=True).latest('year')
    except Convention.DoesNotExist:
        return Response(
            {'message': 'No active convention found'},
            status=status.HTTP_404_NOT_FOUND
        )

    if request.method == 'GET':
        try:
            registration = ConventionRegistration.objects.get(
                convention=convention,
                person=request.user.person
            )
            serializer = ConventionRegistrationDetailSerializer(registration)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ConventionRegistration.DoesNotExist:
            return Response(
                {'message': 'No registration found', 'has_registration': False},
                status=status.HTTP_200_OK
            )

    elif request.method == 'POST':
        # Check if registration already exists (pre-check before acquiring lock)
        if ConventionRegistration.objects.filter(
            convention=convention,
            person=request.user.person
        ).exists():
            return Response(
                {'message': 'You are already registered for this convention'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create registration
        serializer = ConventionRegistrationCreateSerializer(
            data={'convention': convention.id}
        )
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    # Re-check inside lock to prevent race conditions
                    person = Person.objects.select_for_update().get(
                        pk=request.user.person.pk
                    )
                    if ConventionRegistration.objects.filter(
                        convention=convention, person=person
                    ).exists():
                        return Response(
                            {'message': 'You are already registered for this convention'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    registration = serializer.save(person=person)
            except IntegrityError:
                return Response(
                    {'message': 'You are already registered for this convention'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            detail_serializer = ConventionRegistrationDetailSerializer(registration)
            return Response(
                detail_serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_registration_confirmation(request, registration_id):
    """
    Send the convention registration confirmation email.
    Called by the frontend when all sections are complete.
    Only sends once — guarded by confirmation_email_sent flag.
    """
    registration = get_object_or_404(
        ConventionRegistration,
        id=registration_id,
        person=request.user.person
    )

    if registration.confirmation_email_sent:
        return Response({'message': 'Confirmation email already sent.'}, status=status.HTTP_200_OK)

    try:
        person = registration.person
        convention = registration.convention
        mail_subject = f'{convention.name} Registration Received'
        message = render_to_string('convention/registration_confirmation_email.html', {
            'person': person,
            'convention': convention,
            'registration': registration,
            'domain': DOMAIN,
        })
        if not hasattr(person, 'user') or not person.user:
            raise Exception("Person has no associated user account")
        email_msg = EmailMultiAlternatives(
            subject=mail_subject,
            body='',
            to=[person.user.email]
        )
        email_msg.attach_alternative(message, "text/html")
        email_msg.send()

        registration.confirmation_email_sent = True
        registration.save(update_fields=['confirmation_email_sent'])

        logger.info(
            f"Registration confirmation email sent to {person.user.email}",
            extra={'person_id': person.id, 'registration_id': registration.id}
        )
        return Response({'message': 'Confirmation email sent.'}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Failed to send registration confirmation email: {str(e)}")
        return Response({'error': 'Failed to send confirmation email.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_member_info(request):
    """
    Update person's preferred_first_name (for badge name).
    This updates the Person model directly - no duplication.
    """
    if not (hasattr(request.user, 'person') and request.user.person is not None):
        return Response(
            {'message': 'User must have an associated person record'},
            status=status.HTTP_403_FORBIDDEN
        )

    person = request.user.person

    # Update preferred_first_name if provided
    if 'preferred_first_name' in request.data:
        person.preferred_first_name = bleach.clean(
            str(request.data['preferred_first_name']), tags=[], strip=True
        ).strip()
        person.save()

    serializer = MemberPersonalInfoSerializer(person)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_mobile_phone(request):
    """
    Update or create mobile phone number for the person.
    """
    if not (hasattr(request.user, 'person') and request.user.person is not None):
        return Response(
            {'message': 'User must have an associated person record'},
            status=status.HTTP_403_FORBIDDEN
        )

    person = request.user.person
    phone_number = request.data.get('phone_number', '').strip()

    if not phone_number:
        return Response(
            {'message': 'Phone number is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Clean and validate phone number
    clean_number = re.sub(r'\D', '', phone_number)
    if not clean_number:
        return Response(
            {'message': 'Phone number must contain digits.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    if len(clean_number) < 10 or len(clean_number) > 15:
        return Response(
            {'message': 'Phone number must be between 10 and 15 digits.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    if len(set(clean_number)) == 1:
        return Response(
            {'message': 'Please enter a valid phone number.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    if len(clean_number) == 10 and (clean_number[0] in ('0', '1') or clean_number[3] in ('0', '1')):
        return Response(
            {'message': 'Please enter a valid phone number.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    phone_number = clean_number

    # Get or create mobile phone
    mobile_phone, created = PhoneNumber.objects.get_or_create(
        person=person,
        phone_type='Mobile',
        defaults={'phone_number': phone_number, 'is_primary': True}
    )
    
    if not created:
        # Update existing mobile phone
        mobile_phone.phone_number = phone_number
        mobile_phone.save()
    
    return Response(
        {
            'message': 'Mobile phone updated successfully',
            'phone': {
                'id': mobile_phone.id,
                'phone_number': mobile_phone.phone_number,
                'formatted_number': mobile_phone.get_formatted_number(),
                'phone_type': mobile_phone.phone_type,
                'is_primary': mobile_phone.is_primary
            }
        },
        status=status.HTTP_200_OK
    )
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_committee_preferences(request, registration_id):
    """
    Update committee preferences for a registration.
    """
    registration = get_object_or_404(
        ConventionRegistration,
        id=registration_id,
        person=request.user.person
    )
    
    preferences, created = ConventionCommitteePreference.objects.get_or_create(
        registration=registration
    )
    
    serializer = ConventionCommitteePreferenceSerializer(
        preferences,
        data=request.data,
        partial=True
    )
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def guest_management(request, registration_id):
    """
    GET: Get all guests for a registration.
    POST: Add a guest to a registration.
    """
    registration = get_object_or_404(
        ConventionRegistration,
        id=registration_id,
        person=request.user.person
    )
    
    if request.method == 'GET':
        guests = ConventionGuest.objects.filter(registration=registration)
        serializer = ConventionGuestSerializer(guests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        serializer = ConventionGuestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(registration=registration)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def guest_detail(request, registration_id, guest_id):
    """
    PUT: Update a guest.
    DELETE: Remove a guest.
    """
    registration = get_object_or_404(
        ConventionRegistration,
        id=registration_id,
        person=request.user.person
    )
    
    guest = get_object_or_404(
        ConventionGuest,
        id=guest_id,
        registration=registration
    )
    
    if request.method == 'PUT':
        serializer = ConventionGuestSerializer(guest, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        guest.delete()
        return Response(
            {'message': 'Guest removed successfully'},
            status=status.HTTP_200_OK
        )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_travel(request, registration_id):
    """
    Update travel information for a registration.
    """
    registration = get_object_or_404(
        ConventionRegistration,
        id=registration_id,
        person=request.user.person
    )
    
    travel, created = ConventionTravel.objects.get_or_create(
        registration=registration
    )
    
    serializer = ConventionTravelSerializer(
        travel,
        data=request.data,
        partial=True
    )
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    logger.debug("Travel validation errors: %s | data: %s", serializer.errors, request.data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_accommodation(request, registration_id):
    """
    Update accommodation information for a registration.
    """
    registration = get_object_or_404(
        ConventionRegistration,
        id=registration_id,
        person=request.user.person
    )
    
    accommodation, created = ConventionAccommodation.objects.get_or_create(
        registration=registration
    )
    
    serializer = ConventionAccommodationSerializer(
        accommodation,
        data=request.data,
        partial=True
    )
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_emergency_contact(request, registration_id):
    """
    Update emergency contact information for a registration.
    """
    registration = get_object_or_404(
        ConventionRegistration,
        id=registration_id,
        person=request.user.person
    )

    serializer = EmergencyContactSerializer(
        registration,
        data=request.data,
        partial=True
    )

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_airports(request):
    """
    Get all airports, optionally filtered by state.
    Query params:
      - state: Two-letter state code (optional)
    """
    state = request.query_params.get('state', None)
    
    if state:
        airports = Airport.objects.filter(state=state.upper())
    else:
        airports = Airport.objects.all()
    
    serializer = AirportSerializer(airports, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_states(request):
    """
    Get list of unique states that have airports.
    Returns list of state codes and names.
    """
    # Get unique states from Airport model
    states = Airport.objects.values_list('state', flat=True).distinct().order_by('state')
    
    # Map state codes to names
    state_names = {
        'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas',
        'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware',
        'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho',
        'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas',
        'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
        'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi',
        'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada',
        'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York',
        'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma',
        'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
        'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah',
        'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia',
        'WI': 'Wisconsin', 'WY': 'Wyoming', 'DC': 'District of Columbia'
    }
    
    state_list = [
        {'code': state, 'name': state_names.get(state, state)}
        for state in states
    ]
    
    return Response(state_list, status=status.HTTP_200_OK)


# Admin views

STAFF_ADMIN_ROLES = ['hq_staff', 'hq_finance', 'executive_council']

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([AdminRateThrottle])
def admin_travel_list(request):
    """
    Admin view to list all travel registrations with member information.
    Restricted to hq_staff, hq_finance, and executive_council roles.
    Rate limited to 100 requests per hour per user.
    Query params:
      - convention_id: Filter by convention (optional, defaults to active convention)
      - travel_method: Filter by travel method (optional)
      - booked: Filter by booking status ('true' for booked flights, 'false' for pending)
    """
    if not any(request.user.has_role(role) for role in STAFF_ADMIN_ROLES):
        return Response(
            {'message': 'You do not have permission to access admin travel data.'},
            status=status.HTTP_403_FORBIDDEN
        )

    # Audit log
    logger.info(
        f"Admin travel list accessed by user {request.user.email or request.user.username}",
        extra={
            'user_id': request.user.id,
            'action': 'admin_travel_list_view',
            'filters': {
                'convention_id': request.query_params.get('convention_id'),
                'travel_method': request.query_params.get('travel_method'),
                'booked': request.query_params.get('booked'),
            }
        }
    )
    
    # Get convention filter
    convention_id = request.query_params.get('convention_id', None)
    
    if convention_id:
        convention = get_object_or_404(Convention, id=convention_id)
    else:
        try:
            convention = Convention.objects.filter(is_active=True).latest('year')
        except Convention.DoesNotExist:
            return Response(
                {'message': 'No active convention found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    # Get all travel records for the convention
    travels = ConventionTravel.objects.filter(
        registration__convention=convention
    ).select_related('registration__person')

    # Filter by travel method if specified
    travel_method = request.query_params.get('travel_method', None)
    if travel_method:
        travels = travels.filter(travel_method=travel_method)
    
    # Filter by booking status if specified
    booked_filter = request.query_params.get('booked', None)
    if booked_filter == 'true':
        # Has booked flights (both outbound and return flight numbers exist)
        travels = travels.exclude(outbound_flight_number='').exclude(return_flight_number='')
    elif booked_filter == 'false':
        # No booked flights (missing either outbound or return flight number)
        from django.db.models import Q
        travels = travels.filter(
            Q(outbound_flight_number='') | Q(return_flight_number='') | 
            Q(outbound_flight_number__isnull=True) | Q(return_flight_number__isnull=True)
        )
    
    # Order by person last name
    travels = travels.order_by('registration__person__last_name', 'registration__person__first_name')
    
    serializer = AdminConventionTravelListSerializer(travels, many=True)
    
    logger.info(
        f"Admin travel list returned {len(serializer.data)} records",
        extra={'user_id': request.user.id, 'record_count': len(serializer.data)}
    )
    
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
@throttle_classes([AdminRateThrottle])
def admin_travel_detail(request, travel_id):
    """
    Admin view to get or update a specific travel record.
    Rate limited to 100 requests per hour per user.
    GET: Get full travel details including member info
    PUT: Update booked flight information
    """
    if not any(request.user.has_role(role) for role in STAFF_ADMIN_ROLES):
        return Response(
            {'message': 'You do not have permission to access admin travel data.'},
            status=status.HTTP_403_FORBIDDEN
        )

    travel = get_object_or_404(
        ConventionTravel.objects.select_related('registration__person'),
        id=travel_id
    )

    if request.method == 'GET':
        # Audit log
        logger.info(
            f"Admin viewed travel details for travel_id={travel_id}",
            extra={
                'user_id': request.user.id,
                'action': 'admin_travel_detail_view',
                'travel_id': travel_id,
                'person_id': travel.registration.person.id
            }
        )

        # Return full travel details with person info
        person = travel.registration.person
        
        # Get airport descriptions
        departure_airport_info = None
        return_airport_info = None
        
        if travel.departure_airport:
            try:
                airport = Airport.objects.get(code=travel.departure_airport)
                departure_airport_info = {
                    'code': airport.code,
                    'state': airport.state,
                    'description': airport.description
                }
            except Airport.DoesNotExist:
                pass
        
        if travel.return_airport:
            try:
                airport = Airport.objects.get(code=travel.return_airport)
                return_airport_info = {
                    'code': airport.code,
                    'state': airport.state,
                    'description': airport.description
                }
            except Airport.DoesNotExist:
                pass
        
        # Build response with all details
        travel_serializer = ConventionTravelSerializer(travel)
        
        member = person.member if hasattr(person, 'member') else None
        response_data = {
            'id': travel.id,
            'registration_id': travel.registration.id,
            'member': {
                'id': person.id,
                'member_number': member.member_id if member else None,
                'first_name': person.first_name,
                'last_name': person.last_name,
                'chapter_code': member.chapter_code if member else None,
            },
            'travel': travel_serializer.data,
            'departure_airport_info': departure_airport_info,
            'return_airport_info': return_airport_info,
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        # Store original values for audit log
        original_data = {
            'outbound_flight': travel.outbound_flight_number,
            'return_flight': travel.return_flight_number,
            'outbound_airline': travel.outbound_airline,
            'return_airline': travel.return_airline,
        }
        
        # Admin updates booked flight information
        serializer = AdminConventionTravelUpdateSerializer(
            travel,
            data=request.data,
            partial=True
        )
        
        if serializer.is_valid():
            updated_travel = serializer.save()
            
            # Audit log - record what was changed
            changes = {}
            for field in ['outbound_airline', 'outbound_flight_number', 'outbound_confirmation',
                         'return_airline', 'return_flight_number', 'return_confirmation']:
                old_value = getattr(travel, field, None)
                new_value = serializer.validated_data.get(field, old_value)
                if old_value != new_value:
                    changes[field] = {'old': old_value, 'new': new_value}
            
            logger.info(
                f"Admin updated travel booking for travel_id={travel_id}",
                extra={
                    'user_id': request.user.id,
                    'user_email': request.user.email or request.user.username,
                    'action': 'admin_travel_update',
                    'travel_id': travel_id,
                    'person_id': travel.registration.person.id,
                    'person_name': f"{travel.registration.person.first_name} {travel.registration.person.last_name}",
                    'changes': changes,
                }
            )
            
            # Send flight booking confirmation email if both flights are booked
            # Refresh the travel object to get the updated data
            updated_travel.refresh_from_db()
            if updated_travel.outbound_flight_number and updated_travel.return_flight_number:
                try:
                    # Send flight confirmation email (inline - matches existing pattern)
                    person = updated_travel.registration.person
                    convention = updated_travel.registration.convention
                    mail_subject = f'{convention.name} - Your Flight Details'

                    message = render_to_string('convention/flight_booking_confirmation_email.html', {
                        'person': person,
                        'convention': convention,
                        'travel': updated_travel,
                        'registration': updated_travel.registration,
                        'domain': DOMAIN,
                    })

                    if not hasattr(person, 'user') or not person.user:
                        raise Exception("Person has no associated user account")
                    to_email = person.user.email
                    email_msg = EmailMultiAlternatives(
                        subject=mail_subject,
                        body='',
                        to=[to_email]
                    )
                    email_msg.attach_alternative(message, "text/html")
                    email_msg.send()
                    
                    logger.info(
                        f"Flight booking confirmation email sent to {to_email}",
                        extra={
                            'person_id': person.id,
                            'travel_id': updated_travel.id,
                            'convention_id': convention.id,
                            'outbound_flight': updated_travel.outbound_flight_number,
                            'return_flight': updated_travel.return_flight_number
                        }
                    )
                except Exception as e:
                    # Log error but don't fail the update
                    logger.error(
                        f"Failed to send flight booking confirmation email: {str(e)}",
                        extra={
                            'travel_id': travel_id,
                            'person_id': travel.registration.person.id,
                            'error': str(e)
                        }
                    )
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        # Log validation errors
        logger.warning(
            f"Admin travel update failed validation for travel_id={travel_id}",
            extra={
                'user_id': request.user.id,
                'action': 'admin_travel_update_failed',
                'travel_id': travel_id,
                'errors': serializer.errors
            }
        )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([AdminRateThrottle])
def check_in_list(request):
    """
    Get all registrations for the active convention for check-in.
    Requires hq_staff or member role.
    """
    if not any(request.user.has_role(r) for r in ['hq_staff', 'member']):
        raise PermissionDenied('You do not have permission to access check-in.')
    
    try:
        convention = Convention.objects.filter(is_active=True).latest('year')
    except Convention.DoesNotExist:
        return Response(
            {'message': 'No active convention found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Get all registrations for the current convention, excluding guests
    registrations = ConventionRegistration.objects.filter(
        convention=convention,
        is_guest=False
    ).select_related('person').prefetch_related('guest_details', 'person__addresses', 'person__phone_numbers')
    
    serializer = CheckInListSerializer(registrations, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@throttle_classes([AdminRateThrottle])
def update_registration_status(request, registration_id):
    """
    Update registration status for check-in or cancellation.
    Staff only.
    """
    # Check if user has staff permissions
    if not any(request.user.has_role(r) for r in ['hq_staff', 'member']):
        raise PermissionDenied('You do not have permission to update registration status.')
    
    registration = get_object_or_404(ConventionRegistration, id=registration_id)
    
    serializer = RegistrationStatusUpdateSerializer(
        registration,
        data=request.data,
        partial=True
    )
    
    if serializer.is_valid():
        serializer.save()
        
        # Log the status change
        logger.info(
            f"Registration status updated for {registration.person}",
            extra={
                'registration_id': registration.id,
                'person_id': registration.person.id,
                'new_status': serializer.validated_data.get('status_code'),
                'updated_by': request.user.email,
            }
        )

        # Return updated registration with full details
        updated_registration = ConventionRegistration.objects.select_related(
            'person'
        ).prefetch_related('guest_details', 'person__addresses', 'person__phone_numbers').get(id=registration_id)
        
        response_serializer = CheckInListSerializer(updated_registration)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@throttle_classes([AdminRateThrottle])
def staff_update_address(request, person_id, address_id):
    """
    Staff: update any person's address fields during check-in.
    Requires hq_staff or member role.
    """
    if not any(request.user.has_role(r) for r in ['hq_staff', 'member']):
        raise PermissionDenied('You do not have permission to update member information.')

    person = get_object_or_404(Person, id=person_id)
    address = get_object_or_404(Address, id=address_id, person=person)

    # Block add_type changes: the accounts AddressSerializer's uniqueness check requires
    # request context (which we omit for staff), so a type change would bypass validation
    # and raise an IntegrityError at the DB level instead of a clean 400.
    if 'add_type' in request.data and request.data['add_type'] != address.add_type:
        return Response({'error': 'Address type cannot be changed here.'}, status=status.HTTP_400_BAD_REQUEST)

    # Use accounts AddressSerializer for full bleach + state validation
    from accounts.serializers import AddressSerializer as AccountsAddressSerializer
    from accounts.db_sync import sync_address_to_sql
    serializer = AccountsAddressSerializer(address, data=request.data, partial=True)
    if serializer.is_valid():
        # Capture pre-save data for SQL Server update matching
        old_address_data = {
            'add_line1': address.add_line1,
            'add_line2': address.add_line2,
            'add_city': address.add_city,
            'add_state': address.add_state,
            'add_zip': address.add_zip,
            'add_type': address.add_type,
        }
        with transaction.atomic():
            serializer.save()
        address.refresh_from_db()
        # Sync to legacy SQL Server database
        member_id = getattr(getattr(person, 'member', None), 'member_id', None)
        if member_id:
            new_address_data = {
                'add_line1': address.add_line1,
                'add_line2': address.add_line2,
                'add_city': address.add_city,
                'add_state': address.add_state,
                'add_zip': address.add_zip,
                'add_type': address.add_type,
            }
            sync_address_to_sql('update', member_id, new_address_data, old_address_data)
        from .serializers import AddressSerializer as ConventionAddressSerializer
        return Response(ConventionAddressSerializer(address).data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([AdminRateThrottle])
def staff_set_primary_address(request, person_id, address_id):
    """
    Staff: set one of a person's addresses as primary.
    Requires hq_staff or member role.
    """
    if not any(request.user.has_role(r) for r in ['hq_staff', 'member']):
        raise PermissionDenied('You do not have permission to update member information.')

    person = get_object_or_404(Person, id=person_id)
    address = get_object_or_404(Address, id=address_id, person=person)

    with transaction.atomic():
        person.addresses.update(is_primary=False)
        address.is_primary = True
        address.save()

    from .serializers import AddressSerializer as ConventionAddressSerializer
    return Response(ConventionAddressSerializer(address).data, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@throttle_classes([AdminRateThrottle])
def staff_update_mobile_phone(request, person_id):
    """
    Staff: update or create a person's Mobile phone number during check-in.
    Requires hq_staff or member role.
    """
    if not any(request.user.has_role(r) for r in ['hq_staff', 'member']):
        raise PermissionDenied('You do not have permission to update member information.')

    person = get_object_or_404(Person, id=person_id)

    country_code = bleach.clean(str(request.data.get('country_code', '1')), tags=[], strip=True).strip() or '1'
    phone_number = bleach.clean(str(request.data.get('phone_number', '')), tags=[], strip=True).strip()

    clean_digits = re.sub(r'\D', '', phone_number)
    if not clean_digits:
        return Response({'phone_number': 'Phone number must contain digits.'}, status=status.HTTP_400_BAD_REQUEST)
    if len(clean_digits) < 10 or len(clean_digits) > 15:
        return Response({'phone_number': 'Phone number must be between 10 and 15 digits.'}, status=status.HTTP_400_BAD_REQUEST)
    if len(set(clean_digits)) == 1:
        return Response({'phone_number': 'Phone number appears invalid (all identical digits).'}, status=status.HTTP_400_BAD_REQUEST)
    if len(clean_digits) == 10:
        if clean_digits[0] in ('0', '1') or clean_digits[3] in ('0', '1'):
            return Response({'phone_number': 'Please enter a valid US phone number.'}, status=status.HTTP_400_BAD_REQUEST)

    with transaction.atomic():
        phone, created = PhoneNumber.objects.get_or_create(
            person=person,
            phone_type='Mobile',
            defaults={'country_code': country_code, 'phone_number': clean_digits},
        )
        if not created:
            phone.country_code = country_code
            phone.phone_number = clean_digits
            phone.save()

    # Sync to legacy SQL Server database
    from accounts.db_sync import sync_phone_to_sql
    member_id = getattr(getattr(person, 'member', None), 'member_id', None)
    if member_id:
        sync_phone_to_sql('create' if created else 'update', member_id, 'Mobile', clean_digits)

    from .serializers import PhoneNumberSerializer as ConventionPhoneSerializer
    return Response(ConventionPhoneSerializer(phone).data, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_recruiter_visibility(request, registration_id):
    """
    Update visible_to_recruiters for a registration.
    """
    if not (hasattr(request.user, 'person') and request.user.person is not None):
        return Response(
            {'error': 'No person profile.'},
            status=status.HTTP_403_FORBIDDEN
        )

    registration = get_object_or_404(
        ConventionRegistration,
        id=registration_id,
        person=request.user.person
    )

    value = request.data.get('visible_to_recruiters')
    if value is not None:
        allowed = [c[0] for c in ConventionRegistration.VISIBILITY_CHOICES]
        if value not in allowed:
            return Response(
                {'error': f"visible_to_recruiters must be one of: {', '.join(allowed)}."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        registration.visible_to_recruiters = value
        registration.save(update_fields=['visible_to_recruiters'])

    return Response({'visible_to_recruiters': registration.visible_to_recruiters})


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_guest_attending(request, registration_id):
    """
    Update guest_attending for a registration.
    Accepts: { "guest_attending": true | false }
    """
    if not (hasattr(request.user, 'person') and request.user.person is not None):
        return Response(
            {'error': 'No person profile.'},
            status=status.HTTP_403_FORBIDDEN
        )

    registration = get_object_or_404(
        ConventionRegistration,
        id=registration_id,
        person=request.user.person
    )

    value = request.data.get('guest_attending')
    if value is None:
        return Response(
            {'error': 'guest_attending is required.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    if not isinstance(value, bool):
        return Response(
            {'error': 'guest_attending must be true or false.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    registration.guest_attending = value
    registration.save(update_fields=['guest_attending'])

    return Response({'guest_attending': registration.guest_attending})
