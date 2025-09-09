from django import forms
from django.core.exceptions import ValidationError
import re
from .models import Company, Survey, Question, Option


BASE_INPUT_CLASSES = (
	"flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm "
	"ring-offset-background placeholder:text-muted-foreground "
	"focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 "
	"disabled:cursor-not-allowed disabled:opacity-50 transition-all duration-200"
)


class CompanyForm(forms.ModelForm):
	class Meta:
		model = Company
		fields = [
			'name', 'responsible_person', 'phone', 'cnpj', 'cpf',
			'company_type', 'is_active', 'payment_status',
			'street', 'number', 'complement', 'neighborhood', 
			'city', 'state', 'postal_code',
			'notes'
		]
		labels = {
			'name': 'Nome da Empresa',
			'responsible_person': 'Responsável',
			'phone': 'Telefone',
			'cnpj': 'CNPJ',
			'cpf': 'CPF do Responsável',
			'company_type': 'Tipo de Empresa',
			'is_active': 'Contrato Ativo',
			'payment_status': 'Status de Pagamento',
			'street': 'Rua/Avenida',
			'number': 'Número',
			'complement': 'Complemento',
			'neighborhood': 'Bairro',
			'city': 'Cidade',
			'state': 'UF',
			'postal_code': 'CEP',
			'notes': 'Observações',
		}
		widgets = {
			'name': forms.TextInput(attrs={'class': BASE_INPUT_CLASSES, 'placeholder': 'Ex.: ACME Ltda.'}),
			'responsible_person': forms.TextInput(attrs={'class': BASE_INPUT_CLASSES, 'placeholder': 'Nome completo do responsável'}),
			'phone': forms.TextInput(attrs={'class': BASE_INPUT_CLASSES, 'placeholder': 'Ex.: 55 54 99992-0559'}),
			'cnpj': forms.TextInput(attrs={'class': BASE_INPUT_CLASSES, 'placeholder': 'Ex.: 00.000.000/0000-00'}),
			'cpf': forms.TextInput(attrs={'class': BASE_INPUT_CLASSES, 'placeholder': 'Ex.: 000.000.000-00'}),
			'company_type': forms.Select(attrs={'class': BASE_INPUT_CLASSES}),
			'is_active': forms.CheckboxInput(attrs={'class': 'h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary'}),
			'payment_status': forms.Select(attrs={'class': BASE_INPUT_CLASSES}),
			'street': forms.TextInput(attrs={'class': BASE_INPUT_CLASSES, 'placeholder': 'Ex.: Rua das Flores'}),
			'number': forms.TextInput(attrs={'class': BASE_INPUT_CLASSES, 'placeholder': 'Ex.: 123'}),
			'complement': forms.TextInput(attrs={'class': BASE_INPUT_CLASSES, 'placeholder': 'Ex.: Sala 201'}),
			'neighborhood': forms.TextInput(attrs={'class': BASE_INPUT_CLASSES, 'placeholder': 'Ex.: Centro'}),
			'city': forms.TextInput(attrs={'class': BASE_INPUT_CLASSES, 'placeholder': 'Ex.: Porto Alegre'}),
			'state': forms.TextInput(attrs={'class': BASE_INPUT_CLASSES, 'placeholder': 'Ex.: RS', 'maxlength': '2'}),
			'postal_code': forms.TextInput(attrs={'class': BASE_INPUT_CLASSES, 'placeholder': 'Ex.: 00000-000'}),
			'notes': forms.Textarea(attrs={'class': BASE_INPUT_CLASSES, 'rows': 4, 'placeholder': 'Observações sobre a empresa...'}),
		}

	def clean_cnpj(self):
		cnpj = self.cleaned_data.get('cnpj', '')
		if cnpj:
			# Remove formatting
			cnpj_digits = re.sub(r'\D', '', cnpj)
			if len(cnpj_digits) != 14:
				raise ValidationError('CNPJ deve conter 14 dígitos.')
		return cnpj

	def clean_cpf(self):
		cpf = self.cleaned_data.get('cpf', '')
		if cpf:
			# Remove formatting
			cpf_digits = re.sub(r'\D', '', cpf)
			if len(cpf_digits) != 11:
				raise ValidationError('CPF deve conter 11 dígitos.')
		return cpf

	def clean_phone(self):
		phone = self.cleaned_data.get('phone', '')
		if phone:
			# Remove formatting and check length
			phone_digits = re.sub(r'\D', '', phone)
			if len(phone_digits) < 10 or len(phone_digits) > 13:
				raise ValidationError('Telefone inválido. Use o formato: 55 54 99999-9999')
		return phone

	def clean_postal_code(self):
		postal_code = self.cleaned_data.get('postal_code', '')
		if postal_code:
			# Remove formatting
			cep_digits = re.sub(r'\D', '', postal_code)
			if len(cep_digits) != 8:
				raise ValidationError('CEP deve conter 8 dígitos.')
		return postal_code

	def clean_state(self):
		state = self.cleaned_data.get('state', '')
		if state:
			state = state.upper()
			if len(state) != 2:
				raise ValidationError('Estado deve ser a sigla com 2 letras (ex: RS).')
		return state


class SurveyForm(forms.ModelForm):
	class Meta:
		model = Survey
		fields = ['company', 'title', 'description']
		labels = {
			'company': 'Empresa',
			'title': 'Título da Pesquisa',
			'description': 'Descrição',
		}
		widgets = {
			'company': forms.Select(attrs={'class': BASE_INPUT_CLASSES}),
			'title': forms.TextInput(attrs={'class': BASE_INPUT_CLASSES, 'placeholder': 'Ex.: Satisfação do Cliente 2025'}),
			'description': forms.Textarea(attrs={'class': BASE_INPUT_CLASSES, 'rows': 4, 'placeholder': 'Objetivo e escopo da pesquisa...'}),
		}


class QuestionForm(forms.ModelForm):
	class Meta:
		model = Question
		fields = ['survey', 'question_text', 'question_type']
		labels = {
			'survey': 'Pesquisa',
			'question_text': 'Pergunta',
			'question_type': 'Tipo da Pergunta',
		}
		widgets = {
			'survey': forms.Select(attrs={'class': BASE_INPUT_CLASSES}),
			'question_text': forms.Textarea(attrs={'class': BASE_INPUT_CLASSES, 'rows': 3, 'placeholder': 'Digite o enunciado da pergunta'}),
			'question_type': forms.Select(attrs={'class': BASE_INPUT_CLASSES}),
		}


class OptionForm(forms.ModelForm):
	class Meta:
		model = Option
		fields = ['question', 'option_text', 'option_type']
		labels = {
			'question': 'Pergunta',
			'option_text': 'Texto da Opção',
			'option_type': 'Tipo da Opção',
		}
		widgets = {
			'question': forms.Select(attrs={'class': BASE_INPUT_CLASSES}),
			'option_text': forms.Textarea(attrs={'class': BASE_INPUT_CLASSES, 'rows': 2, 'placeholder': 'Digite o texto da opção (quando aplicável)'}),
			'option_type': forms.Select(attrs={'class': BASE_INPUT_CLASSES}),
		}

