from rest_framework import serializers
from .models import Code, CustomUser, Address, PhoneNumbers, StateProvince, UsedToken
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re

class CreateUserSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = CustomUser
        fields = ('email', 'password1', 'password2')

    # Keep your existing password validation methods
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
    
    def validate_password2(self, value):
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

    def validate_email(self, value):
        """
        Modified to allow re-registration for inactive users.
        Stores reference to existing inactive user if found.
        """
        # Check if user with this email already exists
        existing_user = CustomUser.objects.filter(email=value).first()
        
        if existing_user:
            # If user exists but is NOT active, allow re-registration
            if not existing_user.is_active:
                # Store the existing user so we can update it in create()
                self.existing_inactive_user = existing_user
                return value
            else:
                # User exists and IS active - block registration
                raise serializers.ValidationError(
                    'An account with this email already exists and is active. Please login instead.'
                )
        
        # Email doesn't exist - normal registration flow
        return value

    def validate(self, data):
        """Check that passwords match"""
        if data['password1'] != data['password2']:
            raise serializers.ValidationError({'password2': 'Passwords do not match.'})
        return data

    def create(self, validated_data):
        """
        Create new user OR update existing inactive user.
        Also clears old activation tokens for existing users.
        """
        email = validated_data['email']
        password = validated_data['password1']
        
        # Check if we have an existing inactive user (set in validate_email)
        if hasattr(self, 'existing_inactive_user'):
            # UPDATE EXISTING USER instead of creating new one
            user = self.existing_inactive_user
            
            # Update password
            user.set_password(password)
            
            # Keep inactive until email is verified
            user.is_active = False
            
            # Save updated user
            user.save()
            
            # Delete any old activation tokens for this user
            # This ensures old activation links won't work
            UsedToken.objects.filter(
                user=user,
                token_type='activation'
            ).delete()
            
            # Note: The signal will NOT create a new Code because created=False
            # So we need to update the Code manually
            if hasattr(user, 'code'):
                # Update existing code with new random number
                user.code.save()  # This triggers Code.save() which generates new number
            else:
                # Create code if somehow it doesn't exist
                Code.objects.create(user=user)
            
            return user
        else:
            # CREATE NEW USER (normal flow)
            user = CustomUser(
                email=email,
                is_active=False
            )
            user.set_password(password)
            user.save()
            
            # Signal automatically creates Code for new users
            return user

class CodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Code
        fields = ('number',)
        
class CodeValidationSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=5, min_length=5, required=True)

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, min_length=8, write_only=True)

class VerifyMemberSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    chapter = serializers.CharField(required=True)
    year = serializers.CharField(max_length=4, min_length=4, required=True)

    def validate_email(self, value):
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError("Please enter a valid email address.")
        return value

    def validate_year(self, value):
        if not value.isdigit() or len(value) != 4:
            raise serializers.ValidationError("Year must be a 4-digit number.")
        return value

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'add_line1', 'add_line2', 'add_city', 'add_state', 'add_zip', 'add_country', 'add_type']
        
    def validate(self, data):
        """
        Validate based on country:
        - US addresses require state
        - Non-US addresses don't require state
        - Zip/Postal code is optional for all addresses
        - Check for duplicate address types
        """
        # Get the member from the view context
        member = None
        if self.context and 'request' in self.context:
            request = self.context['request']
            if hasattr(request.user, 'member'):
                member = request.user.member
        
        # Validate state requirement based on country
        country = data.get('add_country', 'United States')
        state = data.get('add_state')
        
        if country == 'United States' and not state:
            raise serializers.ValidationError({
                'add_state': 'State is required for United States addresses.'
            })
        
        # Validate unique address type per member
        if member and 'add_type' in data:
            add_type = data['add_type']
            
            if self.instance:
                # For updates: check if another address of this type exists (excluding current one)
                existing = Address.objects.filter(
                    member=member, 
                    add_type=add_type
                ).exclude(id=self.instance.id)
            else:
                # For creates: check if any address of this type exists
                existing = Address.objects.filter(member=member, add_type=add_type)
            
            if existing.exists():
                raise serializers.ValidationError({
                    'add_type': f'You already have a {add_type.lower()} address. You can only have one address of each type.'
                })
        
        return data

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError("Please enter a valid email address.")
        
        # Check if user exists and is active
        if not CustomUser.objects.filter(email=value, is_active=True).exists():
            raise serializers.ValidationError("No active account found with this email address.")
        
        return value

