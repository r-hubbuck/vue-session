from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError
from phonenumber_field.formfields import SplitPhoneNumberField
from .models import Code, CustomUser
    
# class CreateUserForm(UserCreationForm):
#     def __init__(self, *args, **kwargs):
#         super(CreateUserForm, self).__init__(*args, **kwargs)
    
#     class Meta:
#         model = CustomUser
#         fields = ('email', 'password1', 'password2', 'phone')

#     def clean_email(self):
#         email = self.cleaned_data.get('email')
#         if CustomUser.objects.filter(email=email).exists():
#             raise ValidationError('An account with this email already exists.')
#         return email
    