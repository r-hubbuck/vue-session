from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
import secrets

class User(AbstractUser):
    first_name = None
    last_name = None
    username = None
    # phone = PhoneNumberField()
    email = models.EmailField(max_length=100, unique=True)
    alt_email = models.EmailField(max_length=100, blank=True)
    member = models.OneToOneField('Member', on_delete=models.CASCADE, null=True, blank=True, related_name='user')

    ROLE_CHOICES = [
    ('non-member', 'Non-Member'),
    ('collegiate', 'Collegiate'),
    ('alumni', 'Alumni'),
    ('official', 'Official'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='non-member', blank=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

class Member(models.Model):
    member_id = models.IntegerField(unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    chapter = models.CharField(max_length=100)
    # phone = PhoneNumberField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
class Address(models.Model):
    member = models.ForeignKey('Member', on_delete=models.CASCADE, related_name='addresses')
    add_line1 = models.CharField(max_length=255, blank=False)
    add_line2 = models.CharField(max_length=255, blank=True)
    add_city = models.CharField(max_length=100, blank=False)
    add_state = models.CharField(max_length=100, blank=True, null=True)  # Optional for non-US addresses
    add_zip = models.CharField(max_length=20, blank=True)  # Optional for all addresses
    add_country = models.CharField(max_length=100, default='United States', blank=False)  
    
    ADD_TYPE_CHOICES = [
        ('Home', 'Home'),
        ('Work', 'Work'),
        ('School', 'School'),
    ]
    add_type = models.CharField(max_length=10, choices=ADD_TYPE_CHOICES, blank=False)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['member', 'add_type'],
                name='unique_member_address_type'
            )
        ]
    
    def __str__(self):
        parts = [self.add_line1]
        if self.add_line2:
            parts.append(self.add_line2)
        parts.append(self.add_city)
        if self.add_state:
            parts.append(self.add_state)
        parts.append(self.add_zip)
        parts.append(self.add_country)
        return ', '.join(parts)

class PhoneNumbers(models.Model):
    member = models.ForeignKey('Member', on_delete=models.CASCADE, related_name='phone_numbers')
    country_code = models.CharField(max_length=5, default='+1', blank=False)
    phone_number = models.CharField(max_length=20, blank=False)  # Store without formatting
    PHONE_TYPE_CHOICES = [
        ('Mobile', 'Mobile'),
        ('Home', 'Home'),
        ('Work', 'Work'),
    ]
    phone_type = models.CharField(max_length=10, choices=PHONE_TYPE_CHOICES, blank=False)
    is_primary = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['member', 'phone_type'],
                name='unique_member_phone_type'
            ),
            # models.UniqueConstraint(
            #     fields=['member'],
            #     condition=models.Q(is_primary=True),
            #     name='unique_member_primary_phone'
            # )
        ]
    
    def __str__(self):
        return f"{self.country_code} {self.phone_number}"
    
    def get_formatted_number(self):
        """Return formatted phone number based on country code"""
        if self.country_code == '+1' and len(self.phone_number) == 10:
            # US/Canada format: (XXX) XXX-XXXX
            return f"({self.phone_number[:3]}) {self.phone_number[3:6]}-{self.phone_number[6:]}"
        return self.phone_number
    

class Code(models.Model):
    number = models.CharField(max_length=5, blank=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=False)

    def __str__(self):
        return str(self.number)
    
    def save(self, *args, **kwargs):
        self.number = ''.join(str(secrets.randbelow(10)) for _ in range(5))
        super().save(*args, **kwargs)

class UsedToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token_hash = models.CharField(max_length=64, unique=True)
    token_type = models.CharField(max_length=20, choices=[
        ('activation', 'Account Activation'),
        ('password_reset', 'Password Reset')
    ])
    used_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'token_hash', 'token_type']
    
    def __str__(self):
        return f"{self.user.email} - {self.token_type} - {self.used_at}"

class StateProvince(models.Model):
    st_id = models.IntegerField(primary_key=True)
    st_name = models.CharField(max_length=50)
    st_abbrev = models.CharField(max_length=5)
    st_strtzip = models.CharField(max_length=5, blank=True)
    st_endzip = models.CharField(max_length=5, blank=True)
    st_region = models.CharField(max_length=50, blank=True)
    st_conus = models.BooleanField(default=False)  # Continental US
    st_foreign = models.BooleanField(default=False)  # Foreign territory
    st_ctrid = models.IntegerField(null=True, blank=True)  # Country ID
    
    class Meta:
        db_table = 'state_province'
        ordering = ['st_name']
    
    def __str__(self):
        return f"{self.st_name} ({self.st_abbrev})"
    
    @property
    def country_name(self):
        """Return the country this state/province belongs to"""
        if self.st_ctrid == 0: 
            return "United States"
        elif self.st_ctrid == 19:  
            return "Canada"
        elif self.st_ctrid == 4:  
            return "Australia"
        else:
            return self.st_region or "Other"