class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password1 = serializers.CharField(write_only=True, min_length=8)
    new_password2 = serializers.CharField(write_only=True, min_length=8)

    def validate_new_password1(self, value):
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

    def validate_new_password2(self, value):
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
        if data['new_password1'] != data['new_password2']:
            raise serializers.ValidationError({'new_password2': 'Passwords do not match.'})
        return data


class PhoneNumberSerializer(serializers.ModelSerializer):
    formatted_number = serializers.SerializerMethodField()
    
    class Meta:
        model = PhoneNumbers
        fields = ['id', 'country_code', 'phone_number', 'formatted_number', 'phone_type', 'is_primary']
    
    def get_formatted_number(self, obj):
        """Return formatted phone number for display"""
        return obj.get_formatted_number()
    
    def validate_phone_number(self, value):
        """Strip all formatting and validate digits only"""
        # Remove all non-digit characters
        clean_number = re.sub(r'\D', '', value)
        
        if not clean_number:
            raise serializers.ValidationError("Phone number must contain digits.")
        
        return clean_number
    
    def validate(self, data):
        """
        Validate that the member doesn't already have a phone of this type
        and that only one phone can be primary
        """
        member = None
        if self.context and 'request' in self.context:
            request = self.context['request']
            if hasattr(request.user, 'member'):
                member = request.user.member
        
        if member and 'phone_type' in data:
            phone_type = data['phone_type']
            
            if self.instance:
                existing_type = PhoneNumbers.objects.filter(
                    member=member, 
                    phone_type=phone_type
                ).exclude(id=self.instance.id)
            else:
                existing_type = PhoneNumbers.objects.filter(member=member, phone_type=phone_type)
            
            if existing_type.exists():
                raise serializers.ValidationError({
                    'phone_type': f'You already have a {phone_type.lower()} phone number. You can only have one phone number of each type.'
                })
        
        if member and data.get('is_primary', False):
            if self.instance:
                existing_primary = PhoneNumbers.objects.filter(
                    member=member,
                    is_primary=True
                ).exclude(id=self.instance.id)
            else:
                existing_primary = PhoneNumbers.objects.filter(member=member, is_primary=True)
            
            if existing_primary.exists():
                raise serializers.ValidationError({
                    'is_primary': 'You can only have one primary phone number. Please uncheck the primary option on your other phone number first.'
                })
        
        return data

class UserAccountSerializer(serializers.ModelSerializer):
    phone_numbers = PhoneNumberSerializer(many=True, read_only=True, source='member.phone_numbers')
    
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'alt_email', 'phone_numbers']
        read_only_fields = ['id', 'email']  # Email should not be editable
    
    def validate_alt_email(self, value):
        if value and CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError('This email is already in use as a primary email.')
        return value

class StateProvinceSerializer(serializers.ModelSerializer):
    country_name = serializers.ReadOnlyField()
    
    class Meta:
        model = StateProvince
        fields = ['st_id', 'st_name', 'st_abbrev', 'st_region', 'country_name', 'st_ctrid']
        
    def to_representation(self, instance):
        """Custom representation for grouped display"""
        return {
            'id': instance.st_id,
            'name': instance.st_name,
            'abbrev': instance.st_abbrev,
            'country': instance.country_name,
            'country_id': instance.st_ctrid
        }