from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Member, Address, PhoneNumber, StateProvince


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'get_roles', 'is_active', 'is_staff', 'get_member_name')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'groups')
    search_fields = ('email', 'alt_email')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Contact Information', {'fields': ('alt_email',)}),
        ('Member Link', {'fields': ('member',)}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    
    filter_horizontal = ('groups', 'user_permissions')
    
    def get_member_name(self, obj):
        if obj.member:
            return f"{obj.member.first_name} {obj.member.last_name}"
        return "No member linked"
    get_member_name.short_description = 'Member Name'
    
    def get_roles(self, obj):
        """Display all roles (groups) for the user"""
        roles = obj.groups.values_list('name', flat=True)
        if roles:
            return ", ".join(roles)
        return "No roles"
    get_roles.short_description = 'Roles'


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = (
        'member_id',
        'first_name',
        'last_name',
        'chapter',
        'district',
        'get_user_email',
        'get_user_roles'
    )
    list_filter = ('chapter', 'district')
    search_fields = (
        'member_id',
        'first_name',
        'last_name',
        'preferred_first_name',
        'chapter'
    )
    
    fieldsets = (
        ('Member Information', {
            'fields': ('member_id', 'first_name', 'preferred_first_name', 'middle_name', 'last_name')
        }),
        ('Chapter & District', {
            'fields': ('chapter', 'district')
        }),
    )
    
    readonly_fields = ('get_user_info',)
    
    def get_user_email(self, obj):
        try:
            user = User.objects.get(member=obj)
            return user.email
        except User.DoesNotExist:
            return 'No user linked'
    get_user_email.short_description = 'Email'
    
    def get_user_roles(self, obj):
        """Display all roles for the user linked to this member"""
        try:
            user = User.objects.get(member=obj)
            roles = user.groups.values_list('name', flat=True)
            if roles:
                return ", ".join(roles)
            return "No roles"
        except User.DoesNotExist:
            return 'No user'
    get_user_roles.short_description = 'Roles'
    
    def get_user_info(self, obj):
        """Display linked user information"""
        try:
            user = User.objects.get(member=obj)
            roles = user.groups.values_list('name', flat=True)
            roles_str = ", ".join(roles) if roles else "No roles"
            return f"{user.email} ({roles_str})"
        except User.DoesNotExist:
            return "No user account linked to this member"
    get_user_info.short_description = 'Linked User Account'


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = (
        'get_member_name',
        'add_type',
        'add_line1',
        'add_city',
        'add_state',
        'add_country',
        'is_primary'
    )
    list_filter = ('add_type', 'add_country', 'add_state', 'is_primary')
    search_fields = (
        'member__first_name',
        'member__last_name',
        'add_line1',
        'add_city',
        'add_state',
        'add_zip'
    )
    raw_id_fields = ('member',)
    
    fieldsets = (
        ('Member', {
            'fields': ('member',)
        }),
        ('Address Type', {
            'fields': ('add_type', 'is_primary')
        }),
        ('Address', {
            'fields': (
                'add_line1',
                'add_line2',
                'add_city',
                'add_state',
                'add_zip',
                'add_country'
            )
        }),
    )
    
    def get_member_name(self, obj):
        return f"{obj.member.first_name} {obj.member.last_name}"
    get_member_name.short_description = 'Member'
    get_member_name.admin_order_field = 'member__last_name'


@admin.register(PhoneNumber)
class PhoneNumberAdmin(admin.ModelAdmin):
    list_display = (
        'get_member_name',
        'phone_type',
        'get_formatted',
        'is_primary'
    )
    list_filter = ('phone_type', 'is_primary', 'country_code')
    search_fields = (
        'member__first_name',
        'member__last_name',
        'phone_number'
    )
    raw_id_fields = ('member',)
    
    fieldsets = (
        ('Member', {
            'fields': ('member',)
        }),
        ('Phone Type', {
            'fields': ('phone_type', 'is_primary')
        }),
        ('Phone Number', {
            'fields': ('country_code', 'phone_number')
        }),
    )
    
    def get_member_name(self, obj):
        return f"{obj.member.first_name} {obj.member.last_name}"
    get_member_name.short_description = 'Member'
    get_member_name.admin_order_field = 'member__last_name'
    
    def get_formatted(self, obj):
        return obj.get_formatted_number()
    get_formatted.short_description = 'Formatted Number'


@admin.register(StateProvince)
class StateProvinceAdmin(admin.ModelAdmin):
    list_display = (
        'st_abbrev',
        'st_name',
        'country_name',
        'st_region',
        'st_conus',
        'st_foreign'
    )
    list_filter = ('st_conus', 'st_foreign', 'st_region')
    search_fields = ('st_name', 'st_abbrev')
    ordering = ('st_name',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('st_id', 'st_name', 'st_abbrev')
        }),
        ('Location', {
            'fields': ('st_region', 'st_ctrid', 'st_conus', 'st_foreign')
        }),
        ('Zip Code Range', {
            'fields': ('st_strtzip', 'st_endzip')
        }),
    )
    
    readonly_fields = ('st_id',)