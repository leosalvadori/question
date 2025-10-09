"""OpenAPI schema extensions for Company authentication."""
from drf_spectacular.extensions import OpenApiAuthenticationExtension


class CompanyAccountAuthenticationScheme(OpenApiAuthenticationExtension):
	"""OpenAPI extension for CompanyAccountAuthentication."""
	
	target_class = 'companies.authentication.CompanyAccountAuthentication'
	name = 'BasicAuth'
	
	def get_security_definition(self, auto_schema):
		"""Define the security scheme for Basic Auth."""
		return {
			'type': 'http',
			'scheme': 'basic',
			'description': 'Username e password da conta API'
		}
