from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
import secrets

class CustomUser(AbstractUser):
    phone = PhoneNumberField()
    email = models.EmailField(max_length=100)

class Code(models.Model):
    number = models.CharField(max_length=5, blank=False)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, blank=False)

    def __str__(self):
        return str(self.number)
    
    def save(self, *args, **kwargs):
        self.number = ''.join(str(secrets.randbelow(10)) for _ in range(5))
        super().save(*args, **kwargs)

