from rest_framework import serializers
from .models import (
    BoothPackage, MealOption, Organization, RecruiterProfile,
    RecruiterRegistration, Invoice
)
from accounts.models import User
from accounts.serializers import CreateUserSerializer
import bleach
import re


def clean_text(value):
    """Strip HTML tags and whitespace from text input."""
    if value:
        return bleach.clean(value, tags=[], strip=True).strip()
    return value


def clean_phone(value):
    """Strip non-digit characters from phone numbers."""
    if value:
        return re.sub(r'\D', '', value.strip())
    return value


def validate_phone_digits(digits, field_name='Phone number'):
    """Validate cleaned phone digit string."""
    if not digits:
        return digits
    if len(digits) < 10 or len(digits) > 15:
        raise serializers.ValidationError(f'{field_name} must be between 10 and 15 digits.')
    # Reject obviously invalid numbers (all same digit, all zeros, etc.)
    if len(set(digits)) == 1:
        raise serializers.ValidationError(f'Please enter a valid {field_name.lower()}.')
    # US numbers: area code and exchange cannot start with 0 or 1
    if len(digits) == 10:
        if digits[0] in ('0', '1') or digits[3] in ('0', '1'):
            raise serializers.ValidationError(f'Please enter a valid {field_name.lower()}.')
    return digits


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'org_type', 'website',
            'address_line1', 'address_line2', 'city', 'state',
            'zip_code', 'country', 'phone', 'billing_email',
            'billing_contact_first_name', 'billing_contact_last_name',
            'num_recruiters'
        ]
        read_only_fields = ['id']

    def validate_name(self, value):
        return clean_text(value)

    def validate_address_line1(self, value):
        return clean_text(value)

    def validate_address_line2(self, value):
        return clean_text(value)

    def validate_city(self, value):
        return clean_text(value)

    def validate_state(self, value):
        return clean_text(value)

    def validate_phone(self, value):
        if value:
            return validate_phone_digits(clean_phone(value), 'Phone number')
        return value

    def validate_billing_contact_first_name(self, value):
        return clean_text(value)

    def validate_billing_contact_last_name(self, value):
        return clean_text(value)


class RecruiterProfileSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer(read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)

    class Meta:
        model = RecruiterProfile
        fields = [
            'id', 'first_name', 'last_name', 'email', 'phone',
            'cell_phone', 'is_approved', 'organization', 'organization_name',
            'created_at'
        ]
        read_only_fields = ['is_approved', 'created_at']


