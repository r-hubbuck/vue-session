from django.urls import path, include
from . import views
from .views import AddressViewSet, VerifyMemberAPIView, ChapterListAPIView, PhoneNumberViewSet
from .views import AdminAddressViewSet, AdminPhoneNumberViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'accounts/addresses', AddressViewSet, basename='address')
router.register(r'accounts/phone-numbers', PhoneNumberViewSet, basename='phone-numbers')

urlpatterns = [
    path('accounts/set-csrf-token', views.set_csrf_token, name='set_csrf_token'),
    path('accounts/login', views.login_view, name='login'),
    path('accounts/logout', views.logout_view, name='logout'),
    path('accounts/user', views.user_view, name='user'),
    path('accounts/register', views.register, name='register'),
    path('accounts/code-check', views.code_check, name='code_check'),
    path('accounts/chapter-list', ChapterListAPIView.as_view(), name='chapter_list'),
    path('accounts/verify-member', VerifyMemberAPIView.as_view(), name='verify_member'),
    path('accounts/activate/<str:uidb64>/<str:token>/', views.activate, name='activate'),
    path('accounts/password-reset-request', views.password_reset_request, name='password_reset_request'),
    path('accounts/password-reset-confirm/<str:uidb64>/<str:token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('accounts/user-account', views.user_account_view, name='user_account'),
    path('accounts/states-provinces', views.state_province_list, name='state_province_list'),

    # Admin user management
    path('accounts/admin/users/', views.admin_list_users, name='admin_list_users'),
    path('accounts/admin/users/<int:user_id>/user-account/', views.admin_user_account_view, name='admin_user_account'),
    path('accounts/admin/users/<int:user_id>/addresses/', AdminAddressViewSet.as_view({'get': 'list', 'post': 'create'}), name='admin-addresses-list'),
    path('accounts/admin/users/<int:user_id>/addresses/<int:pk>/', AdminAddressViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='admin-addresses-detail'),
    path('accounts/admin/users/<int:user_id>/addresses/<int:pk>/set_primary/', AdminAddressViewSet.as_view({'post': 'set_primary'}), name='admin-addresses-set-primary'),
    path('accounts/admin/users/<int:user_id>/phone-numbers/', AdminPhoneNumberViewSet.as_view({'get': 'list', 'post': 'create'}), name='admin-phones-list'),
    path('accounts/admin/users/<int:user_id>/phone-numbers/<int:pk>/', AdminPhoneNumberViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='admin-phones-detail'),
    path('accounts/admin/users/<int:user_id>/phone-numbers/<int:pk>/set_primary/', AdminPhoneNumberViewSet.as_view({'post': 'set_primary'}), name='admin-phones-set-primary'),
] + router.urls  # Add router URLs to existing patterns
