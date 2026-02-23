from decimal import Decimal

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from convention.models import Convention


class BoothPackage(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(
        max_digits=8, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01')), MaxValueValidator(Decimal('99999.99'))]
    )
    is_in_person = models.BooleanField(default=False)
    includes_resume_access = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    convention = models.ForeignKey(
        Convention,
        on_delete=models.CASCADE,
        related_name='booth_packages'
    )
    sort_order = models.IntegerField(default=0)

    class Meta:
        db_table = 'booth_package'
        ordering = ['sort_order', 'price']

    def __str__(self):
        return f"{self.name} (${self.price})"


class MealOption(models.Model):
    name = models.CharField(max_length=200)
    convention = models.ForeignKey(
        Convention,
        on_delete=models.CASCADE,
        related_name='meal_options'
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'meal_option'
        ordering = ['name']

    def __str__(self):
        return self.name


class Organization(models.Model):
    ORG_TYPE_CHOICES = [
        ('business', 'Business'),
        ('graduate_school', 'Graduate School'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=255)
    org_type = models.CharField(max_length=20, choices=ORG_TYPE_CHOICES)
    website = models.URLField(blank=True)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default='United States')
    phone = models.CharField(max_length=20, blank=True)
    billing_email = models.EmailField()
    billing_contact_first_name = models.CharField(max_length=100)
    billing_contact_last_name = models.CharField(max_length=100)
    num_recruiters = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'organization'

    def __str__(self):
        return self.name


class RecruiterProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recruiter_profile'
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='recruiters'
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    cell_phone = models.CharField(max_length=20, blank=True)
    is_approved = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'recruiter_profile'

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.organization.name})"


class RecruiterRegistration(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    recruiter = models.ForeignKey(
        RecruiterProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='registrations'
    )
    convention = models.ForeignKey(
        Convention,
        on_delete=models.CASCADE,
        related_name='recruiter_registrations'
    )
    booth_package = models.ForeignKey(
        BoothPackage,
        on_delete=models.PROTECT,
        related_name='registrations'
    )
    booth_id = models.CharField(max_length=50, blank=True)
    meal_option = models.ForeignKey(
        MealOption,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='registrations'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    special_requests = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'recruiter_registration'
        constraints = [
            models.UniqueConstraint(
                fields=['recruiter', 'convention'],
                name='unique_recruiter_convention'
            )
        ]

    def __str__(self):
        return f"{self.recruiter} - {self.convention}"


class Invoice(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ]

    organization = models.ForeignKey(
        Organization,
        on_delete=models.PROTECT,
        related_name='invoices'
    )
    convention = models.ForeignKey(
        Convention,
        on_delete=models.CASCADE,
        related_name='invoices'
    )
    invoice_number = models.CharField(max_length=50, unique=True)
    amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01')), MaxValueValidator(Decimal('999999.99'))]
    )
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    issued_date = models.DateField()
    due_date = models.DateField()
    paid_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_invoices'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'invoice'
        ordering = ['-issued_date']

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.organization.name}"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            # Auto-generate invoice number: INV-{convention_year}-{sequence}
            last_invoice = Invoice.objects.filter(
                convention=self.convention
            ).order_by('-id').first()
            seq = (last_invoice.id + 1) if last_invoice else 1
            self.invoice_number = f"INV-{self.convention.year}-{seq:04d}"
        super().save(*args, **kwargs)
