from django.db import models
from django.utils import timezone


class Company(models.Model):
	# Status choices for company lifecycle
	PROSPECT = 'prospect'
	CLIENT = 'client'
	COMPANY_TYPE_CHOICES = [
		(PROSPECT, 'Prospect (Em análise)'),
		(CLIENT, 'Cliente (Operando)'),
	]

	# Payment status choices
	PAYMENT_ACTIVE = 'active'
	PAYMENT_OVERDUE = 'overdue'
	PAYMENT_SUSPENDED = 'suspended'
	PAYMENT_STATUS_CHOICES = [
		(PAYMENT_ACTIVE, 'Pagamento em dia'),
		(PAYMENT_OVERDUE, 'Pagamento atrasado'),
		(PAYMENT_SUSPENDED, 'Suspenso por inadimplência'),
	]

	# Basic info
	name = models.CharField(max_length=255)
	responsible_person = models.CharField(
		max_length=255,
		blank=True,
		help_text='Nome do responsável pela empresa'
	)
	phone = models.CharField(
		max_length=20,
		blank=True,
		help_text='Telefone de contato (ex: 55 54 99992-0559)'
	)
	
	# Tax identification
	cnpj = models.CharField(
		max_length=18,
		blank=True,
		help_text='CNPJ da empresa (ex: 00.000.000/0000-00)'
	)
	cpf = models.CharField(
		max_length=14,
		blank=True,
		help_text='CPF do responsável (ex: 000.000.000-00)'
	)
	
	# Address fields
	street = models.CharField(
		max_length=255,
		blank=True,
		help_text='Rua/Avenida'
	)
	number = models.CharField(
		max_length=20,
		blank=True,
		help_text='Número'
	)
	complement = models.CharField(
		max_length=100,
		blank=True,
		help_text='Complemento (apto, sala, etc.)'
	)
	neighborhood = models.CharField(
		max_length=100,
		blank=True,
		help_text='Bairro'
	)
	city = models.CharField(
		max_length=100,
		blank=True,
		help_text='Cidade'
	)
	state = models.CharField(
		max_length=2,
		blank=True,
		help_text='Estado (sigla)'
	)
	postal_code = models.CharField(
		max_length=9,
		blank=True,
		help_text='CEP (ex: 00000-000)'
	)
	
	# Company lifecycle status
	company_type = models.CharField(
		max_length=20, 
		choices=COMPANY_TYPE_CHOICES, 
		default=PROSPECT,
		help_text='Define se a empresa é prospect ou cliente ativo'
	)
	
	# Sales/Contract status
	is_active = models.BooleanField(
		default=False,
		help_text='Indica se a empresa tem contrato ativo (relacionado a vendas)'
	)
	
	# Payment status
	payment_status = models.CharField(
		max_length=20,
		choices=PAYMENT_STATUS_CHOICES,
		default=PAYMENT_ACTIVE,
		help_text='Status do pagamento da empresa'
	)
	
	# Important dates
	activated_at = models.DateTimeField(
		null=True, 
		blank=True,
		help_text='Data de ativação do contrato'
	)
	deactivated_at = models.DateTimeField(
		null=True, 
		blank=True,
		help_text='Data de desativação do contrato'
	)
	payment_suspended_at = models.DateTimeField(
		null=True,
		blank=True,
		help_text='Data de suspensão por inadimplência'
	)
	
	# Notes/Comments
	notes = models.TextField(
		blank=True,
		help_text='Observações sobre a empresa'
	)
	
	# Timestamps
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		db_table = 'surveys_company'

	def __str__(self) -> str:  # type: ignore[override]
		return self.name

	# Helper methods
	def activate(self) -> None:
		"""Activate company contract."""
		self.is_active = True
		self.activated_at = timezone.now()
		self.save(update_fields=['is_active', 'activated_at', 'updated_at'])

	def deactivate(self) -> None:
		"""Deactivate company contract."""
		self.is_active = False
		self.deactivated_at = timezone.now()
		self.save(update_fields=['is_active', 'deactivated_at', 'updated_at'])

	def convert_to_client(self) -> None:
		"""Convert prospect to client."""
		self.company_type = self.CLIENT
		if not self.activated_at:
			self.activated_at = timezone.now()
		self.save(update_fields=['company_type', 'activated_at', 'updated_at'])

	def suspend_for_payment(self) -> None:
		"""Suspend company due to payment issues."""
		self.payment_status = self.PAYMENT_SUSPENDED
		self.payment_suspended_at = timezone.now()
		self.save(update_fields=['payment_status', 'payment_suspended_at', 'updated_at'])

	def restore_payment(self) -> None:
		"""Restore company after payment."""
		self.payment_status = self.PAYMENT_ACTIVE
		self.save(update_fields=['payment_status', 'updated_at'])

	@property
	def is_operational(self) -> bool:
		"""Check if company can operate (active contract and good payment status)."""
		return self.is_active and self.payment_status == self.PAYMENT_ACTIVE

	@property
	def status_display(self) -> str:
		"""Get a human-readable status summary."""
		status_parts = []
		
		# Company type
		status_parts.append(self.get_company_type_display())
		
		# Contract status
		if self.is_active:
			status_parts.append("Contrato ativo")
		else:
			status_parts.append("Contrato inativo")
		
		# Payment status
		if self.payment_status != self.PAYMENT_ACTIVE:
			status_parts.append(self.get_payment_status_display())
		
		return " | ".join(status_parts)

	@property
	def full_address(self) -> str:
		"""Get formatted full address."""
		address_parts = []
		
		if self.street:
			address_parts.append(self.street)
			if self.number:
				address_parts.append(f", {self.number}")
			if self.complement:
				address_parts.append(f" - {self.complement}")
		
		if self.neighborhood:
			if address_parts:
				address_parts.append(f", {self.neighborhood}")
			else:
				address_parts.append(self.neighborhood)
		
		if self.city:
			if address_parts:
				address_parts.append(f", {self.city}")
			else:
				address_parts.append(self.city)
			
			if self.state:
				address_parts.append(f"/{self.state}")
		
		if self.postal_code:
			if address_parts:
				address_parts.append(f" - CEP: {self.postal_code}")
			else:
				address_parts.append(f"CEP: {self.postal_code}")
		
		return "".join(address_parts) if address_parts else "Endereço não informado"

	@property
	def formatted_phone(self) -> str:
		"""Get formatted phone number."""
		if not self.phone:
			return ""
		# Remove non-numeric characters for formatting
		phone_digits = ''.join(filter(str.isdigit, self.phone))
		return self.phone  # Return as-is, user can format as they prefer


