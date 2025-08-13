from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Code

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Code)