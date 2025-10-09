from django.urls import path
from . import views


urlpatterns = [
	# API Accounts management (Basic Auth Authentication)
	path('companies/<int:pk>/accounts/', views.company_accounts, name='company_accounts'),
	path('companies/<int:pk>/accounts/create/', views.company_account_create, name='company_account_create'),
	path('companies/<int:pk>/accounts/<int:account_id>/deactivate/', views.company_account_deactivate, name='company_account_deactivate'),
	path('companies/<int:pk>/accounts/<int:account_id>/activate/', views.company_account_activate, name='company_account_activate'),
	path('companies/<int:pk>/accounts/<int:account_id>/delete/', views.company_account_delete, name='company_account_delete'),
	
	# Status management
	path('companies/<int:pk>/activate/', views.company_activate, name='company_activate'),
	path('companies/<int:pk>/deactivate/', views.company_deactivate, name='company_deactivate'),
	path('companies/<int:pk>/convert-to-client/', views.company_convert_to_client, name='company_convert_to_client'),
	path('companies/<int:pk>/suspend-payment/', views.company_suspend_payment, name='company_suspend_payment'),
	path('companies/<int:pk>/restore-payment/', views.company_restore_payment, name='company_restore_payment'),
	
	# Contact history management
	path('companies/<int:pk>/contacts/', views.company_contacts, name='company_contacts'),
	path('companies/<int:pk>/contacts/create/', views.company_contact_create, name='company_contact_create'),
	path('companies/<int:pk>/contacts/<int:contact_id>/delete/', views.company_contact_delete, name='company_contact_delete'),
]

