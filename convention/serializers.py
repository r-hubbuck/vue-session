import bleach
from rest_framework import serializers

# Valid choices for structured allergy/dietary selection fields
FOOD_ALLERGY_CHOICES = [
    'milk', 'eggs', 'peanuts', 'tree_nuts', 'fish',
    'shellfish', 'soy', 'wheat', 'sesame',
]
DIETARY_RESTRICTION_CHOICES = [
    'gluten_free', 'vegetarian', 'vegan', 'kosher',
    'halal', 'dairy_free', 'nut_free',
]

from .models import (
    Convention,
    ConventionRegistration,
    ConventionCommitteePreference,
    ConventionGuest,
    ConventionMeal,
    ConventionTravel,
    ConventionAccommodation,
    ConventionFullyPaidChapter,
    Airport,
)
from accounts.models import Person, Address, PhoneNumber


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
            'days_prior_to_start',
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
    Based on Person model; accesses Member sub-type for member-specific fields.
    """
    badge_name = serializers.SerializerMethodField()
    primary_phone = serializers.SerializerMethodField()
    primary_address = serializers.SerializerMethodField()
    resume_url = serializers.SerializerMethodField()
    resume_uploaded_at = serializers.SerializerMethodField()
    resume_curricula = serializers.SerializerMethodField()
    chapter_code = serializers.SerializerMethodField()

    class Meta:
        model = Person
        fields = [
            'id',
            'first_name',
            'last_name',
            'preferred_first_name',
            'badge_name',
            'chapter_code',
            'primary_phone',
            'primary_address',
            'resume_url',
            'resume_uploaded_at',
            'resume_curricula',
        ]
        read_only_fields = [
            'first_name', 'last_name', 'chapter_code', 'badge_name',
            'primary_phone', 'primary_address', 'resume_url', 'resume_uploaded_at',
            'resume_curricula',
        ]

    def _get_active_registration(self, obj):
        from convention.models import Convention
        convention = Convention.objects.filter(is_active=True).first()
        if not convention:
            return None
        return obj.convention_registrations.filter(convention=convention).first()

    def get_resume_url(self, obj):
        reg = self._get_active_registration(obj)
        if reg and reg.resume:
            return '/api/recruiters/member/resume/'
        return None

    def get_resume_uploaded_at(self, obj):
        reg = self._get_active_registration(obj)
        if reg:
            return reg.resume_uploaded_at
        return None

    def get_resume_curricula(self, obj):
        reg = self._get_active_registration(obj)
        if not reg:
            return []
        return [{'id': c.id, 'full_name': c.full_name} for c in reg.resume_curricula.all()]

    def get_chapter_code(self, obj):
        if hasattr(obj, 'member'):
            return obj.member.chapter_code
        return None

    def get_badge_name(self, obj):
        """Compute badge name from preferred_first_name + last_name"""
        if hasattr(obj, 'member'):
            return obj.member.get_badge_name()
        preferred = obj.preferred_first_name or obj.first_name
        return f"{preferred} {obj.last_name}"

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


class ConventionMealSerializer(serializers.ModelSerializer):
    price_display = serializers.SerializerMethodField()

    class Meta:
        model = ConventionMeal
        fields = ['id', 'name', 'price', 'price_display', 'sort_order']

    def get_price_display(self, obj):
        return f"${obj.price:,.2f}"


class ConventionGuestSerializer(serializers.ModelSerializer):
    # Read: nested meal objects; Write: list of meal PKs (source maps both to guest_meals)
    guest_meals = ConventionMealSerializer(many=True, read_only=True)
    guest_meal_ids = serializers.PrimaryKeyRelatedField(
        source='guest_meals',
        queryset=ConventionMeal.objects.filter(is_active=True),
        many=True,
        required=False,
        write_only=True,
    )

    class Meta:
        model = ConventionGuest
        fields = [
            'id',
            'guest_first_name',
            'guest_last_name',
            'guest_email',
            'guest_phone',
            'guest_food_allergies',
            'guest_food_allergies_other',
            'guest_dietary_restrictions',
            'guest_dietary_restrictions_other',
            'guest_special_requests',
            'guest_meals',
            'guest_meal_ids',
        ]

    def validate_guest_first_name(self, value):
        if value:
            return bleach.clean(value, tags=[], strip=True).strip()
        return value

    def validate_guest_last_name(self, value):
        if value:
            return bleach.clean(value, tags=[], strip=True).strip()
        return value

    def validate_guest_phone(self, value):
        if value:
            import re
            digits = re.sub(r'\D', '', value.strip())
            if digits:
                if len(digits) < 10 or len(digits) > 15:
                    raise serializers.ValidationError('Phone number must be between 10 and 15 digits.')
                if len(set(digits)) == 1:
                    raise serializers.ValidationError('Please enter a valid phone number.')
                if len(digits) == 10 and (digits[0] in ('0', '1') or digits[3] in ('0', '1')):
                    raise serializers.ValidationError('Please enter a valid phone number.')
                return digits
        return value

    def validate_guest_email(self, value):
        if value:
            return bleach.clean(value, tags=[], strip=True).strip()
        return value

    def validate_guest_food_allergies(self, value):
        """Validate guest food allergies are from the known choices list."""
        if value is None:
            return []
        if not isinstance(value, list):
            raise serializers.ValidationError('Food allergies must be a list.')
        cleaned = []
        for item in value:
            item = bleach.clean(str(item), tags=[], strip=True).strip().lower()
            if item not in FOOD_ALLERGY_CHOICES:
                raise serializers.ValidationError(
                    f'"{item}" is not a valid food allergy choice.'
                )
            cleaned.append(item)
        return cleaned

    def validate_guest_food_allergies_other(self, value):
        if value:
            return bleach.clean(value, tags=[], strip=True).strip()
        return value

    def validate_guest_dietary_restrictions(self, value):
        """Validate guest dietary restrictions are from the known choices list."""
        if value is None:
            return []
        if not isinstance(value, list):
            raise serializers.ValidationError('Dietary restrictions must be a list.')
        cleaned = []
        for item in value:
            item = bleach.clean(str(item), tags=[], strip=True).strip().lower()
            if item not in DIETARY_RESTRICTION_CHOICES:
                raise serializers.ValidationError(
                    f'"{item}" is not a valid dietary restriction choice.'
                )
            cleaned.append(item)
        return cleaned

    def validate_guest_dietary_restrictions_other(self, value):
        if value:
            return bleach.clean(value, tags=[], strip=True).strip()
        return value

    def validate_guest_special_requests(self, value):
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
            'dietary_restrictions_other',
            'room_number',
            'room_confirmation',
            'special_requests',
            'has_room_assignment',
        ]
        read_only_fields = ['room_number', 'room_confirmation']

    def get_has_room_assignment(self, obj):
        """Check if room has been assigned"""
        return bool(obj.room_number)

    def validate_food_allergies(self, value):
        """Validate that food_allergies is a list of known allergy keys."""
        if value is None:
            return []
        if not isinstance(value, list):
            raise serializers.ValidationError('Food allergies must be a list.')
        cleaned = []
        for item in value:
            item = bleach.clean(str(item), tags=[], strip=True).strip().lower()
            if item not in FOOD_ALLERGY_CHOICES:
                raise serializers.ValidationError(
                    f'"{item}" is not a valid food allergy choice.'
                )
            cleaned.append(item)
        return cleaned

    def validate_dietary_restrictions(self, value):
        """Validate that dietary_restrictions is a list of known restriction keys."""
        if value is None:
            return []
        if not isinstance(value, list):
            raise serializers.ValidationError('Dietary restrictions must be a list.')
        cleaned = []
        for item in value:
            item = bleach.clean(str(item), tags=[], strip=True).strip().lower()
            if item not in DIETARY_RESTRICTION_CHOICES:
                raise serializers.ValidationError(
                    f'"{item}" is not a valid dietary restriction choice.'
                )
            cleaned.append(item)
        return cleaned

    def validate_other_allergies(self, value):
        if value:
            return bleach.clean(value, tags=[], strip=True).strip()
        return value

    def validate_dietary_restrictions_other(self, value):
        if value:
            return bleach.clean(value, tags=[], strip=True).strip()
        return value

    def validate_special_requests(self, value):
        if value:
            return bleach.clean(value, tags=[], strip=True)
        return value

    def validate_specific_roommate_name(self, value):
        if value:
            return bleach.clean(value, tags=[], strip=True).strip()
        return value

    def validate_specific_roommate_chapter(self, value):
        if value:
            return bleach.clean(value, tags=[], strip=True).strip()
        return value


class EmergencyContactSerializer(serializers.ModelSerializer):
    """
    Serializer for updating emergency contact information on a registration.
    """
    class Meta:
        model = ConventionRegistration
        fields = [
            'emergency_contact_name',
            'emergency_contact_relationship',
            'emergency_contact_phone',
        ]

    def validate_emergency_contact_name(self, value):
        if value:
            return bleach.clean(value, tags=[], strip=True).strip()
        return value

    def validate_emergency_contact_relationship(self, value):
        if value:
            return bleach.clean(value, tags=[], strip=True).strip()
        return value

    def validate_emergency_contact_phone(self, value):
        if value:
            import re
            digits = re.sub(r'\D', '', value.strip())
            if digits:
                if len(digits) < 10 or len(digits) > 15:
                    raise serializers.ValidationError(
                        'Phone number must be between 10 and 15 digits.'
                    )
                if len(set(digits)) == 1:
                    raise serializers.ValidationError('Please enter a valid phone number.')
                if len(digits) == 10 and (digits[0] in ('0', '1') or digits[3] in ('0', '1')):
                    raise serializers.ValidationError('Please enter a valid phone number.')
                return digits
        return value


class ConventionRegistrationDetailSerializer(serializers.ModelSerializer):
    """
    Comprehensive serializer for convention registration with all nested data.
    """
    convention_info = ConventionSerializer(source='convention', read_only=True)
    
    # Person personal info (from Person model, not duplicated)
    member_info = MemberPersonalInfoSerializer(source='person', read_only=True)

    # All person's addresses and phones (for editing)
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
            'person',
            'member_info',
            'member_addresses',
            'member_phones',
            'status_code',
            'registration_date',
            'committee_preferences',
            'guest_details',
            'travel',
            'accommodation',
            'visible_to_recruiters',
            'confirmation_email_sent',
            'paid',
            'guest_attending',
            'emergency_contact_name',
            'emergency_contact_relationship',
            'emergency_contact_phone',
        ]
        read_only_fields = ['paid']

    def get_member_addresses(self, obj):
        """Get all addresses for the person"""
        addresses = Address.objects.filter(person=obj.person)
        return AddressSerializer(addresses, many=True).data

    def get_member_phones(self, obj):
        """Get all phone numbers for the person"""
        phones = PhoneNumber.objects.filter(person=obj.person)
        return PhoneNumberSerializer(phones, many=True).data

    def validate_visible_to_recruiters(self, value):
        allowed = [choice[0] for choice in ConventionRegistration.VISIBILITY_CHOICES]
        if value not in allowed:
            raise serializers.ValidationError(
                f"Must be one of: {', '.join(allowed)}."
            )
        return value


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
    member_id = serializers.IntegerField(source='registration.person.id', read_only=True)
    member_number = serializers.CharField(source='registration.person.member.member_id', read_only=True)
    first_name = serializers.CharField(source='registration.person.first_name', read_only=True)
    last_name = serializers.CharField(source='registration.person.last_name', read_only=True)
    chapter_code = serializers.CharField(source='registration.person.member.chapter_code', read_only=True)
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
            'chapter_code',
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
        errors = {}

        required_fields = [
            ('outbound_airline', 'Outbound airline is required.'),
            ('outbound_flight_number', 'Outbound flight number is required.'),
            ('outbound_departure_time', 'Outbound departure time is required.'),
            ('outbound_arrival_time', 'Outbound arrival time is required.'),
            ('outbound_confirmation', 'Outbound confirmation number is required.'),
            ('return_airline', 'Return airline is required.'),
            ('return_flight_number', 'Return flight number is required.'),
            ('return_departure_time', 'Return departure time is required.'),
            ('return_arrival_time', 'Return arrival time is required.'),
            ('return_confirmation', 'Return confirmation number is required.'),
        ]

        for field, message in required_fields:
            value = data.get(field)
            if value is None or (isinstance(value, str) and not value.strip()):
                errors[field] = message

        outbound_dep = data.get('outbound_departure_time')
        outbound_arr = data.get('outbound_arrival_time')
        if outbound_dep and outbound_arr and outbound_arr <= outbound_dep:
            errors['outbound_arrival_time'] = 'Arrival time must be after departure time.'

        return_dep = data.get('return_departure_time')
        return_arr = data.get('return_arrival_time')
        if return_dep and return_arr and return_arr <= return_dep:
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
    member_id = serializers.IntegerField(source='person.id', read_only=True)
    member_number = serializers.IntegerField(source='person.member.member_id', read_only=True)
    first_name = serializers.CharField(source='person.first_name', read_only=True)
    last_name = serializers.CharField(source='person.last_name', read_only=True)
    preferred_first_name = serializers.CharField(source='person.preferred_first_name', read_only=True)
    chapter_code = serializers.CharField(source='person.member.chapter_code', read_only=True)
    primary_address = serializers.SerializerMethodField()
    has_guest = serializers.SerializerMethodField()
    guest_count = serializers.SerializerMethodField()
    all_addresses = serializers.SerializerMethodField()
    cell_phone = serializers.SerializerMethodField()

    class Meta:
        model = ConventionRegistration
        fields = [
            'id',
            'member_id',
            'member_number',
            'first_name',
            'last_name',
            'preferred_first_name',
            'chapter_code',
            'status_code',
            'checked_in_at',
            'at_convention',
            'primary_address',
            'has_guest',
            'guest_count',
            'is_guest',
            'all_addresses',
            'cell_phone',
        ]
    
    def get_primary_address(self, obj):
        """Get primary address for person"""
        try:
            primary_address = obj.person.addresses.filter(is_primary=True).first()
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

    def get_all_addresses(self, obj):
        """Get all addresses for the person"""
        try:
            return AddressSerializer(obj.person.addresses.all(), many=True).data
        except Exception:
            return []

    def get_cell_phone(self, obj):
        """Get the person's Mobile phone number"""
        try:
            phone = obj.person.phone_numbers.filter(phone_type='Mobile').first()
            if phone:
                return PhoneNumberSerializer(phone).data
        except Exception:
            pass
        return None


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
        """Validate status code is a valid choice and enforce state transitions"""
        valid_statuses = ['registered', 'confirmed', 'cancelled', 'checked_in', 'waitlisted']
        if value not in valid_statuses:
            raise serializers.ValidationError(f'Invalid status code. Must be one of: {", ".join(valid_statuses)}')

        # Enforce valid state transitions on update
        if self.instance:
            current = self.instance.status_code
            valid_transitions = {
                'registered': ['confirmed', 'cancelled', 'waitlisted', 'checked_in'],
                'confirmed': ['checked_in', 'cancelled', 'registered'],
                'waitlisted': ['registered', 'confirmed', 'cancelled'],
                'checked_in': ['cancelled', 'confirmed', 'registered'],
                'cancelled': ['registered'],
            }
            if value != current and value not in valid_transitions.get(current, []):
                raise serializers.ValidationError(
                    f'Cannot transition registration from "{current}" to "{value}".'
                )

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


class AdminRegistrationPersonSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()
    member_id = serializers.SerializerMethodField()

    class Meta:
        model = Person
        fields = ['id', 'first_name', 'last_name', 'preferred_first_name', 'email', 'member_id']

    def get_email(self, obj):
        if hasattr(obj, 'user') and obj.user:
            return obj.user.email
        return None

    def get_member_id(self, obj):
        if hasattr(obj, 'member'):
            return obj.member.member_id
        return None


class AdminRegistrationListSerializer(serializers.ModelSerializer):
    person = AdminRegistrationPersonSerializer(read_only=True)
    has_travel = serializers.SerializerMethodField()
    has_accommodation = serializers.SerializerMethodField()
    travel_booked = serializers.SerializerMethodField()

    class Meta:
        model = ConventionRegistration
        fields = [
            'id',
            'status_code',
            'registration_date',
            'is_guest',
            'paid',
            'credentials_received',
            'contact_email',
            'terms_agreed',
            'terms_agreed_at',
            'person',
            'has_travel',
            'has_accommodation',
            'travel_booked',
        ]

    def get_has_travel(self, obj):
        return hasattr(obj, 'travel') and obj.travel is not None

    def get_has_accommodation(self, obj):
        return hasattr(obj, 'accommodation') and obj.accommodation is not None

    def get_travel_booked(self, obj):
        try:
            return bool(obj.travel.outbound_flight_number and obj.travel.return_flight_number)
        except Exception:
            return False


class AdminRegistrationDetailSerializer(serializers.ModelSerializer):
    person = AdminRegistrationPersonSerializer(read_only=True)
    committee_preferences = ConventionCommitteePreferenceSerializer(read_only=True)
    guest_details = ConventionGuestSerializer(many=True, read_only=True)
    travel = ConventionTravelSerializer(read_only=True)
    accommodation = ConventionAccommodationSerializer(read_only=True)

    class Meta:
        model = ConventionRegistration
        fields = [
            'id',
            'status_code',
            'registration_date',
            'is_guest',
            'paid',
            'credentials_received',
            'visible_to_recruiters',
            'guest_attending',
            'contact_email',
            'terms_agreed',
            'terms_agreed_at',
            'emergency_contact_name',
            'emergency_contact_relationship',
            'emergency_contact_phone',
            'confirmation_email_sent',
            'person',
            'committee_preferences',
            'guest_details',
            'travel',
            'accommodation',
        ]


class AdminRegistrationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConventionRegistration
        fields = [
            'status_code',
            'paid',
            'credentials_received',
            'visible_to_recruiters',
            'guest_attending',
            'contact_email',
            'emergency_contact_name',
            'emergency_contact_relationship',
            'emergency_contact_phone',
        ]
        read_only_fields = ['terms_agreed', 'terms_agreed_at']

    def validate_contact_email(self, value):
        if value:
            value = bleach.clean(value, tags=[], strip=True).strip()
            import re
            if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', value):
                raise serializers.ValidationError('Enter a valid email address.')
        return value

    def validate_status_code(self, value):
        value = bleach.clean(value, tags=[], strip=True).strip()
        valid = [c[0] for c in ConventionRegistration.STATUS_CHOICES]
        if value not in valid:
            raise serializers.ValidationError(f'Must be one of: {", ".join(valid)}.')
        return value

    def validate_visible_to_recruiters(self, value):
        value = bleach.clean(value, tags=[], strip=True).strip()
        allowed = [c[0] for c in ConventionRegistration.VISIBILITY_CHOICES]
        if value not in allowed:
            raise serializers.ValidationError(f'Must be one of: {", ".join(allowed)}.')
        return value

    def validate_emergency_contact_name(self, value):
        if value:
            return bleach.clean(value, tags=[], strip=True).strip()
        return value

    def validate_emergency_contact_relationship(self, value):
        if value:
            return bleach.clean(value, tags=[], strip=True).strip()
        return value

    def validate_emergency_contact_phone(self, value):
        if value:
            import re
            digits = re.sub(r'\D', '', value.strip())
            if digits:
                if len(digits) < 10 or len(digits) > 15:
                    raise serializers.ValidationError('Phone number must be between 10 and 15 digits.')
                if len(set(digits)) == 1:
                    raise serializers.ValidationError('Please enter a valid phone number.')
                if len(digits) == 10 and (digits[0] in ('0', '1') or digits[3] in ('0', '1')):
                    raise serializers.ValidationError('Please enter a valid phone number.')
                return digits
        return value


class PersonSearchSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()
    member_id = serializers.SerializerMethodField()
    has_active_registration = serializers.SerializerMethodField()

    class Meta:
        model = Person
        fields = ['id', 'first_name', 'last_name', 'preferred_first_name', 'email', 'member_id', 'has_active_registration']

    def get_email(self, obj):
        if hasattr(obj, 'user') and obj.user:
            return obj.user.email
        return None

    def get_member_id(self, obj):
        if hasattr(obj, 'member'):
            return obj.member.member_id
        return None

    def get_has_active_registration(self, obj):
        convention = self.context.get('convention')
        if not convention:
            return False
        return obj.convention_registrations.filter(convention=convention).exists()


class AdminTravelSerializer(ConventionTravelSerializer):
    """
    Staff version of ConventionTravelSerializer — all fields writable including
    booked flight details that are read-only for members.
    Skips the need_booking validation so staff can save partial data freely.
    """
    class Meta(ConventionTravelSerializer.Meta):
        read_only_fields = []

    def validate(self, data):
        return data

    def validate_outbound_airline(self, value):
        if value:
            return bleach.clean(value, tags=[], strip=True).strip()
        return value

    def validate_outbound_flight_number(self, value):
        if value:
            return bleach.clean(value, tags=[], strip=True).strip()
        return value

    def validate_outbound_confirmation(self, value):
        if value:
            return bleach.clean(value, tags=[], strip=True).strip()
        return value

    def validate_return_airline(self, value):
        if value:
            return bleach.clean(value, tags=[], strip=True).strip()
        return value

    def validate_return_flight_number(self, value):
        if value:
            return bleach.clean(value, tags=[], strip=True).strip()
        return value

    def validate_return_confirmation(self, value):
        if value:
            return bleach.clean(value, tags=[], strip=True).strip()
        return value


