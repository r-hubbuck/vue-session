from django.urls import path
from . import views

app_name = 'expense_reports'

urlpatterns = [
    # Expense report types
    path('types/', views.expense_report_types_list, name='report-types'),
    
    # User endpoints
    path('my-reports/', views.my_expense_reports, name='my-reports'),
    path('my-reports/<int:report_id>/', views.expense_report_detail, name='report-detail'),
    path('my-reports/<int:report_id>/upload-receipts/', views.upload_receipts, name='upload-receipts'),
    
    # Staff endpoints (for review and management)
    path('staff/reports/', views.all_expense_reports, name='staff-all-reports'),
    path('staff/reports/<int:report_id>/', views.staff_expense_report_detail, name='staff-report-detail'),
]
