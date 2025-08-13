from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError
from phonenumber_field.formfields import SplitPhoneNumberField
from .models import Code, CustomUser

# class CreateUserForm(forms.ModelForm):
#     class Meta:
#         model = User
#         fields = ['email', 'password']

#     def save(self, commit=True) -> User:
#         user = super().save(commit=False)
#         user.username = self.cleaned_data["email"]
#         user.set_password(self.cleaned_data["password"])
#         if commit:
#             user.save()
#         return user
    
class CreateUserForm(UserCreationForm):
    # email = forms.EmailField(required=True,widget=forms.EmailInput(attrs={'class':'form-control'}))
    # phone = SplitPhoneNumberField()

    def __init__(self, *args, **kwargs):
        super(CreateUserForm, self).__init__(*args, **kwargs)
    
    class Meta:
        model = CustomUser
        fields = ('email', 'password1', 'password2', 'phone')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError('An account with this email already exists.')
        return email
    
class CodeForm(forms.ModelForm):
    # number = forms.CharField(label='Code', help_text='Enter SMS verification code.')

    class Meta:
        model = Code
        fields = ('number',)

    def __init__(self, *args, **kwargs):
        super(CodeForm, self).__init__(*args, **kwargs)
        # self.fields['number'].widget.attrs['class'] = 'form-control'
    
class VerifyForm(forms.Form):
    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={'class':'form-control'}))
    grad_year = forms.CharField(required=True, max_length=4, widget=forms.TextInput(attrs={'class':'form-control'}))
    chapter = forms.ChoiceField(choices=(), required=True, widget=forms.Select(attrs={'class':'form-control'}))
    
    def __init__(self, chap_choices, *args, **kwargs):
        super(VerifyForm, self).__init__(*args, **kwargs)
        self.fields['chapter'].choices = chap_choices