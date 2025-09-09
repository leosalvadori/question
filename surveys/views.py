from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from companies.models import Company
from django.core.paginator import Paginator
from .models import Survey, Question, Option
from .forms import CompanyForm, SurveyForm, QuestionForm, OptionForm
from .serializers import SurveyDetailSerializer

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from .schema import get_survey_by_token_schema
from answers.serializers import SubmissionCreateSerializer


# Companies
@login_required
def company_list(request):
	companies_qs = Company.objects.all()
	
	# Filtering
	company_type = request.GET.get('company_type')
	is_active = request.GET.get('is_active')
	payment_status = request.GET.get('payment_status')
	
	if company_type:
		companies_qs = companies_qs.filter(company_type=company_type)
	
	if is_active:
		companies_qs = companies_qs.filter(is_active=is_active == 'true')
	
	if payment_status:
		companies_qs = companies_qs.filter(payment_status=payment_status)
	
	companies_qs = companies_qs.order_by('name')
	
	page_size = int(request.GET.get('page_size') or 15)
	paginator = Paginator(companies_qs, page_size)
	page = request.GET.get('page')
	companies = paginator.get_page(page)
	
	context = {
		'companies': companies,
		'page_obj': companies,
		'page_size': page_size,
		'company_type': company_type,
		'is_active': is_active,
		'payment_status': payment_status,
		'company_types': Company.COMPANY_TYPE_CHOICES,
		'payment_statuses': Company.PAYMENT_STATUS_CHOICES,
	}
	
	return render(request, 'surveys/company_list.html', context)


@login_required
def company_prospects(request):
	companies_qs = Company.objects.filter(company_type=Company.PROSPECT)
	
	# Additional filtering
	is_active = request.GET.get('is_active')
	payment_status = request.GET.get('payment_status')
	
	if is_active:
		companies_qs = companies_qs.filter(is_active=is_active == 'true')
	
	if payment_status:
		companies_qs = companies_qs.filter(payment_status=payment_status)
	
	companies_qs = companies_qs.order_by('name')
	
	# Annotate with contact count for prospects
	from django.db.models import Count
	companies_qs = companies_qs.annotate(contact_count=Count('contacts'))
	
	page_size = int(request.GET.get('page_size') or 15)
	paginator = Paginator(companies_qs, page_size)
	page = request.GET.get('page')
	companies = paginator.get_page(page)
	
	context = {
		'companies': companies,
		'page_obj': companies,
		'page_size': page_size,
		'is_active': is_active,
		'payment_status': payment_status,
		'payment_statuses': Company.PAYMENT_STATUS_CHOICES,
		'page_title': 'Prospects',
		'filter_type': 'prospects',
	}
	
	return render(request, 'surveys/company_list.html', context)


@login_required
def company_clients(request):
	companies_qs = Company.objects.filter(company_type=Company.CLIENT)
	
	# Additional filtering
	is_active = request.GET.get('is_active')
	payment_status = request.GET.get('payment_status')
	
	if is_active:
		companies_qs = companies_qs.filter(is_active=is_active == 'true')
	
	if payment_status:
		companies_qs = companies_qs.filter(payment_status=payment_status)
	
	companies_qs = companies_qs.order_by('name')
	
	page_size = int(request.GET.get('page_size') or 15)
	paginator = Paginator(companies_qs, page_size)
	page = request.GET.get('page')
	companies = paginator.get_page(page)
	
	context = {
		'companies': companies,
		'page_obj': companies,
		'page_size': page_size,
		'is_active': is_active,
		'payment_status': payment_status,
		'payment_statuses': Company.PAYMENT_STATUS_CHOICES,
		'page_title': 'Clientes Operando',
		'filter_type': 'clients',
	}
	
	return render(request, 'surveys/company_list.html', context)


@login_required
def company_create(request):
	if request.method == 'POST':
		form = CompanyForm(request.POST)
		if form.is_valid():
			company = form.save()
			return redirect('company_detail', pk=company.pk)
	else:
		form = CompanyForm()
	return render(request, 'surveys/company_form.html', {'form': form})


