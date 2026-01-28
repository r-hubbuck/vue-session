from django.urls import path
from . import views

urlpatterns = [
    # Convention info
    path('current/', views.current_convention, name='current-convention'),
    
    # Reference data
    path('airports/', views.get_airports, name='get-airports'),
    path('states/', views.get_states, name='get-states'),
    
    # Registration
    path('my-registration/', views.my_registration, name='my-registration'),
    
    # Member info (updates Member model directly - no duplication)
    path('member/update-info/', views.update_member_info, name='update-member-info'),
    path('member/update-mobile-phone/', views.update_mobile_phone, name='update-mobile-phone'),
    path('member/address/<int:address_id>/set-primary/', views.set_primary_address, name='set-primary-address'),
    path('member/phone/<int:phone_id>/set-primary/', views.set_primary_phone, name='set-primary-phone'),
    
    # Committee preferences
    path('registration/<int:registration_id>/committee-preferences/', views.update_committee_preferences, name='update-committee-preferences'),
    
    # Guest management
    path('registration/<int:registration_id>/guests/', views.guest_management, name='guest-management'),
    path('registration/<int:registration_id>/guests/<int:guest_id>/', views.guest_detail, name='guest-detail'),
    
    # Travel
    path('registration/<int:registration_id>/travel/', views.update_travel, name='update-travel'),
    
    # Accommodation
    path('registration/<int:registration_id>/accommodation/', views.update_accommodation, name='update-accommodation'),
    
    # Admin endpoints
    path('admin/travel/', views.admin_travel_list, name='admin-travel-list'),
    path('admin/travel/<int:travel_id>/', views.admin_travel_detail, name='admin-travel-detail'),

    # Check-in endpoints (staff only)
    path('check-in/list/', views.check_in_list, name='check-in-list'),
    path('check-in/registration/<int:registration_id>/status/', views.update_registration_status, name='update-registration-status'),
    path('check-in/address/<int:address_id>/', views.update_member_address_checkin, name='update-member-address-checkin'),

]

# Available endpoints:
# GET    /api/convention/current/                                          - Get current active convention
# GET    /api/convention/airports/                                         - Get all airports (optionally filter by ?state=XX)
# GET    /api/convention/states/                                           - Get list of states with airports
# GET    /api/convention/my-registration/                                  - Get user's registration
# POST   /api/convention/my-registration/                                  - Create new registration
# 
# Member Info (updates Member, Address, PhoneNumbers models directly):
# PUT    /api/convention/member/update-info/                               - Update preferred_first_name
# PUT    /api/convention/member/address/{id}/set-primary/                  - Set primary address
# PUT    /api/convention/member/phone/{id}/set-primary/                    - Set primary phone
# 
# Convention-specific data:
# PUT    /api/convention/registration/{id}/committee-preferences/          - Update committee preferences
# GET    /api/convention/registration/{id}/guests/                         - List guests
# POST   /api/convention/registration/{id}/guests/                         - Add guest
# PUT    /api/convention/registration/{id}/guests/{guest_id}/              - Update guest
# DELETE /api/convention/registration/{id}/guests/{guest_id}/              - Remove guest
# PUT    /api/convention/registration/{id}/travel/                         - Update travel
# PUT    /api/convention/registration/{id}/accommodation/                  - Update accommodation
