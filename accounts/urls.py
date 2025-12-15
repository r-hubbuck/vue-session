from django.urls import path, include
from . import views
from .views import AddressViewSet, VerifyMemberAPIView, ChapterListAPIView, PhoneNumberViewSet
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
] + router.urls  # Add router URLs to existing patterns