class RecruiterRegistrationSerializer(serializers.Serializer):
    """Serializer for recruiter self-registration (user + org + profile)."""
    # Personal info
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    cell_phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    password1 = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)

    # Organization info
    org_name = serializers.CharField(max_length=255)
    org_type = serializers.ChoiceField(choices=Organization.ORG_TYPE_CHOICES)
    org_website = serializers.URLField(required=False, allow_blank=True)
    org_address_line1 = serializers.CharField(max_length=255)
    org_address_line2 = serializers.CharField(max_length=255, required=False, allow_blank=True)
    org_city = serializers.CharField(max_length=100)
    org_state = serializers.CharField(max_length=100, required=False, allow_blank=True)
    org_zip_code = serializers.CharField(max_length=20, required=False, allow_blank=True)
    org_country = serializers.CharField(max_length=100, required=False, default='United States')
    org_phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    org_billing_email = serializers.EmailField()
    org_billing_contact_first_name = serializers.CharField(max_length=100)
    org_billing_contact_last_name = serializers.CharField(max_length=100)
    org_num_recruiters = serializers.IntegerField(min_value=1, default=1)

    def validate_first_name(self, value):
        return clean_text(value)

    def validate_last_name(self, value):
        return clean_text(value)

    def validate_phone(self, value):
        if value:
            return validate_phone_digits(clean_phone(value), 'Phone number')
        return value

    def validate_cell_phone(self, value):
        if value:
            return validate_phone_digits(clean_phone(value), 'Cell phone number')
        return value

    def validate_org_phone(self, value):
        if value:
            return validate_phone_digits(clean_phone(value), 'Organization phone number')
        return value

    def validate_org_name(self, value):
        return clean_text(value)

    def validate_org_address_line1(self, value):
        return clean_text(value)

    def validate_org_address_line2(self, value):
        return clean_text(value)

    def validate_org_city(self, value):
        return clean_text(value)

    def validate_org_state(self, value):
        return clean_text(value)

    def validate_org_billing_contact_first_name(self, value):
        return clean_text(value)

    def validate_org_billing_contact_last_name(self, value):
        return clean_text(value)

    def validate_password1(self, value):
        if len(value) < 8:
            raise serializers.ValidationError('Password must be at least 8 characters long.')
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError('Password must contain at least one uppercase letter.')
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError('Password must contain at least one lowercase letter.')
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError('Password must contain at least one number.')
        if not re.search(r'[!@#$%^&*_=+\-.]', value):
            raise serializers.ValidationError('Password must contain at least one special character (!@#$%^&*_=+-.)')
        if re.search(r'[^A-Za-z0-9!@#$%^&*_=+\-.]', value):
            raise serializers.ValidationError('Password contains invalid characters.')
        return value

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError({'password2': 'Passwords do not match.'})

        # Check if email already exists and is active — use a generic message
        # to avoid confirming whether a specific email is registered in the system
        existing = User.objects.filter(email=data['email'], is_active=True).first()
        if existing:
            raise serializers.ValidationError({
                'email': 'This email address cannot be used for registration.'
            })
        return data


class BoothPackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoothPackage
        fields = [
            'id', 'name', 'description', 'price', 'is_in_person',
            'includes_resume_access', 'sort_order'
        ]


class MealOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealOption
        fields = ['id', 'name']


class RecruiterConventionRegistrationSerializer(serializers.ModelSerializer):
    booth_package_detail = BoothPackageSerializer(source='booth_package', read_only=True)
    meal_option_detail = MealOptionSerializer(source='meal_option', read_only=True)

    class Meta:
        model = RecruiterRegistration
        fields = [
            'id', 'booth_package', 'booth_package_detail',
            'booth_id', 'meal_option', 'meal_option_detail',
            'status', 'special_requests', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'booth_id', 'status', 'created_at', 'updated_at']

    def validate_special_requests(self, value):
        if value:
            value = bleach.clean(value, tags=[], strip=True).strip()
            if len(value) > 500:
                raise serializers.ValidationError('Special requests must be 500 characters or fewer.')
        return value

    def validate(self, data):
        booth_package = data.get('booth_package')
        meal_option = data.get('meal_option')

        if booth_package:
            from convention.models import Convention
            active_convention = Convention.objects.filter(is_active=True).first()
            if active_convention and booth_package.convention_id != active_convention.id:
                raise serializers.ValidationError({
                    'booth_package': 'This booth package is not available for the current convention.'
                })
            if not booth_package.is_active:
                raise serializers.ValidationError({
                    'booth_package': 'This booth package is no longer available.'
                })

        if booth_package and booth_package.is_in_person and not meal_option:
            raise serializers.ValidationError({
                'meal_option': 'Meal selection is required for in-person booth packages.'
            })

        if booth_package and not booth_package.is_in_person and meal_option:
            raise serializers.ValidationError({
                'meal_option': 'Meal selection is not available for virtual booth packages.'
            })

        return data


