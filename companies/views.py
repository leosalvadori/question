from datetime import timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.db.models import Q

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import Company, CompanyToken, LastContact


@login_required
def company_tokens(request, pk: int):
	company = get_object_or_404(Company, pk=pk)
	# Ordenar tokens: ativos e válidos primeiro, depois revogados, depois expirados
	from django.utils import timezone
	now = timezone.now()
	
	tokens = company.api_tokens.annotate(
		is_active=~Q(revoked_at__isnull=False),
		is_valid=Q(expires_at__gt=now) | Q(expires_at__isnull=True)
	).order_by(
		'-is_active',  # Ativos primeiro (True antes de False)
		'-is_valid',   # Válidos primeiro (True antes de False)
		'-created_at'  # Mais recentes primeiro dentro de cada grupo
	)
	
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
		
		# Store both tokens for display and refresh purposes
		access_token_str = str(access)
		refresh_token_str = str(refresh)
		
		# Calculate expiration time (1 day from now, matching SIMPLE_JWT settings)
		expires_at = timezone.now() + timedelta(days=1)
		
		CompanyToken.objects.create(
			company=company, 
			label=label, 
			refresh_jti=str(access['jti']),  # Usar JTI do access token, não do refresh
			access_token=access_token_str,
			refresh_token=refresh_token_str,
			expires_at=expires_at
		)
		return render(request, 'companies/company_token_created.html', {
			'company': company,
			'access_token': access_token_str,
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


@extend_schema(
	summary="Refresh Access Token",
	description="Refresh access token using refresh token from request body.",
	request={
		'application/json': {
			'type': 'object',
			'properties': {
				'refresh': {
					'type': 'string',
					'description': 'The refresh token to use for generating a new access token',
					'example': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'
				}
			},
			'required': ['refresh']
		}
	},
	responses={
		200: {
			'description': 'Token refreshed successfully',
			'content': {
				'application/json': {
					'type': 'object',
					'properties': {
						'access_token': {
							'type': 'string',
							'description': 'New access token',
							'example': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'
						},
						'expires_at': {
							'type': 'string',
							'format': 'date-time',
							'description': 'Token expiration time',
							'example': '2024-01-15T10:30:00.000Z'
						},
						'message': {
							'type': 'string',
							'description': 'Success message',
							'example': 'Token refreshed successfully'
						}
					}
				}
			}
		},
		400: {
			'description': 'Bad request - Invalid or missing refresh token',
			'content': {
				'application/json': {
					'type': 'object',
					'properties': {
						'error': {
							'type': 'string',
							'description': 'Error message',
							'example': 'Refresh token is required'
						}
					}
				}
			}
		},
		404: {
			'description': 'Token not found or has been revoked',
			'content': {
				'application/json': {
					'type': 'object',
					'properties': {
						'error': {
							'type': 'string',
							'description': 'Error message',
							'example': 'Token not found or has been revoked'
						}
					}
				}
			}
		}
	}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
	"""
	Refresh access token using refresh token from request body.
	This is the standard JWT approach for mobile apps.
	"""
	try:
		refresh_token_str = request.data.get('refresh')
		
		if not refresh_token_str:
			return Response(
				{'error': 'Refresh token is required'}, 
				status=status.HTTP_400_BAD_REQUEST
			)
		
		# Validate the refresh token
		refresh = RefreshToken(refresh_token_str)
		
		# Extract company_id from the refresh token
		company_id = refresh.get('company_id')
		if not company_id:
			return Response(
				{'error': 'Invalid refresh token: no company_id found'}, 
				status=status.HTTP_400_BAD_REQUEST
			)
		
		# Find the corresponding CompanyToken
		try:
			company_token = CompanyToken.objects.get(
				company_id=company_id,
				refresh_token=refresh_token_str,
				revoked_at__isnull=True
			)
		except CompanyToken.DoesNotExist:
			return Response(
				{'error': 'Token not found or has been revoked'}, 
				status=status.HTTP_404_NOT_FOUND
			)
		
		# Generate new access token
		new_access = refresh.access_token
		new_access['company_id'] = company_id
		
		# Update the access token in database
		company_token.access_token = str(new_access)
		company_token.expires_at = timezone.now() + timedelta(days=1)
		company_token.save()
		
		return Response({
			'access_token': str(new_access),
			'expires_at': company_token.expires_at.isoformat(),
			'message': 'Token refreshed successfully'
		})
		
	except TokenError as e:
		return Response(
			{'error': f'Invalid refresh token: {str(e)}'}, 
			status=status.HTTP_400_BAD_REQUEST
		)
	except Exception as e:
		return Response(
			{'error': f'Unexpected error: {str(e)}'}, 
			status=status.HTTP_500_INTERNAL_SERVER_ERROR
		)