@login_required
def company_detail(request, pk: int):
	company = get_object_or_404(Company, pk=pk)
	surveys_qs = company.surveys.all().order_by('-created_at')
	page_size = int(request.GET.get('page_size') or 15)
	paginator = Paginator(surveys_qs, page_size)
	page = request.GET.get('page')
	surveys = paginator.get_page(page)
	return render(request, 'surveys/company_detail.html', {'company': company, 'surveys': surveys, 'page_obj': surveys, 'page_size': page_size})


@login_required
def company_update(request, pk: int):
	company = get_object_or_404(Company, pk=pk)
	if request.method == 'POST':
		form = CompanyForm(request.POST, instance=company)
		if form.is_valid():
			form.save()
			return redirect('company_detail', pk=company.pk)
	else:
		form = CompanyForm(instance=company)
	return render(request, 'surveys/company_form.html', {'form': form, 'company': company})


@login_required
def company_delete(request, pk: int):
	company = get_object_or_404(Company, pk=pk)
	if request.method == 'POST':
		company.delete()
		return redirect('company_list')
	return render(request, 'surveys/confirm_delete.html', {
		'object': company,
		'entity': 'empresa',
		'cancel_url': reverse('company_detail', args=[company.pk])
	})


# Surveys
@login_required
def survey_list(request):
	surveys_qs = Survey.objects.select_related('company').order_by('-created_at')
	page_size = int(request.GET.get('page_size') or 15)
	paginator = Paginator(surveys_qs, page_size)
	page = request.GET.get('page')
	surveys = paginator.get_page(page)
	return render(request, 'surveys/survey_list.html', {'surveys': surveys, 'page_obj': surveys, 'page_size': page_size})


@login_required
def survey_create(request):
	if request.method == 'POST':
		form = SurveyForm(request.POST)
		if form.is_valid():
			survey = form.save()
			return redirect('survey_detail', pk=survey.pk)
	else:
		form = SurveyForm()
	return render(request, 'surveys/survey_form.html', {'form': form})


@login_required
def survey_detail(request, pk: int):
	survey = get_object_or_404(Survey, pk=pk)
	questions = survey.questions.all().prefetch_related('options')
	return render(request, 'surveys/survey_detail.html', {'survey': survey, 'questions': questions})


@login_required
def survey_update(request, pk: int):
	survey = get_object_or_404(Survey, pk=pk)
	if request.method == 'POST':
		form = SurveyForm(request.POST, instance=survey)
		if form.is_valid():
			form.save()
			return redirect('survey_detail', pk=survey.pk)
	else:
		form = SurveyForm(instance=survey)
	return render(request, 'surveys/survey_form.html', {'form': form, 'survey': survey})


@login_required
def survey_delete(request, pk: int):
	survey = get_object_or_404(Survey, pk=pk)
	if request.method == 'POST':
		survey.delete()
		return redirect('survey_list')
	return render(request, 'surveys/confirm_delete.html', {
		'object': survey,
		'entity': 'pesquisa',
		'cancel_url': reverse('survey_detail', args=[survey.pk])
	})


# Questions
@login_required
def question_create(request, survey_id: int):
	survey = get_object_or_404(Survey, pk=survey_id)
	if request.method == 'POST':
		form = QuestionForm(request.POST)
		if form.is_valid():
			question = form.save()
			return redirect('survey_detail', pk=question.survey_id)
	else:
		form = QuestionForm(initial={'survey': survey})
	return render(request, 'surveys/question_form.html', {'form': form, 'survey': survey})


@login_required
def question_update(request, pk: int):
	question = get_object_or_404(Question, pk=pk)
	if request.method == 'POST':
		form = QuestionForm(request.POST, instance=question)
		if form.is_valid():
			form.save()
			return redirect('survey_detail', pk=question.survey_id)
	else:
		form = QuestionForm(instance=question)
	return render(request, 'surveys/question_form.html', {'form': form, 'question': question})


@login_required
def question_delete(request, pk: int):
	question = get_object_or_404(Question, pk=pk)
	if request.method == 'POST':
		parent_survey_id = question.survey_id
		question.delete()
		return redirect('survey_detail', pk=parent_survey_id)
	return render(request, 'surveys/confirm_delete.html', {
		'object': question,
		'entity': 'pergunta',
		'cancel_url': reverse('survey_detail', args=[question.survey_id])
	})


