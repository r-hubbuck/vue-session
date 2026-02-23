from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from phonenumber_field.modelfields import PhoneNumberField
import secrets

# Role name constants
ROLE_MEMBER = 'member'
ROLE_ALUMNI = 'alumni'
ROLE_COLLEGIATE_OFFICER = 'collegiate_officer'
ROLE_ALUMNI_OFFICER = 'alumni_officer'
ROLE_DISTRICT_DIRECTOR = 'district_director'
ROLE_ENGINEERING_FUTURES_FACILITATOR = 'engineering_futures_facilitator'
ROLE_EXECUTIVE_COUNCIL = 'executive_council'
ROLE_TRUST_ADVISORY_COMMITTEE = 'trust_advisory_committee'
ROLE_CHAPTER_DEVELOPMENT_COMMITTEE = 'chapter_development_committee'
ROLE_FELLOWSHIP_BOARD = 'fellowship_board'
ROLE_EDITORIAL_BOARD = 'editorial_board'
ROLE_DIRECTOR_ALUMNI_AFFAIRS = 'director_alumni_affairs'
ROLE_DIRECTOR_DISTRICT_PROGRAM = 'director_district_program'
ROLE_DIRECTOR_ENGINEERING_FUTURES = 'director_engineering_futures'
ROLE_DIRECTOR_FELLOWSHIPS = 'director_fellowships'
ROLE_DIRECTOR_RITUALS = 'director_rituals'
ROLE_NEST_PROGRAM_LEAD = 'nest_program_lead'
ROLE_HQ_STAFF = 'hq_staff'
ROLE_HQ_IT = 'hq_it'
ROLE_HQ_FINANCE = 'hq_finance'
ROLE_HQ_CHAPTER_SERVICES = 'hq_chapter_services'
ROLE_HQ_ADMIN = 'hq_admin'
ROLE_RECRUITER = 'recruiter'

ALL_ROLES = [
    ROLE_MEMBER,
    ROLE_ALUMNI,
    ROLE_COLLEGIATE_OFFICER,
    ROLE_ALUMNI_OFFICER,
    ROLE_DISTRICT_DIRECTOR,
    ROLE_ENGINEERING_FUTURES_FACILITATOR,
    ROLE_EXECUTIVE_COUNCIL,
    ROLE_TRUST_ADVISORY_COMMITTEE,
    ROLE_CHAPTER_DEVELOPMENT_COMMITTEE,
    ROLE_FELLOWSHIP_BOARD,
    ROLE_EDITORIAL_BOARD,
    ROLE_DIRECTOR_ALUMNI_AFFAIRS,
    ROLE_DIRECTOR_DISTRICT_PROGRAM,
    ROLE_DIRECTOR_ENGINEERING_FUTURES,
    ROLE_DIRECTOR_FELLOWSHIPS,
    ROLE_DIRECTOR_RITUALS,
    ROLE_NEST_PROGRAM_LEAD,
    ROLE_HQ_STAFF,
    ROLE_HQ_IT,
    ROLE_HQ_FINANCE,
    ROLE_HQ_CHAPTER_SERVICES,
    ROLE_HQ_ADMIN,
    ROLE_RECRUITER,
]

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('member', 'Member'),
        ('recruiter', 'Recruiter'),
    ]

    first_name = None
    last_name = None
    username = None
    email = models.EmailField(max_length=254, unique=True)
    alt_email = models.EmailField(max_length=254, blank=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='member')
    member = models.OneToOneField('Member', on_delete=models.CASCADE, null=True, blank=True, related_name='user')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        db_table = 'user'
    
    def has_role(self, role_name):
        """Check if user has a specific role"""
        return self.groups.filter(name=role_name).exists()
    
    def add_role(self, role_name):
        """Add a role to user"""
        from django.contrib.auth.models import Group
        group, _ = Group.objects.get_or_create(name=role_name)
        self.groups.add(group)
    
    def remove_role(self, role_name):
        """Remove a role from user"""
        self.groups.filter(name=role_name).delete()
    
    def get_roles(self):
        """Get list of role names for this user"""
        return list(self.groups.values_list('name', flat=True))

class Member(models.Model):
    member_id = models.IntegerField(unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    preferred_first_name = models.CharField(max_length=100, blank=True)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    chapter = models.CharField(max_length=100)
    district = models.IntegerField(null=True, blank=True)  # For district directors
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    resume_uploaded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'member'

    def get_badge_name(self):
        first = self.preferred_first_name or self.first_name
        return f"{first} {self.last_name}"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
class Address(models.Model):
    member = models.ForeignKey('Member', on_delete=models.CASCADE, related_name='addresses')
    add_line1 = models.CharField(max_length=255, blank=False)
    add_line2 = models.CharField(max_length=255, blank=True)
    add_city = models.CharField(max_length=100, blank=False)
    add_state = models.CharField(max_length=100, blank=True, null=True)
    add_zip = models.CharField(max_length=20, blank=True)
    add_country = models.CharField(max_length=100, default='United States', blank=False)  
    is_primary = models.BooleanField(default=False)
    
    ADD_TYPE_CHOICES = [
        ('Home', 'Home'),
        ('Work', 'Work'),
        ('School', 'School'),
    ]
    add_type = models.CharField(max_length=10, choices=ADD_TYPE_CHOICES, blank=False)
    
    class Meta:
        db_table = 'address'
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

class PhoneNumber(models.Model):
    member = models.ForeignKey('Member', on_delete=models.CASCADE, related_name='phone_numbers')
    country_code = models.CharField(max_length=5, default='+1', blank=False)
    phone_number = models.CharField(max_length=20, blank=False)
    PHONE_TYPE_CHOICES = [
        ('Mobile', 'Mobile'),
        ('Home', 'Home'),
        ('Work', 'Work'),
    ]
    phone_type = models.CharField(max_length=10, choices=PHONE_TYPE_CHOICES, blank=False)
    is_primary = models.BooleanField(default=False)

    class Meta:
        db_table = 'phone_number'
        constraints = [
            models.UniqueConstraint(
                fields=['member', 'phone_type'],
                name='unique_member_phone_type'
            ),
        ]
    
    def __str__(self):
        return f"{self.country_code} {self.phone_number}"
    
    def get_formatted_number(self):
        """Return formatted phone number based on country code"""
        if self.country_code == '+1' and len(self.phone_number) == 10:
            return f"({self.phone_number[:3]}) {self.phone_number[3:6]}-{self.phone_number[6:]}"
        return self.phone_number

class Code(models.Model):
    number = models.CharField(max_length=5, blank=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=False)

    class Meta:
            db_table = 'two_factor_code'

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
        db_table = 'used_token'
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
    st_conus = models.BooleanField(default=False)
    st_foreign = models.BooleanField(default=False)
    st_ctrid = models.IntegerField(null=True, blank=True)
    
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