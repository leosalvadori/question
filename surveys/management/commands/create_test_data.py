from django.core.management.base import BaseCommand
from companies.models import Company
from surveys.models import Survey, Question, Option
from django.utils import timezone


class Command(BaseCommand):
    help = 'Create test data for surveys and companies'

    def handle(self, *args, **options):
        self.stdout.write('Creating test data...')
        
        # Create test companies
        companies_data = [
            {'name': 'Empresa Alpha', 'company_type': Company.CLIENT, 'is_active': True},
            {'name': 'Empresa Beta', 'company_type': Company.CLIENT, 'is_active': True},
            {'name': 'Empresa Gamma', 'company_type': Company.PROSPECT, 'is_active': False},
        ]
        
        created_companies = []
        for company_data in companies_data:
            company, created = Company.objects.get_or_create(
                name=company_data['name'],
                defaults=company_data
            )
            if created:
                self.stdout.write(f'Created company: {company.name}')
            created_companies.append(company)
        
        # Create test surveys
        surveys_data = [
            {
                'title': 'Pesquisa de Satisfação Alpha',
                'description': 'Avaliação de satisfação dos clientes da Empresa Alpha',
                'company': created_companies[0]
            },
            {
                'title': 'Pesquisa de Produtos Alpha',
                'description': 'Avaliação dos produtos da Empresa Alpha',
                'company': created_companies[0]
            },
            {
                'title': 'Pesquisa de Serviços Beta',
                'description': 'Avaliação dos serviços da Empresa Beta',
                'company': created_companies[1]
            },
            {
                'title': 'Pesquisa de Mercado Gamma',
                'description': 'Pesquisa de mercado para Empresa Gamma',
                'company': created_companies[2]
            },
        ]
        
        created_surveys = []
        for survey_data in surveys_data:
            survey, created = Survey.objects.get_or_create(
                title=survey_data['title'],
                company=survey_data['company'],
                defaults=survey_data
            )
            if created:
                self.stdout.write(f'Created survey: {survey.title}')
            created_surveys.append(survey)
        
        # Create test questions for each survey
        questions_data = [
            {
                'question_text': 'Como você avalia nosso atendimento?',
                'question_type': Question.SINGLE_CHOICE
            },
            {
                'question_text': 'Quais produtos você mais utiliza?',
                'question_type': Question.MULTIPLE_CHOICE
            },
            {
                'question_text': 'Deixe seu comentário sobre nossos serviços:',
                'question_type': Question.TEXT
            }
        ]
        
        for survey in created_surveys:
            for i, question_data in enumerate(questions_data):
                question, created = Question.objects.get_or_create(
                    survey=survey,
                    question_text=f"{question_data['question_text']} ({survey.company.name})",
                    defaults=question_data
                )
                if created:
                    self.stdout.write(f'Created question: {question.question_text[:50]}...')
                
                # Create options for choice questions
                if question.question_type in [Question.SINGLE_CHOICE, Question.MULTIPLE_CHOICE]:
                    options_text = [
                        'Excelente',
                        'Bom', 
                        'Regular',
                        'Ruim'
                    ]
                    for option_text in options_text:
                        option, created = Option.objects.get_or_create(
                            question=question,
                            option_text=option_text,
                            defaults={'option_type': Option.CHOICE}
                        )
                        if created:
                            self.stdout.write(f'Created option: {option_text}')
        
        self.stdout.write(
            self.style.SUCCESS('Test data created successfully!')
        )
        self.stdout.write(f'Created {len(created_companies)} companies and {len(created_surveys)} surveys')
