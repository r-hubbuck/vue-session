from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm
from .models import User, Member, Address, PhoneNumber, StateProvince, Person, Staff, GuestSpeaker, Gender


class UserWithPersonCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, required=True, label='First name')
    last_name = forms.CharField(max_length=100, required=True, label='Last name')
    preferred_first_name = forms.CharField(max_length=100, required=False, label='Preferred first name')
    middle_name = forms.CharField(max_length=100, required=False, label='Middle name')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email',)


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'preferred_first_name', 'gender', 'birth_date', 'initiation_date')
    search_fields = ('first_name', 'last_name', 'preferred_first_name')


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('person', 'department')
    list_filter = ('department',)
    raw_id_fields = ('person',)


@admin.register(GuestSpeaker)
class GuestSpeakerAdmin(admin.ModelAdmin):
    list_display = ('person', 'company')
    search_fields = ('person__first_name', 'person__last_name', 'company')
    raw_id_fields = ('person',)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = UserWithPersonCreationForm
    list_display = ('email', 'get_roles', 'is_active', 'is_staff', 'get_person_name')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'groups')
    search_fields = ('email', 'alt_email')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Contact Information', {'fields': ('alt_email',)}),
        ('Person Link', {'fields': ('person',)}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        ('Account', {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
        ('Person', {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'preferred_first_name', 'middle_name'),
        }),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change and obj.person is None:
            person = Person.objects.create(
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                preferred_first_name=form.cleaned_data.get('preferred_first_name', ''),
                middle_name=form.cleaned_data.get('middle_name', ''),
            )
            obj.person = person
            obj.save(update_fields=['person'])

    filter_horizontal = ('groups', 'user_permissions')

    def get_person_name(self, obj):
        if obj.person:
            return str(obj.person)
        return "No person linked"
    get_person_name.short_description = 'Person Name'

    def get_roles(self, obj):
        roles = obj.groups.values_list('name', flat=True)
        if roles:
            return ", ".join(roles)
        return "No roles"
    get_roles.short_description = 'Roles'


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = (
        'member_id',
        'get_first_name',
        'get_last_name',
        'chapter',
        'district',
        'get_user_email',
        'get_user_roles'
    )
    list_filter = ('chapter', 'district')
    search_fields = (
        'member_id',
        'person__first_name',
        'person__last_name',
        'person__preferred_first_name',
        'chapter'
    )
    raw_id_fields = ('person',)

    fieldsets = (
        ('Person Link', {
            'fields': ('person',)
        }),
        ('Member Information', {
            'fields': ('member_id',)
        }),
        ('Chapter & District', {
            'fields': ('chapter', 'district')
        }),
    )

    readonly_fields = ('get_user_info',)

    def get_first_name(self, obj):
        return obj.person.first_name
    get_first_name.short_description = 'First Name'
    get_first_name.admin_order_field = 'person__first_name'

    def get_last_name(self, obj):
        return obj.person.last_name
    get_last_name.short_description = 'Last Name'
    get_last_name.admin_order_field = 'person__last_name'

    def get_user_email(self, obj):
        try:
            user = obj.person.user
            return user.email
        except Exception:
            return 'No user linked'
    get_user_email.short_description = 'Email'

    def get_user_roles(self, obj):
        try:
            user = obj.person.user
            roles = user.groups.values_list('name', flat=True)
            if roles:
                return ", ".join(roles)
            return "No roles"
        except Exception:
            return 'No user'
    get_user_roles.short_description = 'Roles'

    def get_user_info(self, obj):
        try:
            user = obj.person.user
            roles = user.groups.values_list('name', flat=True)
            roles_str = ", ".join(roles) if roles else "No roles"
            return f"{user.email} ({roles_str})"
        except Exception:
            return "No user account linked to this member"
    get_user_info.short_description = 'Linked User Account'


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = (
        'get_person_name',
        'add_type',
        'add_line1',
        'add_city',
        'add_state',
        'add_country',
        'is_primary'
    )
    list_filter = ('add_type', 'add_country', 'add_state', 'is_primary')
    search_fields = (
        'person__first_name',
        'person__last_name',
        'add_line1',
        'add_city',
        'add_state',
        'add_zip'
    )
    raw_id_fields = ('person',)

    fieldsets = (
        ('Person', {
            'fields': ('person',)
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

    def get_person_name(self, obj):
        return str(obj.person)
    get_person_name.short_description = 'Person'
    get_person_name.admin_order_field = 'person__last_name'


@admin.register(PhoneNumber)
class PhoneNumberAdmin(admin.ModelAdmin):
    list_display = (
        'get_person_name',
        'phone_type',
        'get_formatted',
        'is_primary'
    )
    list_filter = ('phone_type', 'is_primary', 'country_code')
    search_fields = (
        'person__first_name',
        'person__last_name',
        'phone_number'
    )
    raw_id_fields = ('person',)

    fieldsets = (
        ('Person', {
            'fields': ('person',)
        }),
        ('Phone Type', {
            'fields': ('phone_type', 'is_primary')
        }),
        ('Phone Number', {
            'fields': ('country_code', 'phone_number')
        }),
    )

    def get_person_name(self, obj):
        return str(obj.person)
    get_person_name.short_description = 'Person'
    get_person_name.admin_order_field = 'person__last_name'

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


@admin.register(Gender)
class GenderAdmin(admin.ModelAdmin):
    list_display = ('id', 'gender', 'title')
    search_fields = ('gender',)
