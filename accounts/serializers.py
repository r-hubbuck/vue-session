import bleach
from rest_framework import serializers
from .models import Code, User, Address, PhoneNumber, StateProvince, UsedToken, Person
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
import re

class CreateUserSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')
        extra_kwargs = {
            'email': {
                'validators': [],  # Remove default unique validator
            }
        }

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
        existing_user = User.objects.filter(email=value).first()

        if existing_user:
            if not existing_user.is_active:
                account_age = timezone.now() - existing_user.date_joined

                if account_age < timedelta(hours=24):
                    raise serializers.ValidationError(
                        'An activation email was recently sent to this address. '
                        'Please check your email or wait 24 hours to re-register.'
                    )

                self.existing_inactive_user = existing_user
                return value
            else:
                raise serializers.ValidationError(
                    'This email address cannot be used for registration.'
                )

        return value

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError({'password2': 'Passwords do not match.'})
        return data

    def create(self, validated_data):
        email = validated_data['email']
        password = validated_data['password1']

        if hasattr(self, 'existing_inactive_user'):
            user = self.existing_inactive_user
            user.set_password(password)
            user.last_login = timezone.now()
            user.is_active = False
            user.save()

            UsedToken.objects.filter(
                user=user,
                token_type='activation'
            ).delete()

            if hasattr(user, 'code'):
                user.code.save()
            else:
                Code.objects.create(user=user)

            return user
        else:
            user = User(
                email=email,
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

    def validate_email(self, value):
        return bleach.clean(value, tags=[], strip=True).strip()


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

    def validate_chapter(self, value):
        if value:
            return bleach.clean(value, tags=[], strip=True).strip()
        return value

    def validate_year(self, value):
        if not value.isdigit() or len(value) != 4:
            raise serializers.ValidationError("Year must be a 4-digit number.")
        return value


class AddressSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = Address
        fields = ['id', 'add_line1', 'add_line2', 'add_city', 'add_state', 'add_zip', 'add_country', 'add_type', 'is_primary', 'display_name']

    def validate_add_line1(self, value):
        if value:
            return bleach.clean(value, tags=[], strip=True).strip()
        return value

    def validate_add_line2(self, value):
        if value:
            return bleach.clean(value, tags=[], strip=True).strip()
        return value

    def validate_add_city(self, value):
        if value:
            return bleach.clean(value, tags=[], strip=True).strip()
        return value

    def validate_add_state(self, value):
        if value:
            return bleach.clean(value, tags=[], strip=True).strip()
        return value

    def validate_add_zip(self, value):
        if value:
            return bleach.clean(value, tags=[], strip=True).strip()
        return value

    def validate_add_country(self, value):
        if value:
            return bleach.clean(value, tags=[], strip=True).strip()
        return value

    def get_display_name(self, obj):
        parts = [obj.add_line1]
        if obj.add_line2:
            parts.append(obj.add_line2)
        parts.append(f"{obj.add_city}, {obj.add_state} {obj.add_zip}" if obj.add_state else obj.add_city)
        if obj.add_country and obj.add_country != 'United States':
            parts.append(obj.add_country)
        return ', '.join(parts)

    def validate(self, data):
        person = None
        if self.context and 'request' in self.context:
            request = self.context['request']
            if hasattr(request.user, 'person') and request.user.person is not None:
                person = request.user.person

        country = data.get('add_country', 'United States')
        state = data.get('add_state')

        if country == 'United States' and not state:
            raise serializers.ValidationError({
                'add_state': 'State is required for United States addresses.'
            })

        if person and 'add_type' in data:
            add_type = data['add_type']

            if self.instance:
                existing = Address.objects.filter(
                    person=person,
                    add_type=add_type
                ).exclude(id=self.instance.id)
            else:
                existing = Address.objects.filter(person=person, add_type=add_type)

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
        model = PhoneNumber
        fields = ['id', 'country_code', 'phone_number', 'formatted_number', 'phone_type', 'is_primary']

    def get_formatted_number(self, obj):
        return obj.get_formatted_number()

    def validate_phone_number(self, value):
        clean_number = re.sub(r'\D', '', value)

        if not clean_number:
            raise serializers.ValidationError("Phone number must contain digits.")

        if len(clean_number) < 10 or len(clean_number) > 15:
            raise serializers.ValidationError("Phone number must be between 10 and 15 digits.")

        if len(set(clean_number)) == 1:
            raise serializers.ValidationError("Please enter a valid phone number.")

        if len(clean_number) == 10:
            if clean_number[0] in ('0', '1') or clean_number[3] in ('0', '1'):
                raise serializers.ValidationError("Please enter a valid phone number.")

        return clean_number

    def validate(self, data):
        person = None
        if self.context and 'request' in self.context:
            request = self.context['request']
            if hasattr(request.user, 'person') and request.user.person is not None:
                person = request.user.person

        if person and 'phone_type' in data:
            phone_type = data['phone_type']

            if self.instance:
                existing_type = PhoneNumber.objects.filter(
                    person=person,
                    phone_type=phone_type
                ).exclude(id=self.instance.id)
            else:
                existing_type = PhoneNumber.objects.filter(person=person, phone_type=phone_type)

            if existing_type.exists():
                raise serializers.ValidationError({
                    'phone_type': f'You already have a {phone_type.lower()} phone number. You can only have one phone number of each type.'
                })

        return data


class UserAccountSerializer(serializers.ModelSerializer):
    phone_numbers = PhoneNumberSerializer(many=True, read_only=True, source='person.phone_numbers')
    first_name = serializers.CharField(source='person.first_name', read_only=True, default='')
    last_name = serializers.CharField(source='person.last_name', read_only=True, default='')

    class Meta:
        model = User
        fields = ['id', 'email', 'alt_email', 'first_name', 'last_name', 'phone_numbers']
        read_only_fields = ['id', 'email', 'first_name', 'last_name']

    def validate_alt_email(self, value):
        if value and User.objects.filter(email=value).exists():
            raise serializers.ValidationError('This email is already in use as a primary email.')
        return value


class UserSerializer(serializers.ModelSerializer):
    member = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()
    recruiter_profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'alt_email', 'roles', 'member', 'recruiter_profile']

    def get_member(self, obj):
        if obj.person and hasattr(obj.person, 'member'):
            m = obj.person.member
            return {
                'member_id': m.member_id,
                'first_name': obj.person.first_name,
                'preferred_first_name': obj.person.preferred_first_name,
                'middle_name': obj.person.middle_name,
                'last_name': obj.person.last_name,
                'chapter': m.chapter,
                'district': m.district,
            }
        return None

    def get_roles(self, obj):
        return list(obj.groups.values_list('name', flat=True))

    def get_recruiter_profile(self, obj):
        if obj.has_role('recruiter') and hasattr(obj, 'recruiter_profile'):
            profile = obj.recruiter_profile
            return {
                'id': profile.id,
                'first_name': profile.first_name,
                'last_name': profile.last_name,
                'organization_name': profile.organization.name,
                'is_approved': profile.is_approved,
            }
        return None


class StateProvinceSerializer(serializers.ModelSerializer):
    country_name = serializers.ReadOnlyField()

    class Meta:
        model = StateProvince
        fields = ['st_id', 'st_name', 'st_abbrev', 'st_region', 'country_name', 'st_ctrid']

    def to_representation(self, instance):
        return {
            'id': instance.st_id,
            'name': instance.st_name,
            'abbrev': instance.st_abbrev,
            'country': instance.country_name,
            'country_id': instance.st_ctrid
        }
