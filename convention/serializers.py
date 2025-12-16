from rest_framework import serializers
from .models import (
    Convention,
    ConventionRegistration,
    ConventionCommitteePreference,
    ConventionGuest,
    ConventionTravel,
    ConventionAccommodation,
)
from accounts.models import Member, Address, PhoneNumbers


class ConventionSerializer(serializers.ModelSerializer):
    registration_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Convention
        fields = [
            'id',
            'name',
            'year',
            'location',
            'start_date',
            'end_date',
            'registration_open_date',
            'registration_close_date',
            'is_active',
            'registration_status',
        ]
    
    def get_registration_status(self, obj):
        """Determine if registration is open, closed, or upcoming"""
        from django.utils import timezone
        now = timezone.now().date()
        
        if not obj.registration_open_date or not obj.registration_close_date:
            return "not_set"
        
        if now < obj.registration_open_date:
            return "upcoming"
        elif obj.registration_open_date <= now <= obj.registration_close_date:
            return "open"
        else:
            return "closed"


class AddressSerializer(serializers.ModelSerializer):
    """Serializer for member addresses"""
    class Meta:
        model = Address
        fields = [
            'id', 
            'add_line1', 
            'add_line2', 
            'add_city', 
            'add_state', 
            'add_zip', 
            'add_country', 
            'add_type',
            'is_primary'
        ]


class PhoneNumberSerializer(serializers.ModelSerializer):
    """Serializer for member phone numbers"""
    formatted_number = serializers.SerializerMethodField()
    
    class Meta:
        model = PhoneNumbers
        fields = [
            'id', 
            'country_code', 
            'phone_number', 
            'formatted_number', 
            'phone_type', 
            'is_primary'
        ]
    
    def get_formatted_number(self, obj):
        return obj.get_formatted_number()


class MemberPersonalInfoSerializer(serializers.ModelSerializer):
    """
    Serializer for member personal info used in convention registration.
    Pulls from Member model - no duplication.
    """
    badge_name = serializers.SerializerMethodField()
    primary_phone = serializers.SerializerMethodField()
    primary_address = serializers.SerializerMethodField()
    
    class Meta:
        model = Member
        fields = [
            'id',
            'first_name',
            'last_name',
            'preferred_first_name',
            'badge_name',
            'chapter',
            'primary_phone',
            'primary_address',
        ]
        read_only_fields = ['first_name', 'last_name', 'chapter', 'badge_name', 'primary_phone', 'primary_address']
    
    def get_badge_name(self, obj):
        """Compute badge name from preferred_first_name + last_name"""
        return obj.get_badge_name()
    
    def get_primary_phone(self, obj):
        """Get primary phone number"""
        try:
            primary_phone = obj.phone_numbers.filter(is_primary=True).first()
            if primary_phone:
                return PhoneNumberSerializer(primary_phone).data
        except:
            pass
        return None
    
    def get_primary_address(self, obj):
        """Get primary address"""
        try:
            primary_address = obj.addresses.filter(is_primary=True).first()
            if primary_address:
                return AddressSerializer(primary_address).data
        except:
            pass
        return None


class ConventionCommitteePreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConventionCommitteePreference
        fields = [
            'id',
            'alumni_affairs',
            'awards',
            'chapter_operations',
            'collegiate_chapters',
            'communications',
            'constitution',
            'engineering_futures',
            'membership',
            'public_relations',
            'resolutions',
            'rituals',
        ]


class ConventionGuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConventionGuest
        fields = [
            'id',
            'guest_first_name',
            'guest_last_name',
            'guest_email',
            'guest_phone',
            'guest_dietary_restrictions',
            'guest_special_requests',
        ]


