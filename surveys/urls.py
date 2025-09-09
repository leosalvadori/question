from django.urls import path
from . import views


urlpatterns = [
	path('companies/', views.company_list, name='company_list'),
	path('companies/prospects/', views.company_prospects, name='company_prospects'),
	path('companies/clients/', views.company_clients, name='company_clients'),
	path('companies/create/', views.company_create, name='company_create'),
	path('companies/<int:pk>/', views.company_detail, name='company_detail'),
	path('companies/<int:pk>/edit/', views.company_update, name='company_update'),
	path('companies/<int:pk>/delete/', views.company_delete, name='company_delete'),

	path('surveys/', views.survey_list, name='survey_list'),
	path('surveys/create/', views.survey_create, name='survey_create'),

	# Preview (public, no bearer)
	path('surveys/preview/', views.survey_preview_start, name='survey_preview_start'),
	path('surveys/preview/<str:token>/', views.survey_preview, name='survey_preview'),
	path('surveys/preview/<str:token>/success/', views.survey_preview_success, name='survey_preview_success'),
	path('surveys/<int:pk>/', views.survey_detail, name='survey_detail'),
	path('surveys/<int:pk>/edit/', views.survey_update, name='survey_update'),
	path('surveys/<int:pk>/delete/', views.survey_delete, name='survey_delete'),

	path('questions/create/<int:survey_id>/', views.question_create, name='question_create'),
	path('questions/<int:pk>/edit/', views.question_update, name='question_update'),
	path('questions/<int:pk>/delete/', views.question_delete, name='question_delete'),

	path('options/create/<int:question_id>/', views.option_create, name='option_create'),
	path('options/<int:pk>/edit/', views.option_update, name='option_update'),
	path('options/<int:pk>/delete/', views.option_delete, name='option_delete'),

	# API Endpoint para obter pesquisa detalhada por token (?token=...)
	path('api/v1/survey/', views.api_survey_detail, name='api_survey_detail'),
]

