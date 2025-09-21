from django.urls import path
from . import views


urlpatterns = [
    path('api/v1/answers/submit/', views.submit_answers, name='answers_submit'),
    path('answers/', views.surveys_index, name='answers_summary'),
    path('answers/<int:survey_id>/dashboard/', views.survey_dashboard, name='answers_dashboard'),
    path('answers/<int:survey_id>/', views.submissions_detail, name='answers_detail'),
    path('answers/<int:survey_id>/delete/<int:submission_id>/', views.delete_submission, name='answers_delete_submission'),
    path('answers/<int:survey_id>/cities/', views.get_cities_for_state, name='answers_get_cities'),
]


