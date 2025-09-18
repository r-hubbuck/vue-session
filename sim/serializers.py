from rest_framework import serializers
from .models import Code, CustomUser, Address
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re

class CreateUserSerializer(serializers.ModelSerializer):
    # Validate the password fields to meet complexity requirements
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
    password1 = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = CustomUser
        fields = ('email', 'password1', 'password2', 'phone')

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError('An account with this email already exists.')
        return value

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError({'password2': 'Passwords do not match.'})
        return data

    def create(self, validated_data):
        email = validated_data['email']
        password = validated_data['password1']
        phone = validated_data.get('phone')
        user = CustomUser(
            email=email,
            phone=phone,
            is_active=False
        )
        user.set_password(password)
        user.save()
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
    # Member field is completely excluded - won't appear in requests OR responses
    
    # Add choices for add_type field
    ADD_TYPE_CHOICES = [
        ('Home', 'Home'),
        ('Work', 'Work'),
        ('School', 'School'),
    ]
    add_type = serializers.ChoiceField(choices=ADD_TYPE_CHOICES)
    
    class Meta:
        model = Address
        fields = ['id', 'add_line1', 'add_line2', 'add_city', 'add_state', 'add_zip', 'add_type']
        
    def validate_add_zip(self, value):
        """Validate zip code format"""
        if not value.replace('-', '').isdigit():
            raise serializers.ValidationError("Zip code must contain only numbers and hyphens.")
        return value
    
    def validate(self, data):
        """
        Validate that the member doesn't already have an address of this type
        """
        # Get the member from the view context (set during create/update)
        member = None
        if self.context and 'request' in self.context:
            request = self.context['request']
            if hasattr(request.user, 'member'):
                member = request.user.member
        
        if member and 'add_type' in data:
            add_type = data['add_type']
            
            # Check if this is an update (instance exists) or create (no instance)
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
                    'add_type': f'You already have a {add_type} address. Each member can only have one address of each type.'
                })
        
        return data