# Options
@login_required
def option_create(request, question_id: int):
	question = get_object_or_404(Question, pk=question_id)
	if request.method == 'POST':
		form = OptionForm(request.POST)
		if form.is_valid():
			option = form.save()
			return redirect('survey_detail', pk=option.question.survey_id)
	else:
		form = OptionForm(initial={'question': question})
	return render(request, 'surveys/option_form.html', {'form': form, 'question': question})


@login_required
def option_update(request, pk: int):
	option = get_object_or_404(Option, pk=pk)
	if request.method == 'POST':
		form = OptionForm(request.POST, instance=option)
		if form.is_valid():
			form.save()
			return redirect('survey_detail', pk=option.question.survey_id)
	else:
		form = OptionForm(instance=option)
	return render(request, 'surveys/option_form.html', {'form': form, 'option': option})


@login_required
def option_delete(request, pk: int):
	option = get_object_or_404(Option, pk=pk)
	if request.method == 'POST':
		parent_survey_id = option.question.survey_id
		option.delete()
		return redirect('survey_detail', pk=parent_survey_id)
	return render(request, 'surveys/confirm_delete.html', {
		'object': option,
		'entity': 'opção',
		'cancel_url': reverse('survey_detail', args=[option.question.survey_id])
	})


# ---------------------- Preview (public, no bearer) ----------------------

def survey_preview_start(request):
	"""Simple page to enter a Survey TOKEN and go to preview."""
	if request.method == 'POST':
		token = (request.POST.get('token') or '').strip()
		if token:
			return redirect('survey_preview', token=token)
		return render(request, 'surveys/preview_start.html', {'error': 'Informe um token válido.'})
	return render(request, 'surveys/preview_start.html')


def survey_preview(request, token: str):
	survey = Survey.objects.filter(token=token).prefetch_related('questions__options', 'company').first()
	if not survey:
		return render(request, 'surveys/preview_start.html', {'error': 'Pesquisa não encontrada para este token.'})

	if request.method == 'POST':
		# Build serializer payload to share the exact creation logic with API
		answers_payload = []
		for q in survey.questions.all():
			if q.question_type == Question.MULTIPLE_CHOICE:
				selected_ids = request.POST.getlist(f'question_{q.id}')
				if selected_ids:
					try:
						ids = [int(v) for v in selected_ids]
					except ValueError:
						ids = []
					if ids:
						answers_payload.append({'question_id': q.id, 'option_ids': ids})
			elif q.question_type == Question.SINGLE_CHOICE:
				selected = request.POST.get(f'question_{q.id}')
				if selected:
					try:
						answers_payload.append({'question_id': q.id, 'option_id': int(selected)})
					except ValueError:
						pass
			else:
				text_value = (request.POST.get(f'text_{q.id}') or '').strip()
				answers_payload.append({'question_id': q.id, 'text_response': text_value})

		payload = {
			'token': token,
			'occurred_at': request.POST.get('occurred_at') or None,
			'latitude': request.POST.get('latitude') or None,
			'longitude': request.POST.get('longitude') or None,
			'answers': answers_payload,
		}

		serializer = SubmissionCreateSerializer(data=payload, context={'request': request})
		if serializer.is_valid():
			serializer.save()
			return redirect('survey_preview_success', token=token)
		# On error, re-render with errors
		return render(request, 'surveys/preview_form.html', {
			'survey': survey,
			'token': token,
			'errors': serializer.errors,
		})

	return render(request, 'surveys/preview_form.html', {'survey': survey, 'token': token})


def survey_preview_success(request, token: str):
	return render(request, 'surveys/preview_success.html', {'token': token})


# ---------------------- API ----------------------


@get_survey_by_token_schema
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_survey_detail(request): 
	token = request.GET.get('token')
	if not token:
		return Response({'detail': 'token ausente'}, status=status.HTTP_400_BAD_REQUEST)
	survey = Survey.objects.filter(token=token).prefetch_related('questions__options', 'company').first()
	if not survey:
		return Response({'detail': 'pesquisa não encontrada'}, status=status.HTTP_404_NOT_FOUND)
	data = SurveyDetailSerializer(survey).data
	return Response(data)

