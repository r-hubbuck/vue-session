from rest_framework import serializers
from .models import ExpenseReportType, ExpenseReport, ExpenseReportDetail
from accounts.models import Member


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
            'implemented',
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
    details = ExpenseReportDetailSerializer(read_only=True)
    reviewer_name = serializers.SerializerMethodField()
    approver_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    
    class Meta:
        model = ExpenseReport
        fields = [
            'id',
            'member_name',
            'member_email',
            'report_type_detail',
            'chapter',
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


class ExpenseReportCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new expense report.
    Includes nested creation of expense details.
    """
    details = ExpenseReportDetailSerializer(required=True)
    
    class Meta:
        model = ExpenseReport
        fields = [
            'report_type',
            'chapter',
            'report_date',
            'details',
        ]
    
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


class ExpenseReportUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating an expense report.
    Allows updating both report and detail fields.
    """
    details = ExpenseReportDetailSerializer(required=False)
    
    class Meta:
        model = ExpenseReport
        fields = [
            'chapter',
            'report_date',
            'status',
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
    
    def update(self, instance, validated_data):
        user = self.context['request'].user
        
        # Automatically set reviewer/approver based on status changes
        if 'status' in validated_data:
            new_status = validated_data['status']
            
            if new_status == 'under_review' and not instance.reviewer:
                instance.reviewer = user
            
            if new_status == 'approved' and not instance.approver:
                instance.approver = user
        
        # Update all fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance
