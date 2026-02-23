from django.urls import path
from . import views

urlpatterns = [
    # Recruiter self-registration & profile
    path('register/', views.recruiter_register, name='recruiter_register'),
    path('profile/', views.recruiter_profile_view, name='recruiter_profile'),
    path('organization/', views.update_organization, name='update_organization'),

    # Admin: approve recruiters
    path('admin/pending/', views.admin_pending_recruiters, name='admin_pending_recruiters'),
    path('admin/approve/<int:pk>/', views.admin_approve_recruiter, name='admin_approve_recruiter'),
    path('admin/organizations/', views.admin_organizations, name='admin_organizations'),

    # Convention: booth packages & meal options
    path('convention/booth-packages/', views.booth_packages, name='booth_packages'),
    path('convention/meal-options/', views.meal_options, name='meal_options'),

    # Convention: recruiter registration
    path('convention/register/', views.recruiter_convention_register, name='recruiter_convention_register'),
    path('convention/my-registration/', views.recruiter_my_registration, name='recruiter_my_registration'),

    # Admin: manage registrations
    path('admin/registrations/', views.admin_registrations, name='admin_registrations'),
    path('admin/registrations/<int:pk>/', views.admin_update_registration, name='admin_update_registration'),

    # Attendees
    path('convention/attendees/', views.recruiter_attendees, name='recruiter_attendees'),
    path('convention/attendees/<int:member_id>/resume/', views.recruiter_attendee_resume, name='recruiter_attendee_resume'),

    # Member resume upload (used by members, not recruiters)
    path('member/resume/', views.member_resume, name='member_resume'),

    # Invoices
    path('admin/invoices/', views.admin_invoices, name='admin_invoices'),
    path('admin/invoices/<int:pk>/', views.admin_update_invoice, name='admin_update_invoice'),
    path('invoices/', views.recruiter_invoices, name='recruiter_invoices'),
]