class ConventionTravelSerializer(serializers.ModelSerializer):
    travel_method_display = serializers.CharField(source='get_travel_method_display', read_only=True)
    has_booked_flight = serializers.SerializerMethodField()
    
    class Meta:
        model = ConventionTravel
        fields = [
            'id',
            'travel_method',
            'travel_method_display',
            'departure_airport',
            'departure_date',
            'departure_time_preference',
            'return_airport',
            'return_date',
            'return_time_preference',
            'outbound_airline',
            'outbound_flight_number',
            'outbound_departure_time',
            'outbound_arrival_time',
            'outbound_confirmation',
            'return_airline',
            'return_flight_number',
            'return_departure_time',
            'return_arrival_time',
            'return_confirmation',
            'flight_notes',
            'has_booked_flight',
        ]
        read_only_fields = [
            'outbound_airline', 
            'outbound_flight_number', 
            'outbound_departure_time',
            'outbound_arrival_time',
            'outbound_confirmation',
            'return_airline',
            'return_flight_number',
            'return_departure_time',
            'return_arrival_time',
            'return_confirmation'
        ]
    
    def get_has_booked_flight(self, obj):
        """Check if flight has been booked by staff"""
        return bool(obj.outbound_flight_number and obj.return_flight_number)


class ConventionAccommodationSerializer(serializers.ModelSerializer):
    package_choice_display = serializers.CharField(source='get_package_choice_display', read_only=True)
    roommate_preference_display = serializers.CharField(source='get_roommate_preference_display', read_only=True)
    has_room_assignment = serializers.SerializerMethodField()
    
    class Meta:
        model = ConventionAccommodation
        fields = [
            'id',
            'package_choice',
            'package_choice_display',
            'needs_hotel',
            'check_in_date',
            'check_out_date',
            'roommate_preference',
            'roommate_preference_display',
            'specific_roommate_name',
            'specific_roommate_chapter',
            'food_allergies',
            'dietary_restrictions',
            'other_allergies',
            'room_number',
            'room_confirmation',
            'special_requests',
            'has_room_assignment',
        ]
        read_only_fields = ['room_number', 'room_confirmation']
    
    def get_has_room_assignment(self, obj):
        """Check if room has been assigned"""
        return bool(obj.room_number)


class ConventionRegistrationDetailSerializer(serializers.ModelSerializer):
    """
    Comprehensive serializer for convention registration with all nested data.
    """
    convention_info = ConventionSerializer(source='convention', read_only=True)
    
    # Member personal info (from Member model, not duplicated)
    member_info = MemberPersonalInfoSerializer(source='member', read_only=True)
    
    # All member's addresses and phones (for editing)
    member_addresses = serializers.SerializerMethodField()
    member_phones = serializers.SerializerMethodField()
    
    # Nested convention-specific objects
    committee_preferences = ConventionCommitteePreferenceSerializer(read_only=True)
    guest_details = ConventionGuestSerializer(many=True, read_only=True)
    travel = ConventionTravelSerializer(read_only=True)
    accommodation = ConventionAccommodationSerializer(read_only=True)
    
    class Meta:
        model = ConventionRegistration
        fields = [
            'id',
            'convention',
            'convention_info',
            'member',
            'member_info',
            'member_addresses',
            'member_phones',
            'status_code',
            'registration_date',
            'committee_preferences',
            'guest_details',
            'travel',
            'accommodation',
        ]
    
    def get_member_addresses(self, obj):
        """Get all addresses for the member"""
        addresses = Address.objects.filter(member=obj.member)
        return AddressSerializer(addresses, many=True).data
    
    def get_member_phones(self, obj):
        """Get all phone numbers for the member"""
        phones = PhoneNumbers.objects.filter(member=obj.member)
        return PhoneNumberSerializer(phones, many=True).data


class ConventionRegistrationCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new convention registration.
    """
    class Meta:
        model = ConventionRegistration
        fields = ['convention']
    
    def create(self, validated_data):
        """
        Create registration and initialize related objects.
        """
        registration = super().create(validated_data)
        
        # Create empty related objects
        ConventionCommitteePreference.objects.create(registration=registration)
        ConventionTravel.objects.create(registration=registration)
        ConventionAccommodation.objects.create(registration=registration)
        
        return registration
