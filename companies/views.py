from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Company, LastContact, CompanyAPIAccount


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

# ==================== API Accounts Management ====================

@login_required
def company_accounts(request, pk: int):
	"""List all API accounts for a company."""
	company = get_object_or_404(Company, pk=pk)
	accounts = company.api_accounts.all()
	
	context = {
		'company': company,
		'accounts': accounts,
	}
	
	return render(request, 'companies/company_accounts.html', context)


@login_required
def company_account_create(request, pk: int):
	"""Create new API account for a company."""
	company = get_object_or_404(Company, pk=pk)
	
	if request.method == 'POST':
		username = request.POST.get('username', '').strip()
		password = request.POST.get('password', '').strip()
		label = request.POST.get('label', '').strip()
		
		# Validation
		if not username or not password:
			messages.error(request, 'Username e senha são obrigatórios')
			return render(request, 'companies/company_account_form.html', {
				'company': company,
				'username': username,
				'label': label,
			})
		
		if len(password) < 8:
			messages.error(request, 'A senha deve ter pelo menos 8 caracteres')
			return render(request, 'companies/company_account_form.html', {
				'company': company,
				'username': username,
				'label': label,
			})
		
		if CompanyAPIAccount.objects.filter(username=username).exists():
			messages.error(request, 'Username já existe. Escolha outro.')
			return render(request, 'companies/company_account_form.html', {
				'company': company,
				'label': label,
			})
		
		# Create account with hashed password
		from django.contrib.auth.hashers import make_password
		account = CompanyAPIAccount.objects.create(
			company=company,
			username=username,
			password=make_password(password),
			label=label
		)
		
		messages.success(request, f'Conta "{username}" criada com sucesso!')
		return redirect('company_accounts', pk=pk)
	
	return render(request, 'companies/company_account_form.html', {'company': company})


@login_required
def company_account_deactivate(request, pk: int, account_id: int):
	"""Deactivate an API account."""
	company = get_object_or_404(Company, pk=pk)
	account = get_object_or_404(CompanyAPIAccount, pk=account_id, company=company)
	
	if request.method == 'POST':
		account.deactivate()
		messages.warning(request, f'Conta "{account.username}" foi desativada')
		return redirect('company_accounts', pk=pk)
	
	context = {
		'company': company,
		'account': account,
		'action': 'deactivate',
	}
	return render(request, 'companies/company_account_confirm.html', context)


@login_required
def company_account_activate(request, pk: int, account_id: int):
	"""Reactivate an API account."""
	company = get_object_or_404(Company, pk=pk)
	account = get_object_or_404(CompanyAPIAccount, pk=account_id, company=company)
	
	if request.method == 'POST':
		account.activate()
		messages.success(request, f'Conta "{account.username}" foi reativada')
		return redirect('company_accounts', pk=pk)
	
	# No need for confirmation page, just redirect back
	return redirect('company_accounts', pk=pk)


@login_required
def company_account_delete(request, pk: int, account_id: int):
	"""Delete an API account permanently."""
	company = get_object_or_404(Company, pk=pk)
	account = get_object_or_404(CompanyAPIAccount, pk=account_id, company=company)
	
	if request.method == 'POST':
		username = account.username
		account.delete()
		messages.success(request, f'Conta "{username}" foi deletada permanentemente')
		return redirect('company_accounts', pk=pk)
	
	context = {
		'company': company,
		'account': account,
		'action': 'delete',
	}
	return render(request, 'companies/company_account_confirm.html', context)


