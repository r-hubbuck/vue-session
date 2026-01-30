import bleach
from rest_framework import serializers
from .models import (
    Convention,
    ConventionRegistration,
    ConventionCommitteePreference,
    ConventionGuest,
    ConventionTravel,
    ConventionAccommodation,
    Airport,
)
from accounts.models import Member, Address, PhoneNumber


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
    """
    Serializer for displaying member addresses in convention contexts.
    NOTE: This is for READ-ONLY display in nested serializers.
    For address CRUD operations, use the accounts app's AddressViewSet which
    includes database sync logic.
    """
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
    """
    Serializer for displaying member phone numbers in convention contexts.
    NOTE: This is for READ-ONLY display in nested serializers.
    For phone CRUD operations, use the accounts app's PhoneNumberViewSet.
    """
    formatted_number = serializers.SerializerMethodField()
    
    class Meta:
        model = PhoneNumber
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


class AirportSerializer(serializers.ModelSerializer):
    """Serializer for airports"""
    class Meta:
        model = Airport
        fields = ['code', 'state', 'description']


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

    def validate_guest_dietary_restrictions(self, value):
        """Strip HTML tags from guest dietary restrictions"""
        if value:
            return bleach.clean(value, tags=[], strip=True)
        return value
    
    def validate_guest_special_requests(self, value):
        """Strip HTML tags from guest special requests"""
        if value:
            return bleach.clean(value, tags=[], strip=True)
        return value