class CompanyToken(models.Model):
	company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='api_tokens')
	label = models.CharField(max_length=100, blank=True)
	refresh_jti = models.CharField(max_length=50, db_index=True)
	created_at = models.DateTimeField(auto_now_add=True)
	revoked_at = models.DateTimeField(null=True, blank=True)

	def __str__(self) -> str:  # type: ignore[override]
		status = 'revoked' if self.revoked_at else 'active'
		return f"{self.company.name} - {self.label or self.refresh_jti} ({status})"


class LastContact(models.Model):
	"""Track contact history with prospect companies."""
	company = models.ForeignKey(
		Company, 
		on_delete=models.CASCADE, 
		related_name='contacts',
		limit_choices_to={'company_type': Company.PROSPECT}
	)
	contact_date = models.DateTimeField(
		default=timezone.now,
		help_text='Data e hora do contato'
	)
	notes = models.TextField(
		help_text='Observações sobre o contato realizado'
	)
	created_by = models.ForeignKey(
		'auth.User',
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='company_contacts'
	)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-contact_date', '-created_at']
		verbose_name = 'Último Contato'
		verbose_name_plural = 'Últimos Contatos'

	def __str__(self) -> str:  # type: ignore[override]
		return f"{self.company.name} - {self.contact_date.strftime('%d/%m/%Y %H:%M')}"

