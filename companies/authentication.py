"""Custom authentication for Company API Accounts."""
from rest_framework.authentication import BasicAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.hashers import check_password
from django.utils import timezone

from .models import CompanyAPIAccount


class CompanyAccountAuthentication(BasicAuthentication):
	"""
	Custom authentication using Company API Accounts with Basic Auth.
	
	This replaces JWT authentication with simple username/password.
	Each company can have multiple API accounts for different purposes.
	"""

	def authenticate_credentials(self, userid: str, password: str, request=None):
		"""
		Authenticate using CompanyAPIAccount.
		
		Args:
			userid: The username from Basic Auth
			password: The password from Basic Auth
			request: The request object
			
		Returns:
			Tuple of (user, auth) where user contains company info
			
		Raises:
			AuthenticationFailed: If credentials are invalid or account is inactive
		"""
		try:
			account = CompanyAPIAccount.objects.select_related('company').get(
				username=userid
			)
		except CompanyAPIAccount.DoesNotExist:
			raise AuthenticationFailed('Credenciais inválidas')

		# Check if account is active
		if not account.is_active:
			raise AuthenticationFailed('Conta desativada')

		# Check if company is operational (active contract and good payment)
		if not account.company.is_operational:
			raise AuthenticationFailed('Empresa não está operacional')

		# Verify password hash
		if not check_password(password, account.password):
			raise AuthenticationFailed('Credenciais inválidas')

		# Update last used timestamp asynchronously to avoid performance impact
		# We'll do this in a simple way without celery for now
		account.mark_used()

		# Create a pseudo-user object with company information
		# Django REST Framework expects a user object
		class APIUser:
			"""Pseudo user for API authentication."""
			is_authenticated = True
			is_active = True
			is_anonymous = False
			
			def __init__(self, company, api_account):
				self.company = company
				self.api_account = api_account
				self.username = api_account.username
				self.pk = None
				self.id = None
		
		user = APIUser(account.company, account)
		return (user, account)
