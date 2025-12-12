from django.urls import path, include
from . import views
from .views import AddressViewSet, VerifyMemberAPIView, ChapterListAPIView, PhoneNumberViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'api/accounts/addresses', AddressViewSet, basename='address')
router.register(r'api/accounts/phone-numbers', PhoneNumberViewSet, basename='phone-numbers')

urlpatterns = [
    path('api/accounts/set-csrf-token', views.set_csrf_token, name='set_csrf_token'),
    path('api/accounts/login', views.login_view, name='login'),
    path('api/accounts/logout', views.logout_view, name='logout'),
    path('api/accounts/user', views.user_view, name='user'),
    path('api/accounts/register', views.register, name='register'),
    path('api/accounts/code-check', views.code_check, name='code_check'),
    path('api/accounts/chapter-list', ChapterListAPIView.as_view(), name='chapter_list'),
    path('api/accounts/verify-member', VerifyMemberAPIView.as_view(), name='verify_member'),
    path('api/accounts/activate/<str:uidb64>/<str:token>/', views.activate, name='activate'),
    path('api/accounts/password-reset-request', views.password_reset_request, name='password_reset_request'),
    path('api/accounts/password-reset-confirm/<str:uidb64>/<str:token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('api/accounts/user-account', views.user_account_view, name='user_account'),
    path('api/accounts/states-provinces', views.state_province_list, name='state_province_list'),
] + router.urls  # Add router URLs to existing patterns