class AdminRecruiterRegistrationSerializer(serializers.ModelSerializer):
    recruiter = RecruiterProfileSerializer(read_only=True)
    booth_package_detail = BoothPackageSerializer(source='booth_package', read_only=True)
    meal_option_detail = MealOptionSerializer(source='meal_option', read_only=True)

    class Meta:
        model = RecruiterRegistration
        fields = [
            'id', 'recruiter', 'booth_package', 'booth_package_detail',
            'booth_id', 'meal_option', 'meal_option_detail',
            'status', 'special_requests', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'recruiter', 'created_at', 'updated_at']

    def validate_booth_id(self, value):
        if value:
            value = bleach.clean(value, tags=[], strip=True).strip()
            if len(value) > 50:
                raise serializers.ValidationError('Booth ID must be 50 characters or fewer.')
            if not re.match(r'^[A-Za-z0-9\-]+$', value):
                raise serializers.ValidationError(
                    'Booth ID may only contain letters, numbers, and hyphens.'
                )
        return value

    def validate_special_requests(self, value):
        if value:
            return bleach.clean(value, tags=[], strip=True).strip()
        return value

    def validate_status(self, value):
        valid_statuses = ['pending', 'approved', 'confirmed', 'cancelled']
        if value not in valid_statuses:
            raise serializers.ValidationError(f'Invalid status. Must be one of: {", ".join(valid_statuses)}')
        return value


class AttendeeSerializer(serializers.Serializer):
    """Read-only serializer for attendee list visible to recruiters."""
    id = serializers.IntegerField(source='member.id')
    first_name = serializers.SerializerMethodField()
    last_name = serializers.CharField(source='member.last_name')
    chapter = serializers.CharField(source='member.chapter')
    has_resume = serializers.SerializerMethodField()
    resume_url = serializers.SerializerMethodField()

    def get_first_name(self, obj):
        return obj.member.preferred_first_name or obj.member.first_name

    def get_has_resume(self, obj):
        return bool(obj.member.resume)

    def get_resume_url(self, obj):
        # Return the access-controlled API endpoint, never the raw media path
        if self.context.get('includes_resume_access') and obj.member.resume:
            return f'/api/recruiters/convention/attendees/{obj.member.id}/resume/'
        return None


class InvoiceSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    created_by_email = serializers.CharField(source='created_by.email', read_only=True)

    class Meta:
        model = Invoice
        fields = [
            'id', 'organization', 'organization_name', 'convention',
            'invoice_number', 'amount', 'description', 'status',
            'issued_date', 'due_date', 'paid_date', 'notes',
            'created_by', 'created_by_email', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'invoice_number', 'created_by', 'created_at', 'updated_at']

    def validate_amount(self, value):
        from decimal import Decimal
        if value is not None:
            if value <= Decimal('0'):
                raise serializers.ValidationError('Amount must be greater than zero.')
            if value > Decimal('999999.99'):
                raise serializers.ValidationError('Amount cannot exceed $999,999.99.')
        return value

    def validate_description(self, value):
        if value:
            return bleach.clean(value, tags=[], strip=True).strip()
        return value

    def validate_notes(self, value):
        if value:
            return bleach.clean(value, tags=[], strip=True).strip()
        return value

    def validate_status(self, value):
        valid_statuses = ['draft', 'sent', 'paid', 'cancelled']
        if value not in valid_statuses:
            raise serializers.ValidationError(f'Invalid status. Must be one of: {", ".join(valid_statuses)}')

        # Enforce valid state transitions on update
        if self.instance:
            current = self.instance.status
            valid_transitions = {
                'draft': ['sent', 'cancelled'],
                'sent': ['paid', 'cancelled'],
                'paid': [],
                'cancelled': [],
            }
            if value != current and value not in valid_transitions.get(current, []):
                raise serializers.ValidationError(
                    f'Cannot transition invoice from "{current}" to "{value}".'
                )

        return value


class RecruiterInvoiceSerializer(serializers.ModelSerializer):
    """Read-only serializer for recruiters viewing their org's invoices."""
    organization_name = serializers.CharField(source='organization.name', read_only=True)

    class Meta:
        model = Invoice
        fields = [
            'id', 'organization_name', 'invoice_number', 'amount',
            'description', 'status', 'issued_date', 'due_date',
            'paid_date', 'notes'
        ]