class ConventionTravelSerializer(serializers.ModelSerializer):
    travel_method_display = serializers.CharField(source='get_travel_method_display', read_only=True)
    seat_preference_display = serializers.CharField(source='get_seat_preference_display', read_only=True)
    has_booked_flight = serializers.SerializerMethodField()
    departure_time_formatted = serializers.SerializerMethodField()
    return_time_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = ConventionTravel
        fields = [
            'id',
            'travel_method',
            'travel_method_display',
            'departure_airport',
            'departure_date',
            'departure_time_preference',
            'departure_time_formatted',
            'return_airport',
            'return_date',
            'return_time_preference',
            'return_time_formatted',
            'seat_preference',
            'seat_preference_display',
            'needs_ground_transportation',
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
    
    def validate(self, data):
        """
        Validate that flight details are provided only when travel_method is 'need_booking'.
        For 'driving' or 'self_booking', flight details are not required.
        """
        travel_method = data.get('travel_method', getattr(self.instance, 'travel_method', None))
        
        # If travel method is need_booking, require flight details
        if travel_method == 'need_booking':
            required_fields = {
                'departure_airport': 'Departure airport',
                'departure_date': 'Departure date',
                'return_airport': 'Return airport',
                'return_date': 'Return date',
            }
            
            errors = {}
            for field, label in required_fields.items():
                if not data.get(field):
                    errors[field] = f'{label} is required when convention booking is needed.'
            
            if errors:
                raise serializers.ValidationError(errors)
            
            # Validate date logic
            if data.get('departure_date') and data.get('return_date'):
                if data['return_date'] < data['departure_date']:
                    raise serializers.ValidationError({
                        'return_date': 'Return date must be on or after departure date.'
                    })
        
        return data
    
    def to_representation(self, instance):
        """Override to handle empty strings in integer fields"""
        # Fix empty strings in time preference fields before serialization
        if instance.departure_time_preference == '':
            instance.departure_time_preference = None
        if instance.return_time_preference == '':
            instance.return_time_preference = None
        return super().to_representation(instance)
    
    def to_internal_value(self, data):
        """Convert empty strings to None for integer fields"""
        if 'departure_time_preference' in data and data['departure_time_preference'] == '':
            data['departure_time_preference'] = None
        if 'return_time_preference' in data and data['return_time_preference'] == '':
            data['return_time_preference'] = None
        return super().to_internal_value(data)
    
    def get_has_booked_flight(self, obj):
        """Check if flight has been booked by staff"""
        return bool(obj.outbound_flight_number and obj.return_flight_number)
    
    def get_departure_time_formatted(self, obj):
        """Convert minutes from midnight to formatted time string"""
        if obj.departure_time_preference is None or obj.departure_time_preference == '':
            return None
        minutes = int(obj.departure_time_preference) if isinstance(obj.departure_time_preference, str) else obj.departure_time_preference
        hours = minutes // 60
        mins = minutes % 60
        period = 'AM' if hours < 12 else 'PM'
        display_hour = hours if hours <= 12 else hours - 12
        display_hour = 12 if display_hour == 0 else display_hour
        return f"{display_hour:02d}:{mins:02d} {period}"
    
    def get_return_time_formatted(self, obj):
        """Convert minutes from midnight to formatted time string"""
        if obj.return_time_preference is None or obj.return_time_preference == '':
            return None
        minutes = int(obj.return_time_preference) if isinstance(obj.return_time_preference, str) else obj.return_time_preference
        hours = minutes // 60
        mins = minutes % 60
        period = 'AM' if hours < 12 else 'PM'
        display_hour = hours if hours <= 12 else hours - 12
        display_hour = 12 if display_hour == 0 else display_hour
        return f"{display_hour:02d}:{mins:02d} {period}"
    
    def validate_flight_notes(self, value):
        """Strip HTML tags from flight notes"""
        if value:
            return bleach.clean(value, tags=[], strip=True)
        return value


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
    
    def validate_special_requests(self, value):
        """Strip HTML tags from special requests"""
        if value:
            return bleach.clean(value, tags=[], strip=True)
        return value
    
    def validate_food_allergies(self, value):
        """Strip HTML tags from food allergies"""
        if value:
            return bleach.clean(value, tags=[], strip=True)
        return value
    
    def validate_dietary_restrictions(self, value):
        """Strip HTML tags from dietary restrictions"""
        if value:
            return bleach.clean(value, tags=[], strip=True)
        return value


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
        phones = PhoneNumber.objects.filter(member=obj.member)
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


class AdminConventionTravelListSerializer(serializers.ModelSerializer):
    """
    Serializer for admin travel list view with member information.
    """
    member_id = serializers.IntegerField(source='registration.member.id', read_only=True)
    member_number = serializers.CharField(source='registration.member.member_id', read_only=True)
    first_name = serializers.CharField(source='registration.member.first_name', read_only=True)
    last_name = serializers.CharField(source='registration.member.last_name', read_only=True)
    chapter = serializers.CharField(source='registration.member.chapter', read_only=True)
    registration_id = serializers.IntegerField(source='registration.id', read_only=True)
    
    # Get state for departure and return airports
    departure_state = serializers.SerializerMethodField()
    return_state = serializers.SerializerMethodField()
    
    travel_method_display = serializers.CharField(source='get_travel_method_display', read_only=True)
    seat_preference_display = serializers.CharField(source='get_seat_preference_display', read_only=True)
    departure_time_formatted = serializers.SerializerMethodField()
    return_time_formatted = serializers.SerializerMethodField()
    has_booked_flight = serializers.SerializerMethodField()
    
    class Meta:
        model = ConventionTravel
        fields = [
            'id',
            'registration_id',
            'member_id',
            'member_number',
            'first_name',
            'last_name',
            'chapter',
            'travel_method',
            'travel_method_display',
            'departure_airport',
            'departure_state',
            'departure_date',
            'departure_time_preference',
            'departure_time_formatted',
            'return_airport',
            'return_state',
            'return_date',
            'return_time_preference',
            'return_time_formatted',
            'seat_preference',
            'seat_preference_display',
            'needs_ground_transportation',
            'has_booked_flight',
        ]
    
    def get_departure_state(self, obj):
        """Get state for departure airport"""
        if obj.departure_airport:
            try:
                airport = Airport.objects.get(code=obj.departure_airport)
                return airport.state
            except Airport.DoesNotExist:
                return None
        return None
    
    def get_return_state(self, obj):
        """Get state for return airport"""
        if obj.return_airport:
            try:
                airport = Airport.objects.get(code=obj.return_airport)
                return airport.state
            except Airport.DoesNotExist:
                return None
        return None
    
    def get_has_booked_flight(self, obj):
        """Check if flight has been booked by staff"""
        return bool(obj.outbound_flight_number and obj.return_flight_number)
    
    def get_departure_time_formatted(self, obj):
        """Convert minutes from midnight to formatted time string"""
        if obj.departure_time_preference is None or obj.departure_time_preference == '':
            return None
        minutes = int(obj.departure_time_preference) if isinstance(obj.departure_time_preference, str) else obj.departure_time_preference
        hours = minutes // 60
        mins = minutes % 60
        period = 'AM' if hours < 12 else 'PM'
        display_hour = hours if hours <= 12 else hours - 12
        display_hour = 12 if display_hour == 0 else display_hour
        return f"{display_hour:02d}:{mins:02d} {period}"
    
    def get_return_time_formatted(self, obj):
        """Convert minutes from midnight to formatted time string"""
        if obj.return_time_preference is None or obj.return_time_preference == '':
            return None
        minutes = int(obj.return_time_preference) if isinstance(obj.return_time_preference, str) else obj.return_time_preference
        hours = minutes // 60
        mins = minutes % 60
        period = 'AM' if hours < 12 else 'PM'
        display_hour = hours if hours <= 12 else hours - 12
        display_hour = 12 if display_hour == 0 else display_hour
        return f"{display_hour:02d}:{mins:02d} {period}"


class AdminConventionTravelUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for admin to update booked flight information.
    Includes comprehensive validation to match existing code standards.
    """
    class Meta:
        model = ConventionTravel
        fields = [
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
        ]
    
    def validate(self, data):
        """
        Validate flight booking data - ensures data integrity.
        Similar to ConventionTravelSerializer validation logic.
        """
        errors = {}
        
        # Get current values if updating existing record
        outbound_flight = data.get('outbound_flight_number', '')
        return_flight = data.get('return_flight_number', '')
        outbound_airline = data.get('outbound_airline', '')
        return_airline = data.get('return_airline', '')
        
        if self.instance:
            outbound_flight = outbound_flight or self.instance.outbound_flight_number
            return_flight = return_flight or self.instance.return_flight_number
            outbound_airline = outbound_airline or self.instance.outbound_airline
            return_airline = return_airline or self.instance.return_airline
        
        # If booking flights, require both outbound and return
        if outbound_flight and not return_flight:
            errors['return_flight_number'] = 'Return flight required when outbound flight is provided.'
        elif return_flight and not outbound_flight:
            errors['outbound_flight_number'] = 'Outbound flight required when return flight is provided.'
        
        # If providing outbound flight, require airline
        if outbound_flight and not outbound_airline:
            errors['outbound_airline'] = 'Airline required when flight number is provided.'
        
        # If providing return flight, require airline
        if return_flight and not return_airline:
            errors['return_airline'] = 'Airline required when flight number is provided.'
        
        # Validate outbound times - arrival must be after departure
        outbound_dep = data.get('outbound_departure_time')
        outbound_arr = data.get('outbound_arrival_time')
        
        if self.instance:
            outbound_dep = outbound_dep or self.instance.outbound_departure_time
            outbound_arr = outbound_arr or self.instance.outbound_arrival_time
        
        if outbound_dep and outbound_arr:
            if outbound_arr <= outbound_dep:
                errors['outbound_arrival_time'] = 'Arrival time must be after departure time.'
        
        # Validate return times - arrival must be after departure
        return_dep = data.get('return_departure_time')
        return_arr = data.get('return_arrival_time')
        
        if self.instance:
            return_dep = return_dep or self.instance.return_departure_time
            return_arr = return_arr or self.instance.return_arrival_time
        
        if return_dep and return_arr:
            if return_arr <= return_dep:
                errors['return_arrival_time'] = 'Arrival time must be after departure time.'
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return data
    
    def validate_flight_notes(self, value):
        """
        Strip HTML tags from flight notes to prevent XSS.
        Matches security pattern in ConventionTravelSerializer.
        """
        if value:
            return bleach.clean(value, tags=[], strip=True)
        return value
    
    def validate_outbound_airline(self, value):
        """Validate and sanitize airline name"""
        if value:
            value = value.strip()
            if len(value) > 100:
                raise serializers.ValidationError('Airline name cannot exceed 100 characters.')
            # Remove any potentially malicious content
            value = bleach.clean(value, tags=[], strip=True)
        return value
    
    def validate_return_airline(self, value):
        """Validate and sanitize airline name"""
        if value:
            value = value.strip()
            if len(value) > 100:
                raise serializers.ValidationError('Airline name cannot exceed 100 characters.')
            # Remove any potentially malicious content
            value = bleach.clean(value, tags=[], strip=True)
        return value
    
    def validate_outbound_flight_number(self, value):
        """Validate and normalize flight number"""
        if value:
            value = value.strip().upper()
            if len(value) > 20:
                raise serializers.ValidationError('Flight number cannot exceed 20 characters.')
        return value
    
    def validate_return_flight_number(self, value):
        """Validate and normalize flight number"""
        if value:
            value = value.strip().upper()
            if len(value) > 20:
                raise serializers.ValidationError('Flight number cannot exceed 20 characters.')
        return value
    
    def validate_outbound_confirmation(self, value):
        """Validate and normalize confirmation number"""
        if value:
            value = value.strip().upper()
            if len(value) > 50:
                raise serializers.ValidationError('Confirmation number cannot exceed 50 characters.')
        return value
    
    def validate_return_confirmation(self, value):
        """Validate and normalize confirmation number"""
        if value:
            value = value.strip().upper()
            if len(value) > 50:
                raise serializers.ValidationError('Confirmation number cannot exceed 50 characters.')
        return value


class CheckInListSerializer(serializers.ModelSerializer):
    """
    Serializer for check-in list view showing all registrations
    """
    member_id = serializers.IntegerField(source='member.id', read_only=True)
    member_number = serializers.IntegerField(source='member.member_id', read_only=True)
    first_name = serializers.CharField(source='member.first_name', read_only=True)
    last_name = serializers.CharField(source='member.last_name', read_only=True)
    preferred_first_name = serializers.CharField(source='member.preferred_first_name', read_only=True)
    chapter = serializers.CharField(source='member.chapter', read_only=True)
    primary_address = serializers.SerializerMethodField()
    has_guest = serializers.SerializerMethodField()
    guest_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ConventionRegistration
        fields = [
            'id',
            'member_id',
            'member_number',
            'first_name',
            'last_name',
            'preferred_first_name',
            'chapter',
            'status_code',
            'checked_in_at',
            'at_convention',
            'primary_address',
            'has_guest',
            'guest_count',
            'is_guest',
        ]
    
    def get_primary_address(self, obj):
        """Get primary address for member"""
        try:
            primary_address = obj.member.addresses.filter(is_primary=True).first()
            if primary_address:
                return AddressSerializer(primary_address).data
        except:
            pass
        return None
    
    def get_has_guest(self, obj):
        """Check if member is bringing a guest"""
        return obj.guest_details.exists()
    
    def get_guest_count(self, obj):
        """Count number of guests"""
        return obj.guest_details.count()



# NOTE: AddressUpdateSerializer has been removed.
# Address management is now handled entirely by the accounts app.
# Use accounts.serializers.AddressSerializer for all address operations.

class RegistrationStatusUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating registration status during check-in
    """
    class Meta:
        model = ConventionRegistration
        fields = ['status_code', 'checked_in_at', 'at_convention']
        read_only_fields = ['checked_in_at']
    
    def validate_status_code(self, value):
        """Validate status code is a valid choice"""
        valid_statuses = ['registered', 'confirmed', 'cancelled', 'checked_in', 'waitlisted']
        if value not in valid_statuses:
            raise serializers.ValidationError(f'Invalid status code. Must be one of: {", ".join(valid_statuses)}')
        return value
    
    def update(self, instance, validated_data):
        """Update status and set checked_in_at if checking in"""
        from django.utils import timezone
        
        status_code = validated_data.get('status_code', instance.status_code)
        
        # If checking in, set the checked_in_at timestamp and at_convention flag
        if status_code == 'checked_in' and instance.status_code != 'checked_in':
            validated_data['checked_in_at'] = timezone.now()
            validated_data['at_convention'] = True
        
        # If cancelling, set at_convention to False
        if status_code == 'cancelled':
            validated_data['at_convention'] = False
        
        return super().update(instance, validated_data)