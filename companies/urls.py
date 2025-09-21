from django.urls import path
from . import views


urlpatterns = [
	# Token management
	path('companies/<int:pk>/tokens/', views.company_tokens, name='company_tokens'),
	path('companies/<int:pk>/tokens/create/', views.company_token_create, name='company_token_create'),
	path('companies/<int:pk>/tokens/<int:token_id>/revoke/', views.company_token_revoke, name='company_token_revoke'),
	
	# Token refresh (standard JWT approach for mobile and web)
	path('auth/refresh/', views.refresh_token, name='refresh_token'),
	
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

