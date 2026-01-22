from django.contrib import admin
from django.utils.html import format_html
from .models import ExpenseReportType, ExpenseReport, ExpenseReportDetail


class ExpenseReportDetailInline(admin.StackedInline):
    """
    Inline admin for expense report details.
    Allows editing details directly within the expense report.
    """
    model = ExpenseReportDetail
    can_delete = False
    
    fieldsets = (
        ('Automobile Expenses', {
            'fields': (
                ('automobile_miles', 'passengers'),
                'automobile_tolls',
            )
        }),
        ('Lodging', {
            'fields': (
                ('lodging_nights', 'lodging_per_night'),
            )
        }),
        ('En Route Meals', {
            'fields': (
                ('breakfast_enroute', 'lunch_enroute', 'dinner_enroute'),
            )
        }),
        ('On-Site Meals', {
            'fields': (
                ('breakfast_onsite', 'lunch_onsite'),
            )
        }),
        ('Other Transportation', {
            'fields': (
                'terminal_cost',
                'public_carrier_cost',
            )
        }),
        ('Other Expenses', {
            'fields': (
                'other_onsite_cost',
                'billed_to_hq',
            )
        }),
        ('Notes', {
            'fields': ('expense_notes',),
            'classes': ('collapse',)
        }),
    )


@admin.register(ExpenseReportType)
class ExpenseReportTypeAdmin(admin.ModelAdmin):
    list_display = (
        'report_code',
        'report_name',
        'is_active',
        'mileage_rate',
        'max_lodging_per_night',
        'daily_meal_limit',
        'get_report_count'
    )
    list_filter = ('is_active', 'update_board')
    search_fields = ('report_code', 'report_name', 'description')
    ordering = ('report_code',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'report_code',
                'report_name',
                'is_active',
                'update_board',
                'description',
            )
        }),
        ('Mileage Rates', {
            'fields': (
                ('mileage_rate', 'passenger_mileage_rate'),
                'max_passengers',
            )
        }),
        ('Lodging Limits', {
            'fields': (
                'max_lodging_per_night',
            )
        }),
        ('Daily Meal Limits (En Route)', {
            'fields': (
                ('max_breakfast_daily', 'max_lunch_daily', 'max_dinner_daily'),
            )
        }),
        ('On-Site Meal Limits', {
            'fields': (
                ('max_breakfast_onsite', 'max_lunch_onsite'),
            )
        }),
        ('Total Daily Meal Limit', {
            'fields': (
                'daily_meal_limit',
            ),
            'description': 'Set to 0 for no limit'
        }),
    )
    
    readonly_fields = ('get_report_count',)
    
    def get_report_count(self, obj):
        """Display count of expense reports using this type"""
        count = obj.expense_reports.count()
        return count
    get_report_count.short_description = 'Reports Using This Type'


