import bleach
from rest_framework import serializers
from .models import ExpenseReportType, ExpenseReport, ExpenseReportDetail
from accounts.models import Member, Address


class AddressSerializer(serializers.ModelSerializer):
    """
    Serializer for member addresses.
    Used when displaying address information in expense reports.
    """
    display_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Address
        fields = [
            'id',
            'add_line1',
            'add_line2',
            'add_city',
            'add_state',
            'add_zip',
            'add_country',
            'add_type',
            'is_primary',
            'display_name',
        ]
        read_only_fields = ['id']
    
    def get_display_name(self, obj):
        """Return a formatted address string"""
        parts = [obj.add_line1]
        if obj.add_line2:
            parts.append(obj.add_line2)
        parts.append(f"{obj.add_city}, {obj.add_state} {obj.add_zip}" if obj.add_state else obj.add_city)
        if obj.add_country and obj.add_country != 'United States':
            parts.append(obj.add_country)
        return ', '.join(parts)


class ExpenseReportTypeSerializer(serializers.ModelSerializer):
    """
    Serializer for expense report types.
    Used when displaying available report types to users.
    """
    class Meta:
        model = ExpenseReportType
        fields = [
            'id',
            'report_code',
            'report_name',
            'is_active',
            'description',
            'mileage_rate',
            'max_passengers',
            'passenger_mileage_rate',
            'max_lodging_per_night',
            'max_breakfast_daily',
            'max_lunch_daily',
            'max_dinner_daily',
            'max_breakfast_onsite',
            'max_lunch_onsite',
            'daily_meal_limit',
        ]
        read_only_fields = ['id']


class ExpenseReportDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for expense report details.
    """
    class Meta:
        model = ExpenseReportDetail
        fields = [
            'id',
            'automobile_miles',
            'automobile_tolls',
            'passengers',
            'lodging_nights',
            'lodging_per_night',
            'breakfast_enroute',
            'lunch_enroute',
            'dinner_enroute',
            'breakfast_onsite',
            'lunch_onsite',
            'terminal_cost',
            'public_carrier_cost',
            'other_onsite_cost',
            'billed_to_hq',
            'expense_notes',
        ]
        read_only_fields = ['id']
    
    def validate_expense_notes(self, value):
        """Strip HTML tags from expense notes to prevent XSS"""
        if value:
            return bleach.clean(value, tags=[], strip=True)
        return value


class ExpenseReportListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing expense reports.
    Shows summary information only.
    """
    member_name = serializers.SerializerMethodField()
    report_type_name = serializers.CharField(source='report_type.report_name', read_only=True)
    report_type_code = serializers.CharField(source='report_type.report_code', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = ExpenseReport
        fields = [
            'id',
            'member_name',
            'report_type_code',
            'report_type_name',
            'chapter',
            'report_date',
            'status',
            'status_display',
            'total_amount',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_member_name(self, obj):
        return f"{obj.member.first_name} {obj.member.last_name}"


class ExpenseReportDetailedSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for viewing a complete expense report.
    Includes all fields and nested relationships.
    """
    member_name = serializers.SerializerMethodField()
    member_email = serializers.SerializerMethodField()
    report_type_detail = ExpenseReportTypeSerializer(source='report_type', read_only=True)
    report_type_code = serializers.CharField(source='report_type.report_code', read_only=True)
    report_type_name = serializers.CharField(source='report_type.report_name', read_only=True)
    mailing_address = AddressSerializer(read_only=True)
    details = ExpenseReportDetailSerializer(read_only=True)
    reviewer_name = serializers.SerializerMethodField()
    approver_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    receipt_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ExpenseReport
        fields = [
            'id',
            'member_name',
            'member_email',
            'report_type_detail',
            'report_type_code',
            'report_type_name',
            'chapter',
            'mailing_address',
            'report_date',
            'status',
            'status_display',
            'reviewer_name',
            'review_date',
            'approver_name',
            'approval_date',
            'payment_method',
            'payment_method_display',
            'payment_check_number',
            'payment_payer',
            'paid_date',
            'verified_by_member',
            'verified_date',
            'validation_code',
            'total_amount',
            'notes',
            'rejection_reason',
            'receipt_url',
            'details',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'total_amount',
            'created_at',
            'updated_at',
        ]
    
    def get_member_name(self, obj):
        return f"{obj.member.first_name} {obj.member.last_name}"
    
    def get_member_email(self, obj):
        return obj.member.user.email if obj.member.user else None
    
    def get_reviewer_name(self, obj):
        if obj.reviewer:
            return obj.reviewer.email
        return None
    
    def get_approver_name(self, obj):
        if obj.approver:
            return obj.approver.email
        return None
    
    def get_receipt_url(self, obj):
        """Return the URL for the receipt PDF if it exists"""
        if obj.receipt:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.receipt.url)
            return obj.receipt.url
        return None


class ExpenseReportCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new expense report.
    Includes nested creation of expense details.
    Note: Receipt files should be uploaded separately via the upload_receipts endpoint.
    """
    details = ExpenseReportDetailSerializer(required=True)
    
    class Meta:
        model = ExpenseReport
        fields = [
            'report_type',
            'mailing_address',
            'report_date',
            'details',
        ]
    
    def validate_mailing_address(self, value):
        """Validate that the address belongs to the member"""
        request = self.context.get('request')
        if request and hasattr(request.user, 'member'):
            if value.member != request.user.member:
                raise serializers.ValidationError(
                    'You can only select addresses that belong to you.'
                )
        return value
    
    def create(self, validated_data):
        details_data = validated_data.pop('details')
        
        # Create the expense report
        expense_report = ExpenseReport.objects.create(**validated_data)
        
        # Create the details
        ExpenseReportDetail.objects.create(
            expense_report=expense_report,
            **details_data
        )
        
        # Calculate and save total
        expense_report.total_amount = expense_report.calculate_total()
        expense_report.save()
        
        return expense_report


class ReceiptUploadSerializer(serializers.Serializer):
    """
    Serializer for uploading receipt files.
    Accepts multiple files and combines them into a single PDF.
    """
    files = serializers.ListField(
        child=serializers.FileField(
            max_length=100000,
            allow_empty_file=False,
            use_url=False
        ),
        allow_empty=False,
        help_text="List of receipt files (PNG, JPG, or PDF)"
    )
    
    def validate_files(self, files):
        """Validate uploaded files"""
        from .utils import validate_receipt_files
        
        try:
            validate_receipt_files(files)
        except Exception as e:
            raise serializers.ValidationError(str(e))
        
        return files


class ExpenseReportUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating an expense report.
    Allows updating both report and detail fields.
    """
    details = ExpenseReportDetailSerializer(required=False)
    
    class Meta:
        model = ExpenseReport
        fields = [
            'report_date',
            'details',
        ]
    
    def update(self, instance, validated_data):
        details_data = validated_data.pop('details', None)
        
        # Update expense report fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update details if provided
        if details_data and hasattr(instance, 'details'):
            details = instance.details
            for attr, value in details_data.items():
                setattr(details, attr, value)
            details.save()
        
        # Recalculate total
        instance.total_amount = instance.calculate_total()
        instance.save()
        
        return instance


class ExpenseReportStaffUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for staff to update expense report status, review, and payment.
    """
    class Meta:
        model = ExpenseReport
        fields = [
            'status',
            'review_date',
            'approval_date',
            'payment_method',
            'payment_check_number',
            'payment_payer',
            'paid_date',
            'notes',
            'rejection_reason',
        ]
    
    def validate_notes(self, value):
        """Strip HTML tags from notes to prevent XSS"""
        if value:
            return bleach.clean(value, tags=[], strip=True)
        return value
    
    def validate_rejection_reason(self, value):
        """Strip HTML tags from rejection reason to prevent XSS"""
        if value:
            return bleach.clean(value, tags=[], strip=True)
        return value
    
    def validate_payment_check_number(self, value):
        """Validate and sanitize check number"""
        if value:
            value = value.strip()
            if len(value) > 50:
                raise serializers.ValidationError('Check number cannot exceed 50 characters.')
            # Remove any potentially malicious content
            value = bleach.clean(value, tags=[], strip=True)
        return value
    
    def validate_payment_payer(self, value):
        """Validate and sanitize payer name"""
        if value:
            value = value.strip()
            if len(value) > 200:
                raise serializers.ValidationError('Payer name cannot exceed 200 characters.')
            # Remove any potentially malicious content
            value = bleach.clean(value, tags=[], strip=True)
        return value
    
    def update(self, instance, validated_data):
        user = self.context['request'].user
        
        # Automatically set reviewer/approver based on status changes
        if 'status' in validated_data:
            new_status = validated_data['status']
            
            if new_status == 'reviewed' and not instance.reviewer:
                instance.reviewer = user
            
            if new_status == 'approved' and not instance.approver:
                instance.approver = user
        
        # Update all fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance
