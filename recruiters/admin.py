from django.contrib import admin
from .models import (
    BoothPackage, MealOption, Organization, RecruiterProfile,
    RecruiterRegistration, Invoice
)


@admin.register(BoothPackage)
class BoothPackageAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'is_in_person', 'includes_resume_access', 'convention', 'is_active', 'sort_order']
    list_filter = ['convention', 'is_active', 'is_in_person']
    list_editable = ['sort_order', 'is_active']


@admin.register(MealOption)
class MealOptionAdmin(admin.ModelAdmin):
    list_display = ['name', 'convention', 'is_active']
    list_filter = ['convention', 'is_active']


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'org_type', 'billing_email', 'num_recruiters', 'created_at']
    list_filter = ['org_type']
    search_fields = ['name', 'billing_email']


@admin.register(RecruiterProfile)
class RecruiterProfileAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'organization', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'organization']
    search_fields = ['first_name', 'last_name', 'email']
    list_editable = ['is_approved']


@admin.register(RecruiterRegistration)
class RecruiterRegistrationAdmin(admin.ModelAdmin):
    list_display = ['recruiter', 'convention', 'booth_package', 'booth_id', 'status', 'created_at']
    list_filter = ['convention', 'status']
    list_editable = ['booth_id', 'status']
    search_fields = ['recruiter__first_name', 'recruiter__last_name', 'booth_id']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'organization', 'convention', 'amount', 'status', 'issued_date', 'due_date']
    list_filter = ['status', 'convention']
    search_fields = ['invoice_number', 'organization__name']
    readonly_fields = ['invoice_number', 'created_at', 'updated_at']
