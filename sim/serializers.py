from rest_framework import serializers
from .models import Code, CustomUser
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

class CreateUserSerializer(serializers.ModelSerializer):
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
            username=email,
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

