from django.urls import path
from . import views
from .views import VerifyMemberAPIView, ChapterListAPIView

urlpatterns = [
    path('api/set-csrf-token', views.set_csrf_token, name='set_csrf_token'),
    path('api/login', views.login_view, name='login'),
    path('api/logout', views.logout_view, name='logout'),
    path('api/user', views.user_view, name='user'),
    path('api/register', views.register, name='register'),
    path('api/code-check', views.code_check, name='code_check'),
    path('api/chapter-list', ChapterListAPIView.as_view(), name='chapter_list'),
    path('api/verify-member', VerifyMemberAPIView.as_view(), name='verify_member'),
    path('api/activate/<str:uidb64>/<str:token>/', views.activate, name='activate'),
]