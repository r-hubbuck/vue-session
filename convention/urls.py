from django.urls import path
from . import views

app_name = 'convention'

urlpatterns = [
    path('', views.index, name='index'),
    path('convention/register/', views.register, name='register'),
]