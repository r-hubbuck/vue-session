from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from accounts.models import Member, User


class ExpenseReportType(models.Model):
    """
    Types of expense reports with their rules and limits.
    Each type defines what expenses are allowed and their maximum amounts.
    """
    report_code = models.CharField(max_length=5, unique=True)
    report_name = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    update_board = models.BooleanField(default=False)
    
    # Mileage reimbursement rates
    mileage_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('0.25'),
        help_text="Rate per mile for automobile"
    )
    max_passengers = models.IntegerField(default=3)
    passenger_mileage_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.05'),
        help_text="Additional rate per mile per passenger"
    )
    
    # Lodging limits
    max_lodging_per_night = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=Decimal('42.00'),
        help_text="Maximum reimbursement per night"
    )
    
    # Daily meal limits (en route)
    max_breakfast_daily = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('6.00')
    )
    max_lunch_daily = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('8.00')
    )
    max_dinner_daily = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('10.00')
    )
    
    # On-site meal limits
    max_breakfast_onsite = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('9.00')
    )
    max_lunch_onsite = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('15.00')
    )
    
    # Daily meal total limit
    daily_meal_limit = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Total daily meal limit (0 = no limit)"
    )
    
    # Descriptions for the form
    description = models.TextField(blank=True, help_text="Description of this report type")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['report_code']
        indexes = [
            models.Index(fields=['report_code']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.report_code} - {self.report_name}"


class ExpenseReport(models.Model):
    """
    Main expense report submitted by a member.
    Tracks the report through review, approval, and payment.
    """
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('reviewed', 'Reviewed'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
        ('rejected', 'Rejected'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('check', 'Check'),
        ('direct_deposit', 'Direct Deposit'),
        ('credit', 'Credit to Account'),
        ('other', 'Other'),
    ]
    
    # Basic information
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='expense_reports'
    )
    report_type = models.ForeignKey(
        ExpenseReportType,
        on_delete=models.PROTECT,
        related_name='expense_reports'
    )
    chapter = models.CharField(
        max_length=100,
        help_text="Chapter name or code"
    )
    report_date = models.DateField(help_text="Date of the event/trip")
    
    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='submitted'
    )
    
    # Review and approval
    reviewer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_expense_reports'
    )
    review_date = models.DateTimeField(null=True, blank=True)
    
    approver = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_expense_reports'
    )
    approval_date = models.DateTimeField(null=True, blank=True)
    
    # Payment information
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        blank=True
    )
    payment_check_number = models.CharField(max_length=50, blank=True)
    payment_payer = models.CharField(max_length=200, blank=True)
    paid_date = models.DateTimeField(null=True, blank=True)
    
    # Member verification
    verified_by_member = models.BooleanField(default=False)
    verified_date = models.DateTimeField(null=True, blank=True)
    
    # Validation and totals
    validation_code = models.CharField(max_length=50, blank=True)
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Total reimbursement amount"
    )
    
    # Receipt file (combined PDF)
    receipt = models.FileField(
        upload_to='receipts/',
        blank=True,
        null=True,
        help_text="Combined PDF of all receipt images"
    )
    
    # Notes
    notes = models.TextField(blank=True, help_text="Internal notes")
    rejection_reason = models.TextField(blank=True, help_text="Reason for rejection")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['member', 'status']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['report_date']),
        ]
    
    def __str__(self):
        return f"{self.member} - {self.report_type.report_code} - {self.report_date}"
    
    def calculate_total(self):
        """
        Calculate total reimbursement based on expense details.
        Returns the total amount.
        """
        if not hasattr(self, 'details'):
            return Decimal('0.00')
        
        details = self.details
        report_type = self.report_type
        total = Decimal('0.00')
        
        # Automobile mileage
        if details.automobile_miles:
            base_mileage = details.automobile_miles * report_type.mileage_rate
            passenger_mileage = (
                details.automobile_miles * 
                details.passengers * 
                report_type.passenger_mileage_rate
            )
            total += base_mileage + passenger_mileage
        
        # Tolls
        total += details.automobile_tolls
        
        # Lodging
        if details.lodging_nights and details.lodging_per_night:
            lodging_total = min(
                details.lodging_per_night * details.lodging_nights,
                report_type.max_lodging_per_night * details.lodging_nights
            )
            total += lodging_total
        
        # En route meals
        total += min(details.breakfast_enroute * report_type.max_breakfast_daily, 
                     details.breakfast_enroute * Decimal('100.00'))
        total += min(details.lunch_enroute * report_type.max_lunch_daily,
                     details.lunch_enroute * Decimal('100.00'))
        total += min(details.dinner_enroute * report_type.max_dinner_daily,
                     details.dinner_enroute * Decimal('100.00'))
        
        # On-site meals
        total += min(details.breakfast_onsite * report_type.max_breakfast_onsite,
                     details.breakfast_onsite * Decimal('100.00'))
        total += min(details.lunch_onsite * report_type.max_lunch_onsite,
                     details.lunch_onsite * Decimal('100.00'))
        
        # Other costs
        total += details.terminal_cost
        total += details.public_carrier_cost
        total += details.other_onsite_cost
        
        return total
    
    def save(self, *args, **kwargs):
        # Recalculate total before saving
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Recalculate after save if details exist
        if not is_new and hasattr(self, 'details'):
            calculated_total = self.calculate_total()
            if self.total_amount != calculated_total:
                self.total_amount = calculated_total
                super().save(update_fields=['total_amount'])


class ExpenseReportDetail(models.Model):
    """
    Detailed expense information for a report.
    Contains all the actual expenses submitted by the member.
    """
    expense_report = models.OneToOneField(
        ExpenseReport,
        on_delete=models.CASCADE,
        related_name='details'
    )
    
    # Automobile expenses
    automobile_miles = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    automobile_tolls = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    passengers = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Number of passengers (not including driver)"
    )
    
    # Lodging
    lodging_nights = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    lodging_per_night = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Actual cost per night"
    )
    
    # En route meals (number of meals)
    breakfast_enroute = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Number of breakfasts en route"
    )
    lunch_enroute = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Number of lunches en route"
    )
    dinner_enroute = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Number of dinners en route"
    )
    
    # On-site meals (number of meals)
    breakfast_onsite = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Number of breakfasts at convention"
    )
    lunch_onsite = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Number of lunches at convention"
    )
    
    # Other transportation costs
    terminal_cost = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Airport parking, etc."
    )
    public_carrier_cost = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Airline, train, bus, etc."
    )
    
    # Other costs
    other_onsite_cost = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Other on-site expenses"
    )
    
    # Flags
    billed_to_hq = models.BooleanField(
        default=False,
        help_text="Was this billed directly to headquarters?"
    )
    
    # Additional notes
    expense_notes = models.TextField(
        blank=True,
        help_text="Additional notes about expenses"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Details for {self.expense_report}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Trigger recalculation on parent report
        self.expense_report.save()
