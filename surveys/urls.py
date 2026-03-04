from django.urls import path
from . import views

app_name = 'surveys'

urlpatterns = [
    # User-facing
    path('', views.survey_list, name='survey-list'),
    path('<int:survey_id>/', views.survey_detail, name='survey-detail'),
    path('<int:survey_id>/my-response/', views.my_response, name='my-response'),
    path('<int:survey_id>/start/', views.start_survey, name='start-survey'),
    path('<int:survey_id>/responses/<int:response_id>/', views.save_draft, name='save-draft'),
    path('<int:survey_id>/responses/<int:response_id>/submit/', views.submit_survey, name='submit-survey'),

    # Staff-facing
    path('admin/', views.admin_survey_list, name='admin-survey-list'),
    path('admin/<int:survey_id>/', views.admin_survey_detail, name='admin-survey-detail'),
    path('admin/<int:survey_id>/results/', views.admin_survey_results, name='admin-survey-results'),
]
