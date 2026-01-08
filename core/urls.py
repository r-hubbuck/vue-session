from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('accounts.urls')),
    path('api/convention/', include('convention.urls')),
    path('api/expense-reports/', include('expense_reports.urls')),
]