class AdminAccommodationSerializer(ConventionAccommodationSerializer):
    """
    Staff version of ConventionAccommodationSerializer — room_number and
    room_confirmation are writable so staff can assign rooms.
    """
    class Meta(ConventionAccommodationSerializer.Meta):
        read_only_fields = []

    def validate_room_number(self, value):
        if value:
            return bleach.clean(value, tags=[], strip=True).strip()
        return value

    def validate_room_confirmation(self, value):
        if value:
            return bleach.clean(value, tags=[], strip=True).strip()
        return value


class FullyPaidChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConventionFullyPaidChapter
        fields = ['id', 'convention', 'chapter_code', 'spots_available', 'spots_used']
        read_only_fields = ['id', 'spots_used']

    def validate_chapter_code(self, value):
        value = bleach.clean(str(value), tags=[], strip=True).strip().upper()
        if not value:
            raise serializers.ValidationError("chapter_code is required.")
        if len(value) > 10:
            raise serializers.ValidationError("chapter_code cannot exceed 10 characters.")
        return value


class FullyPaidChapterUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConventionFullyPaidChapter
        fields = ['spots_available', 'spots_used']

    def validate_spots_available(self, value):
        if value < 0:
            raise serializers.ValidationError("spots_available cannot be negative.")
        return value

    def validate_spots_used(self, value):
        if value < 0:
            raise serializers.ValidationError("spots_used cannot be negative.")
        return value

    def validate(self, data):
        instance = self.instance
        spots_available = data.get('spots_available', instance.spots_available if instance else 0)
        spots_used = data.get('spots_used', instance.spots_used if instance else 0)
        if spots_used > spots_available:
            raise serializers.ValidationError(
                {'spots_used': 'spots_used cannot exceed spots_available.'}
            )
        return data