@admin.register(ExpenseReport)
class ExpenseReportAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'get_member_name',
        'report_type',
        'chapter',
        'report_date',
        'get_status_badge',
        'get_total_formatted',
        'created_at',
    )
    list_filter = (
        'status',
        'report_type',
        'report_date',
        'payment_method',
        'verified_by_member',
    )
    search_fields = (
        'member__first_name',
        'member__last_name',
        'member__member_id',
        'chapter',
        'validation_code',
    )
    date_hierarchy = 'report_date'
    ordering = ('-created_at',)
    
    raw_id_fields = ('member', 'reviewer', 'approver')
    
    readonly_fields = (
        'get_member_info',
        'total_amount',
        'created_at',
        'updated_at',
        'get_review_info',
        'get_approval_info',
        'get_payment_info',
        'get_receipt_link',
    )
    
    fieldsets = (
        ('Member Information', {
            'fields': (
                'member',
                'get_member_info',
            )
        }),
        ('Report Details', {
            'fields': (
                'report_type',
                'chapter',
                'mailing_address',
                'report_date',
            )
        }),
        ('Status', {
            'fields': (
                'status',
                'total_amount',
                'get_receipt_link',
            )
        }),
        ('Review', {
            'fields': (
                'reviewer',
                'review_date',
                'get_review_info',
            ),
            'classes': ('collapse',)
        }),
        ('Approval', {
            'fields': (
                'approver',
                'approval_date',
                'get_approval_info',
            ),
            'classes': ('collapse',)
        }),
        ('Payment', {
            'fields': (
                'payment_method',
                'payment_check_number',
                'payment_payer',
                'paid_date',
                'get_payment_info',
            ),
            'classes': ('collapse',)
        }),
        ('Member Verification', {
            'fields': (
                'verified_by_member',
                'verified_date',
                'validation_code',
            ),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': (
                'notes',
                'rejection_reason',
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ExpenseReportDetailInline]
    
    def get_member_name(self, obj):
        return f"{obj.member.first_name} {obj.member.last_name}"
    get_member_name.short_description = 'Member'
    get_member_name.admin_order_field = 'member__last_name'
    
    def get_member_info(self, obj):
        """Display member information"""
        member = obj.member
        try:
            from accounts.models import User
            user = User.objects.get(member=member)
            email = user.email
        except:
            email = "No email"
        
        return format_html(
            '<strong>{} {}</strong><br>Member ID: {}<br>Chapter: {}<br>Email: {}',
            member.first_name,
            member.last_name,
            member.member_id,
            obj.chapter,
            email
        )
    get_member_info.short_description = 'Member Details'
    
    def get_status_badge(self, obj):
        """Display status with colored badge"""
        colors = {
            'draft': 'gray',
            'submitted': 'blue',
            'under_review': 'orange',
            'approved': 'green',
            'paid': 'darkgreen',
            'rejected': 'red',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    get_status_badge.short_description = 'Status'
    get_status_badge.admin_order_field = 'status'
    
    def get_total_formatted(self, obj):
        """Display total with currency formatting"""
        return format_html('${:,.2f}', obj.total_amount)
    get_total_formatted.short_description = 'Total Amount'
    get_total_formatted.admin_order_field = 'total_amount'
    
    def get_review_info(self, obj):
        """Display review information"""
        if not obj.reviewer:
            return "Not yet reviewed"
        
        date_str = obj.review_date.strftime('%Y-%m-%d %H:%M') if obj.review_date else 'Date not set'
        return format_html(
            '<strong>Reviewer:</strong> {}<br><strong>Date:</strong> {}',
            obj.reviewer.email,
            date_str
        )
    get_review_info.short_description = 'Review Information'
    
    def get_approval_info(self, obj):
        """Display approval information"""
        if not obj.approver:
            return "Not yet approved"
        
        date_str = obj.approval_date.strftime('%Y-%m-%d %H:%M') if obj.approval_date else 'Date not set'
        return format_html(
            '<strong>Approver:</strong> {}<br><strong>Date:</strong> {}',
            obj.approver.email,
            date_str
        )
    get_approval_info.short_description = 'Approval Information'
    
    def get_payment_info(self, obj):
        """Display payment information"""
        if not obj.payment_method:
            return "Payment method not set"
        
        info = f"<strong>Method:</strong> {obj.get_payment_method_display()}<br>"
        
        if obj.payment_check_number:
            info += f"<strong>Check #:</strong> {obj.payment_check_number}<br>"
        
        if obj.payment_payer:
            info += f"<strong>Payer:</strong> {obj.payment_payer}<br>"
        
        if obj.paid_date:
            info += f"<strong>Paid:</strong> {obj.paid_date.strftime('%Y-%m-%d')}"
        else:
            info += "<strong>Paid:</strong> Not yet paid"
        
        return format_html(info)
    get_payment_info.short_description = 'Payment Information'
    
    def get_receipt_link(self, obj):
        """Display link to receipt PDF"""
        if obj.receipt:
            return format_html(
                '<a href="{}" target="_blank" class="button">View Receipt PDF</a>',
                obj.receipt.url
            )
        return "No receipt uploaded"
    get_receipt_link.short_description = 'Receipt'
    
    def save_model(self, request, obj, form, change):
        """Recalculate total when saving"""
        super().save_model(request, obj, form, change)
        # Total will be recalculated automatically by the model's save method


@admin.register(ExpenseReportDetail)
class ExpenseReportDetailAdmin(admin.ModelAdmin):
    """
    Standalone admin for expense report details.
    Usually these are edited via the ExpenseReport inline.
    """
    list_display = (
        'get_report_id',
        'get_member_name',
        'automobile_miles',
        'lodging_nights',
        'get_meal_count',
        'get_other_costs',
    )
    search_fields = (
        'expense_report__member__first_name',
        'expense_report__member__last_name',
        'expense_notes',
    )
    
    raw_id_fields = ('expense_report',)
    
    fieldsets = (
        ('Expense Report', {
            'fields': ('expense_report',)
        }),
        ('Automobile Expenses', {
            'fields': (
                ('automobile_miles', 'passengers'),
                'automobile_tolls',
            )
        }),
        ('Lodging', {
            'fields': (
                ('lodging_nights', 'lodging_per_night'),
            )
        }),
        ('En Route Meals', {
            'fields': (
                ('breakfast_enroute', 'lunch_enroute', 'dinner_enroute'),
            )
        }),
        ('On-Site Meals', {
            'fields': (
                ('breakfast_onsite', 'lunch_onsite'),
            )
        }),
        ('Other Transportation', {
            'fields': (
                'terminal_cost',
                'public_carrier_cost',
            )
        }),
        ('Other Expenses', {
            'fields': (
                'other_onsite_cost',
                'billed_to_hq',
            )
        }),
        ('Notes', {
            'fields': ('expense_notes',)
        }),
    )
    
    def get_report_id(self, obj):
        return obj.expense_report.id
    get_report_id.short_description = 'Report ID'
    get_report_id.admin_order_field = 'expense_report__id'
    
    def get_member_name(self, obj):
        member = obj.expense_report.member
        return f"{member.first_name} {member.last_name}"
    get_member_name.short_description = 'Member'
    get_member_name.admin_order_field = 'expense_report__member__last_name'
    
    def get_meal_count(self, obj):
        """Total number of meals"""
        total = (
            obj.breakfast_enroute + obj.lunch_enroute + obj.dinner_enroute +
            obj.breakfast_onsite + obj.lunch_onsite
        )
        return total
    get_meal_count.short_description = 'Total Meals'
    
    def get_other_costs(self, obj):
        """Sum of other costs"""
        total = obj.terminal_cost + obj.public_carrier_cost + obj.other_onsite_cost
        return format_html('${:,.2f}', total)
    get_other_costs.short_description = 'Other Costs'
