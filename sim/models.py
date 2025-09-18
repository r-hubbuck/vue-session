from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
import secrets

class CustomUser(AbstractUser):
    first_name = None
    last_name = None
    username = None
    phone = PhoneNumberField()
    email = models.EmailField(max_length=100, unique=True)
    member = models.OneToOneField('Member', on_delete=models.CASCADE, null=True, blank=True, related_name='user')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

class Member(models.Model):
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    chapter = models.CharField(max_length=100)
    phone = PhoneNumberField()
    email = models.EmailField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
class Address(models.Model):
    member = models.ForeignKey('Member', on_delete=models.CASCADE, related_name='addresses')
    add_line1 = models.CharField(max_length=255, blank=False)
    add_line2 = models.CharField(max_length=255, blank=True)
    add_city = models.CharField(max_length=100, blank=False)
    add_state = models.CharField(max_length=100, blank=False)
    add_zip = models.CharField(max_length=10, blank=False)
    
    # Type choices: (stored value, displayed value)
    ADD_TYPE_CHOICES = [
        ('Home', 'Home'),
        ('Work', 'Work'),
        ('School', 'School'),
    ]
    add_type = models.CharField(max_length=10, choices=ADD_TYPE_CHOICES, blank=False)
    
    class Meta:
        # Database-level constraint: one address type per member
        constraints = [
            models.UniqueConstraint(
                fields=['member', 'add_type'],
                name='unique_member_address_type'
            )
        ]
    
    def __str__(self):
        return f"{self.add_line1} {self.add_line2}, {self.add_city}, {self.add_state}, {self.add_zip}"

class Code(models.Model):
    number = models.CharField(max_length=5, blank=False)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, blank=False)

    def __str__(self):
        return str(self.number)
    
    def save(self, *args, **kwargs):
        self.number = ''.join(str(secrets.randbelow(10)) for _ in range(5))
        super().save(*args, **kwargs)

