from datetime import timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from rest_framework_simplejwt.tokens import RefreshToken

from .models import Company, CompanyToken, LastContact


@login_required
def company_tokens(request, pk: int):
	company = get_object_or_404(Company, pk=pk)
	tokens = company.api_tokens.order_by('-created_at')
	return render(request, 'companies/company_tokens.html', {'company': company, 'tokens': tokens})


@login_required
def company_token_create(request, pk: int):
	company = get_object_or_404(Company, pk=pk)
	if request.method == 'POST':
		label = request.POST.get('label', '').strip()
		# Create Refresh + Access (we'll present both; store refresh JTI for revoke)
		refresh = RefreshToken.for_user(request.user)
		refresh['company_id'] = company.pk
		access = refresh.access_token
		access['company_id'] = company.pk
		CompanyToken.objects.create(company=company, label=label, refresh_jti=str(refresh['jti']))
		return render(request, 'companies/company_token_created.html', {
			'company': company,
			'access_token': str(access),
			'refresh_token': str(refresh),
		})
	return redirect('company_tokens', pk=company.pk)


@login_required
def company_token_revoke(request, pk: int, token_id: int):
	company = get_object_or_404(Company, pk=pk)
	token = get_object_or_404(CompanyToken, pk=token_id, company=company)
	if request.method == 'POST':
		token.revoked_at = timezone.now()
		token.save(update_fields=['revoked_at'])
		return redirect('company_tokens', pk=company.pk)
	return render(request, 'companies/confirm_revoke.html', {'company': company, 'token': token})


# Status management views
@login_required
def company_activate(request, pk: int):
	company = get_object_or_404(Company, pk=pk)
	if request.method == 'POST':
		company.activate()
		messages.success(request, f'Contrato da empresa {company.name} foi ativado.')
		return redirect('company_detail', pk=company.pk)
	return redirect('company_detail', pk=company.pk)


@login_required
def company_deactivate(request, pk: int):
	company = get_object_or_404(Company, pk=pk)
	if request.method == 'POST':
		company.deactivate()
		messages.warning(request, f'Contrato da empresa {company.name} foi desativado.')
		return redirect('company_detail', pk=company.pk)
	return redirect('company_detail', pk=company.pk)


@login_required
def company_convert_to_client(request, pk: int):
	company = get_object_or_404(Company, pk=pk)
	if request.method == 'POST':
		if company.company_type == Company.PROSPECT:
			company.convert_to_client()
			messages.success(request, f'{company.name} foi convertida de prospect para cliente.')
		else:
			messages.info(request, f'{company.name} já é um cliente.')
		return redirect('company_detail', pk=company.pk)
	return redirect('company_detail', pk=company.pk)


@login_required
def company_suspend_payment(request, pk: int):
	company = get_object_or_404(Company, pk=pk)
	if request.method == 'POST':
		company.suspend_for_payment()
		messages.error(request, f'{company.name} foi suspensa por inadimplência.')
		return redirect('company_detail', pk=company.pk)
	return redirect('company_detail', pk=company.pk)


@login_required
def company_restore_payment(request, pk: int):
	company = get_object_or_404(Company, pk=pk)
	if request.method == 'POST':
		company.restore_payment()
		messages.success(request, f'Status de pagamento de {company.name} foi restaurado.')
		return redirect('company_detail', pk=company.pk)
	return redirect('company_detail', pk=company.pk)


# Contact History Views
@login_required
def company_contacts(request, pk: int):
	company = get_object_or_404(Company, pk=pk)
	
	# Check if company is a prospect
	if company.company_type != Company.PROSPECT:
		messages.warning(request, 'Histórico de contatos está disponível apenas para prospects.')
		return redirect('company_detail', pk=company.pk)
	
	contacts = company.contacts.all()
	
	context = {
		'company': company,
		'contacts': contacts,
	}
	
	return render(request, 'companies/company_contacts.html', context)


@login_required
def company_contact_create(request, pk: int):
	company = get_object_or_404(Company, pk=pk)
	
	# Check if company is a prospect
	if company.company_type != Company.PROSPECT:
		messages.warning(request, 'Histórico de contatos está disponível apenas para prospects.')
		return redirect('company_detail', pk=company.pk)
	
	if request.method == 'POST':
		notes = request.POST.get('notes', '').strip()
		contact_date = request.POST.get('contact_date')
		
		if notes:
			contact = LastContact.objects.create(
				company=company,
				notes=notes,
				created_by=request.user
			)
			
			# If custom date provided
			if contact_date:
				try:
					from datetime import datetime
					# Parse the datetime-local input
					parsed_date = datetime.strptime(contact_date, '%Y-%m-%dT%H:%M')
					# Make it timezone-aware
					contact.contact_date = timezone.make_aware(parsed_date, timezone.get_current_timezone())
					contact.save()
				except:
					pass
			
			messages.success(request, 'Contato registrado com sucesso.')
			return redirect('company_contacts', pk=company.pk)
		else:
			messages.error(request, 'Por favor, adicione observações sobre o contato.')
	
	return render(request, 'companies/company_contact_form.html', {'company': company})


@login_required
def company_contact_delete(request, pk: int, contact_id: int):
	company = get_object_or_404(Company, pk=pk)
	contact = get_object_or_404(LastContact, pk=contact_id, company=company)
	
	if request.method == 'POST':
		contact.delete()
		messages.success(request, 'Registro de contato excluído.')
		return redirect('company_contacts', pk=company.pk)
	
	context = {
		'company': company,
		'contact': contact,
	}
	
	return render(request, 'companies/contact_confirm_delete.html', context)


