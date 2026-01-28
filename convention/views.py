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

from .models import (
    Convention,
    ConventionRegistration,
    ConventionCommitteePreference,
    ConventionGuest,
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
    ConventionTravelSerializer,
    ConventionAccommodationSerializer,
    AirportSerializer,
    AdminConventionTravelListSerializer,
    AdminConventionTravelUpdateSerializer,
    CheckInListSerializer,
    AddressUpdateSerializer,
    RegistrationStatusUpdateSerializer,
)
from accounts.models import Member, Address, PhoneNumber
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


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def my_registration(request):
    """
    GET: Get the current user's registration for the active convention.
    POST: Create a new registration for the active convention.
    """
    if not hasattr(request.user, 'member'):
        return Response(
            {'message': 'User must have an associated member record'},
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
                member=request.user.member
            )
            serializer = ConventionRegistrationDetailSerializer(registration)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ConventionRegistration.DoesNotExist:
            return Response(
                {'message': 'No registration found', 'has_registration': False},
                status=status.HTTP_200_OK
            )
    
    elif request.method == 'POST':
        # Check if registration already exists
        if ConventionRegistration.objects.filter(
            convention=convention,
            member=request.user.member
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
            registration = serializer.save(member=request.user.member)
            
            # Send confirmation email (inline - matches account activation pattern)
            try:
                member = registration.member
                convention = registration.convention
                mail_subject = f'{convention.name} Registration Received'
                
                message = render_to_string('convention/registration_confirmation_email.html', {
                    'member': member,
                    'convention': convention,
                    'registration': registration,
                    'domain': DOMAIN,
                })
                
                to_email = member.user.email  # Email is on User, not Member
                email_msg = EmailMultiAlternatives(
                    subject=mail_subject,
                    body='',
                    to=[to_email]
                )
                email_msg.attach_alternative(message, "text/html")
                email_msg.send()
                
                logger.info(
                    f"Registration confirmation email sent to {to_email}",
                    extra={
                        'member_id': member.id,
                        'registration_id': registration.id,
                        'convention_id': convention.id
                    }
                )
            except Exception as e:
                # Log error but don't fail the registration
                logger.error(
                    f"Failed to send registration confirmation email: {str(e)}",
                    extra={
                        'registration_id': registration.id,
                        'member_id': request.user.member.id,
                        'error': str(e)
                    }
                )
            
            detail_serializer = ConventionRegistrationDetailSerializer(registration)
            return Response(
                detail_serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_member_info(request):
    """
    Update member's preferred_first_name (for badge name).
    This updates the Member model directly - no duplication.
    """
    if not hasattr(request.user, 'member'):
        return Response(
            {'message': 'User must have an associated member record'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    member = request.user.member
    
    # Update preferred_first_name if provided
    if 'preferred_first_name' in request.data:
        member.preferred_first_name = request.data['preferred_first_name']
        member.save()
    
    serializer = MemberPersonalInfoSerializer(member)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_mobile_phone(request):
    """
    Update or create mobile phone number for the member.
    """
    if not hasattr(request.user, 'member'):
        return Response(
            {'message': 'User must have an associated member record'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    member = request.user.member
    phone_number = request.data.get('phone_number', '').strip()
    
    if not phone_number:
        return Response(
            {'message': 'Phone number is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get or create mobile phone
    mobile_phone, created = PhoneNumber.objects.get_or_create(
        member=member,
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
def set_primary_address(request, address_id):
    """
    Set an address as primary for convention correspondence.
    Unsets any other primary address for this member.
    """
    if not hasattr(request.user, 'member'):
        return Response(
            {'message': 'User must have an associated member record'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Verify address belongs to this member
    address = get_object_or_404(
        Address,
        id=address_id,
        member=request.user.member
    )
    
    # Unset all other primary addresses
    Address.objects.filter(member=request.user.member).update(is_primary=False)
    
    # Set this one as primary
    address.is_primary = True
    address.save()
    
    return Response(
        {'message': 'Primary address updated', 'address_id': address_id},
        status=status.HTTP_200_OK
    )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def set_primary_phone(request, phone_id):
    """
    Set a phone number as primary.
    Unsets any other primary phone for this member.
    """
    if not hasattr(request.user, 'member'):
        return Response(
            {'message': 'User must have an associated member record'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Verify phone belongs to this member
    phone = get_object_or_404(
        PhoneNumber,
        id=phone_id,
        member=request.user.member
    )
    
    # Unset all other primary phones
    PhoneNumber.objects.filter(member=request.user.member).update(is_primary=False)
    
    # Set this one as primary
    phone.is_primary = True
    phone.save()
    
    return Response(
        {'message': 'Primary phone updated', 'phone_id': phone_id},
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
        member=request.user.member
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
        member=request.user.member
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
        member=request.user.member
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
        member=request.user.member
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
    
    # Log the validation errors for debugging
    print("Travel validation errors:", serializer.errors)
    print("Request data:", request.data)
    
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
        member=request.user.member
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
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([AdminRateThrottle])
def admin_travel_list(request):
    """
    Admin view to list all travel registrations with member information.
    Rate limited to 100 requests per hour per user.
    Query params:
      - convention_id: Filter by convention (optional, defaults to active convention)
      - travel_method: Filter by travel method (optional)
      - booked: Filter by booking status ('true' for booked flights, 'false' for pending)
    """
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
    ).select_related('registration__member')
    
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
    
    # Order by member last name
    travels = travels.order_by('registration__member__last_name', 'registration__member__first_name')
    
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
    travel = get_object_or_404(
        ConventionTravel.objects.select_related('registration__member'),
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
                'member_id': travel.registration.member.id
            }
        )
        
        # Return full travel details with member info
        member = travel.registration.member
        
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
        
        response_data = {
            'id': travel.id,
            'registration_id': travel.registration.id,
            'member': {
                'id': member.id,
                'member_number': member.member_id,
                'first_name': member.first_name,
                'last_name': member.last_name,
                'chapter': member.chapter,
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
                    'member_id': travel.registration.member.id,
                    'member_name': f"{travel.registration.member.first_name} {travel.registration.member.last_name}",
                    'changes': changes,
                }
            )
            
            # Send flight booking confirmation email if both flights are booked
            # Refresh the travel object to get the updated data
            updated_travel.refresh_from_db()
            if updated_travel.outbound_flight_number and updated_travel.return_flight_number:
                try:
                    # Send flight confirmation email (inline - matches existing pattern)
                    member = updated_travel.registration.member
                    convention = updated_travel.registration.convention
                    mail_subject = f'{convention.name} - Your Flight Details'
                    
                    message = render_to_string('convention/flight_booking_confirmation_email.html', {
                        'member': member,
                        'convention': convention,
                        'travel': updated_travel,
                        'registration': updated_travel.registration,
                        'domain': DOMAIN,
                    })
                    
                    to_email = member.user.email  # Email is on User, not Member
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
                            'member_id': member.id,
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
                            'member_id': travel.registration.member.id,
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
def check_in_list(request):
    """
    Get all registrations for the active convention for check-in.
    Staff only - requires appropriate permissions.
    """
    # Check if user has staff permissions
    if not request.user.is_staff:
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
    ).select_related('member').prefetch_related('guest_details', 'member__addresses')
    
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
    if not request.user.is_staff:
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
            f"Registration status updated for {registration.member}",
            extra={
                'registration_id': registration.id,
                'member_id': registration.member.id,
                'new_status': serializer.validated_data.get('status_code'),
                'updated_by': request.user.email,
            }
        )
        
        # Return updated registration with full details
        updated_registration = ConventionRegistration.objects.select_related(
            'member'
        ).prefetch_related('guest_details', 'member__addresses').get(id=registration_id)
        
        response_serializer = CheckInListSerializer(updated_registration)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@throttle_classes([AdminRateThrottle])
def update_member_address_checkin(request, address_id):
    """
    Update a member's address during check-in.
    Staff only - allows updating any member's address.
    """
    # Check if user has staff permissions
    if not request.user.is_staff:
        raise PermissionDenied('You do not have permission to update member addresses.')
    
    address = get_object_or_404(Address, id=address_id)
    
    serializer = AddressUpdateSerializer(
        address,
        data=request.data,
        partial=True
    )
    
    if serializer.is_valid():
        serializer.save()
        
        # Log the address update
        logger.info(
            f"Address updated during check-in for member {address.member}",
            extra={
                'address_id': address.id,
                'member_id': address.member.id,
                'updated_by': request.user.email,
            }
        )
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)