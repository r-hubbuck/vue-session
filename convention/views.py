from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

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
)
from accounts.models import Member, Address, PhoneNumbers


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
    mobile_phone, created = PhoneNumbers.objects.get_or_create(
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
        PhoneNumbers,
        id=phone_id,
        member=request.user.member
    )
    
    # Unset all other primary phones
    PhoneNumbers.objects.filter(member=request.user.member).update(is_primary=False)
    
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

