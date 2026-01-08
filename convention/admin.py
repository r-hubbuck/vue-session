from django.contrib import admin
from .models import (
    Convention,
    ConventionRegistration,
    ConventionTravel,
    ConventionGuest,
    ConventionAccommodation,
    ConventionCommitteePreference,
    Airport,
)


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ('code', 'state', 'description')
    list_filter = ('state',)
    search_fields = ('code', 'description', 'state')
    ordering = ('state', 'description')


@admin.register(Convention)
class ConventionAdmin(admin.ModelAdmin):
    list_display = ('name', 'year', 'location', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'year')
    search_fields = ('name', 'location')
    ordering = ('-year', '-start_date')
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'year', 'location', 'is_active')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date', 'registration_open_date', 'registration_close_date')
        }),
    )


@admin.register(ConventionRegistration)
class ConventionRegistrationAdmin(admin.ModelAdmin):
    list_display = (
        'get_member_name',
        'convention',
        'is_guest',
        'status_code',
        'registration_date',
        'at_convention',
        'credentials_received'
    )
    list_filter = ('convention', 'is_guest', 'status_code', 'at_convention', 'credentials_received')
    search_fields = (
        'member__first_name',
        'member__last_name',
        'member__member_id',
        'member__user__email'
    )
    raw_id_fields = ('member', 'convention', 'host_registration')
    date_hierarchy = 'registration_date'
    
    readonly_fields = ('registration_date', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Registration Info', {
            'fields': ('convention', 'member', 'status_code', 'registration_date')
        }),
        ('Guest Information', {
            'fields': ('is_guest', 'host_registration')
        }),
        ('Convention Status', {
            'fields': ('at_convention', 'checked_in_at', 'credentials_received', 'credentials_received_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_member_name(self, obj):
        return f"{obj.member.first_name} {obj.member.last_name}"
    get_member_name.short_description = 'Member'
    get_member_name.admin_order_field = 'member__last_name'


@admin.register(ConventionTravel)
class ConventionTravelAdmin(admin.ModelAdmin):
    list_display = (
        'get_member_name',
        'get_convention',
        'travel_method',
        'departure_airport',
        'return_airport',
        'outbound_flight_number',
        'return_flight_number',
        'needs_ground_transportation'
    )
    list_filter = ('travel_method', 'needs_ground_transportation', 'seat_preference')
    search_fields = (
        'registration__member__first_name',
        'registration__member__last_name',
        'outbound_flight_number',
        'return_flight_number',
        'departure_airport',
        'return_airport'
    )
    raw_id_fields = ('registration',)
    
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Registration', {
            'fields': ('registration',)
        }),
        ('Travel Method', {
            'fields': ('travel_method', 'seat_preference', 'needs_ground_transportation')
        }),
        ('Departure Request', {
            'fields': ('departure_airport', 'departure_date', 'departure_time_preference'),
            'description': 'Member\'s requested departure information'
        }),
        ('Return Request', {
            'fields': ('return_airport', 'return_date', 'return_time_preference'),
            'description': 'Member\'s requested return information'
        }),
        ('Outbound Flight - Booked', {
            'fields': (
                'outbound_airline',
                'outbound_flight_number',
                'outbound_departure_time',
                'outbound_arrival_time',
                'outbound_confirmation',
            ),
            'description': 'Staff-booked outbound flight details'
        }),
        ('Return Flight - Booked', {
            'fields': (
                'return_airline',
                'return_flight_number',
                'return_departure_time',
                'return_arrival_time',
                'return_confirmation',
            ),
            'description': 'Staff-booked return flight details'
        }),
        ('Additional Information', {
            'fields': ('flight_notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_member_name(self, obj):
        return f"{obj.registration.member.first_name} {obj.registration.member.last_name}"
    get_member_name.short_description = 'Member'
    get_member_name.admin_order_field = 'registration__member__last_name'
    
    def get_convention(self, obj):
        return obj.registration.convention.name
    get_convention.short_description = 'Convention'
    get_convention.admin_order_field = 'registration__convention__name'
    
    actions = ['send_flight_confirmation_emails']
    
    def send_flight_confirmation_emails(self, request, queryset):
        """Send flight confirmation emails to selected members"""
        from django.core.mail import EmailMultiAlternatives
        from django.template.loader import render_to_string
        from django.conf import settings
        
        DOMAIN = getattr(settings, 'DOMAIN', 'localhost:8000')
        sent_count = 0
        failed_count = 0
        
        for travel in queryset:
            # Only send if both flights are booked
            if not (travel.outbound_flight_number and travel.return_flight_number):
                continue
                
            try:
                member = travel.registration.member
                convention = travel.registration.convention
                mail_subject = f'{convention.name} - Your Flight Details'
                
                message = render_to_string('convention/flight_booking_confirmation_email.html', {
                    'member': member,
                    'convention': convention,
                    'travel': travel,
                    'registration': travel.registration,
                    'domain': DOMAIN,
                })
                
                to_email = member.user.email
                email_msg = EmailMultiAlternatives(
                    subject=mail_subject,
                    body='',
                    to=[to_email]
                )
                email_msg.attach_alternative(message, "text/html")
                email_msg.send()
                sent_count += 1
                
            except Exception as e:
                failed_count += 1
                self.message_user(
                    request,
                    f"Failed to send email to {travel.registration.member}: {str(e)}",
                    level='ERROR'
                )
        
        if sent_count > 0:
            self.message_user(
                request,
                f"Successfully sent {sent_count} flight confirmation email(s)",
                level='SUCCESS'
            )
        if failed_count > 0:
            self.message_user(
                request,
                f"Failed to send {failed_count} email(s)",
                level='WARNING'
            )
    
    send_flight_confirmation_emails.short_description = "Send flight confirmation emails"


@admin.register(ConventionGuest)
class ConventionGuestAdmin(admin.ModelAdmin):
    list_display = (
        'get_member_name',
        'guest_first_name',
        'guest_last_name',
        'guest_email',
        'guest_phone'
    )
    search_fields = (
        'guest_first_name',
        'guest_last_name',
        'guest_email',
        'registration__member__first_name',
        'registration__member__last_name'
    )
    raw_id_fields = ('registration',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Registration', {
            'fields': ('registration',)
        }),
        ('Guest Information', {
            'fields': ('guest_first_name', 'guest_last_name', 'guest_email', 'guest_phone')
        }),
        ('Special Requirements', {
            'fields': ('guest_dietary_restrictions', 'guest_special_requests')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_member_name(self, obj):
        return f"{obj.registration.member.first_name} {obj.registration.member.last_name}"
    get_member_name.short_description = 'Host Member'
    get_member_name.admin_order_field = 'registration__member__last_name'


@admin.register(ConventionAccommodation)
class ConventionAccommodationAdmin(admin.ModelAdmin):
    list_display = (
        'get_member_name',
        'package_choice',
        'needs_hotel',
        'check_in_date',
        'check_out_date',
        'roommate_preference',
        'room_number'
    )
    list_filter = ('package_choice', 'needs_hotel', 'roommate_preference')
    search_fields = (
        'registration__member__first_name',
        'registration__member__last_name',
        'specific_roommate_name',
        'room_number'
    )
    raw_id_fields = ('registration',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Registration', {
            'fields': ('registration',)
        }),
        ('Package Selection', {
            'fields': ('package_choice',)
        }),
        ('Hotel Information', {
            'fields': (
                'needs_hotel',
                'check_in_date',
                'check_out_date',
                'roommate_preference',
                'specific_roommate_name',
                'specific_roommate_chapter'
            )
        }),
        ('Dietary & Allergies', {
            'fields': ('food_allergies', 'dietary_restrictions', 'other_allergies')
        }),
        ('Room Assignment (Staff)', {
            'fields': ('room_number', 'room_confirmation'),
            'description': 'Populated by staff'
        }),
        ('Special Requests', {
            'fields': ('special_requests',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_member_name(self, obj):
        return f"{obj.registration.member.first_name} {obj.registration.member.last_name}"
    get_member_name.short_description = 'Member'
    get_member_name.admin_order_field = 'registration__member__last_name'


@admin.register(ConventionCommitteePreference)
class ConventionCommitteePreferenceAdmin(admin.ModelAdmin):
    list_display = (
        'get_member_name',
        'alumni_affairs',
        'awards',
        'chapter_operations',
        'collegiate_chapters',
        'communications',
        'constitution'
    )
    list_filter = (
        'alumni_affairs',
        'awards',
        'chapter_operations',
        'collegiate_chapters'
    )
    search_fields = (
        'registration__member__first_name',
        'registration__member__last_name'
    )
    raw_id_fields = ('registration',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Registration', {
            'fields': ('registration',)
        }),
        ('Committee Preferences', {
            'fields': (
                'alumni_affairs',
                'awards',
                'chapter_operations',
                'collegiate_chapters',
                'communications',
                'constitution',
                'engineering_futures',
                'membership',
                'public_relations',
                'resolutions',
                'rituals',
            ),
            'description': '0 = No Interest, 1 = Interested, 2 = Prefer'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_member_name(self, obj):
        return f"{obj.registration.member.first_name} {obj.registration.member.last_name}"
    get_member_name.short_description = 'Member'
    get_member_name.admin_order_field = 'registration__member__last_name'
