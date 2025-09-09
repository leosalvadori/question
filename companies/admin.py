from django.contrib import admin
from django.utils.html import format_html
from .models import Company, CompanyToken, LastContact


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
	list_display = (
		'id', 
		'name',
		'responsible_person',
		'phone',
		'company_type_badge',
		'is_active_badge',
		'payment_status_badge',
		'created_at', 
	)
	list_filter = (
		'company_type',
		'is_active',
		'payment_status',
		'state',
		'city',
		'created_at',
	)
	search_fields = ('name', 'responsible_person', 'cnpj', 'cpf', 'phone', 'city')
	readonly_fields = (
		'created_at', 
		'updated_at',
		'activated_at',
		'deactivated_at',
		'payment_suspended_at',
		'status_display',
		'full_address'
	)
	
	fieldsets = (
		('Informações Básicas', {
			'fields': ('name', 'responsible_person', 'phone', 'company_type')
		}),
		('Documentos', {
			'fields': ('cnpj', 'cpf')
		}),
		('Endereço', {
			'fields': ('street', 'number', 'complement', 'neighborhood', 'city', 'state', 'postal_code', 'full_address'),
			'classes': ('collapse',)
		}),
		('Status de Vendas/Contrato', {
			'fields': ('is_active', 'activated_at', 'deactivated_at')
		}),
		('Status de Pagamento', {
			'fields': ('payment_status', 'payment_suspended_at')
		}),
		('Observações', {
			'fields': ('notes',),
			'classes': ('collapse',)
		}),
		('Informações do Sistema', {
			'fields': ('status_display', 'created_at', 'updated_at'),
			'classes': ('collapse',)
		}),
	)
	
	# Actions for quick status changes
	actions = [
		'activate_companies',
		'deactivate_companies',
		'convert_to_clients',
		'suspend_for_payment',
		'restore_payment'
	]
	
	def company_type_badge(self, obj):
		colors = {
			Company.PROSPECT: 'orange',
			Company.CLIENT: 'green',
		}
		color = colors.get(obj.company_type, 'gray')
		return format_html(
			'<span style="background-color: {}; color: white; padding: 3px 10px; '
			'border-radius: 3px; font-size: 11px;">{}</span>',
			color,
			obj.get_company_type_display()
		)
	company_type_badge.short_description = 'Tipo'
	
	def is_active_badge(self, obj):
		if obj.is_active:
			return format_html(
				'<span style="color: green;">✓ Ativo</span>'
			)
		return format_html(
			'<span style="color: red;">✗ Inativo</span>'
		)
	is_active_badge.short_description = 'Contrato'
	
	def payment_status_badge(self, obj):
		colors = {
			Company.PAYMENT_ACTIVE: 'green',
			Company.PAYMENT_OVERDUE: 'orange',
			Company.PAYMENT_SUSPENDED: 'red',
		}
		color = colors.get(obj.payment_status, 'gray')
		return format_html(
			'<span style="color: {};">{}</span>',
			color,
			obj.get_payment_status_display()
		)
	payment_status_badge.short_description = 'Pagamento'
	
	# Admin actions
	def activate_companies(self, request, queryset):
		for company in queryset:
			company.activate()
		self.message_user(request, f"{queryset.count()} empresa(s) ativada(s).")
	activate_companies.short_description = "Ativar contratos selecionados"
	
	def deactivate_companies(self, request, queryset):
		for company in queryset:
			company.deactivate()
		self.message_user(request, f"{queryset.count()} empresa(s) desativada(s).")
	deactivate_companies.short_description = "Desativar contratos selecionados"
	
	def convert_to_clients(self, request, queryset):
		prospects = queryset.filter(company_type=Company.PROSPECT)
		for company in prospects:
			company.convert_to_client()
		self.message_user(request, f"{prospects.count()} prospect(s) convertido(s) para cliente.")
	convert_to_clients.short_description = "Converter prospects para clientes"
	
	def suspend_for_payment(self, request, queryset):
		for company in queryset:
			company.suspend_for_payment()
		self.message_user(request, f"{queryset.count()} empresa(s) suspensa(s) por inadimplência.")
	suspend_for_payment.short_description = "Suspender por inadimplência"
	
	def restore_payment(self, request, queryset):
		for company in queryset:
			company.restore_payment()
		self.message_user(request, f"{queryset.count()} empresa(s) restaurada(s) após pagamento.")
	restore_payment.short_description = "Restaurar após pagamento"


@admin.register(CompanyToken)
class CompanyTokenAdmin(admin.ModelAdmin):
	list_display = ('id', 'company', 'label', 'refresh_jti', 'created_at', 'revoked_at')
	list_filter = ('company', 'revoked_at')
	search_fields = ('label', 'refresh_jti')


@admin.register(LastContact)
class LastContactAdmin(admin.ModelAdmin):
	list_display = ('id', 'company', 'contact_date', 'created_by', 'created_at')
	list_filter = ('contact_date', 'created_by', 'company')
	search_fields = ('company__name', 'notes')
	readonly_fields = ('created_by', 'created_at', 'updated_at')
	
	fieldsets = (
		('Informações do Contato', {
			'fields': ('company', 'contact_date', 'notes')
		}),
		('Informações do Sistema', {
			'fields': ('created_by', 'created_at', 'updated_at'),
			'classes': ('collapse',)
		}),
	)
	
	def save_model(self, request, obj, form, change):
		if not change:  # Creating new object
			obj.created_by = request.user
		super().save_model(request, obj, form, change)

