from django.apps import AppConfig


class CompaniesConfig(AppConfig):
	default_auto_field = 'django.db.models.BigAutoField'
	name = 'companies'
	verbose_name = 'Empresas'
	
	def ready(self):
		"""Import schema extensions when app is ready."""
		# Import to register the OpenAPI authentication extension
		from . import schema  # noqa: F401

