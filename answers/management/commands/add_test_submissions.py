import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from surveys.models import Survey, Question, Option
from answers.models import Submission, SubmissionAnswer
from companies.models import Company


class Command(BaseCommand):
    help = 'Add test submissions with Brazilian geographic coordinates'

    def add_arguments(self, parser):
        parser.add_argument(
            '--survey-id',
            type=int,
            help='Survey ID to add submissions to'
        )
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Number of submissions to create (default: 10)'
        )

    def handle(self, *args, **options):
        survey_id = options.get('survey_id')
        count = options['count']

        # Brazilian cities with their coordinates
        brazilian_locations = [
            # Major cities
            {'name': 'São Paulo', 'lat': -23.5505, 'lng': -46.6333},
            {'name': 'Rio de Janeiro', 'lat': -22.9068, 'lng': -43.1729},
            {'name': 'Brasília', 'lat': -15.7801, 'lng': -47.9292},
            {'name': 'Salvador', 'lat': -12.9714, 'lng': -38.5014},
            {'name': 'Fortaleza', 'lat': -3.7172, 'lng': -38.5433},
            {'name': 'Belo Horizonte', 'lat': -19.9167, 'lng': -43.9345},
            {'name': 'Manaus', 'lat': -3.1190, 'lng': -60.0217},
            {'name': 'Curitiba', 'lat': -25.4284, 'lng': -49.2733},
            {'name': 'Recife', 'lat': -8.0476, 'lng': -34.8770},
            {'name': 'Porto Alegre', 'lat': -30.0346, 'lng': -51.2177},
            # Additional cities
            {'name': 'Belém', 'lat': -1.4558, 'lng': -48.4902},
            {'name': 'Goiânia', 'lat': -16.6869, 'lng': -49.2648},
            {'name': 'Guarulhos', 'lat': -23.4538, 'lng': -46.5333},
            {'name': 'Campinas', 'lat': -22.9056, 'lng': -47.0608},
            {'name': 'São Luís', 'lat': -2.5297, 'lng': -44.3028},
            {'name': 'Maceió', 'lat': -9.6658, 'lng': -35.7353},
            {'name': 'Natal', 'lat': -5.7945, 'lng': -35.2110},
            {'name': 'Campo Grande', 'lat': -20.4697, 'lng': -54.6201},
            {'name': 'João Pessoa', 'lat': -7.1195, 'lng': -34.8450},
            {'name': 'Florianópolis', 'lat': -27.5954, 'lng': -48.5480},
        ]

        if survey_id:
            try:
                survey = Survey.objects.get(id=survey_id)
            except Survey.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Survey with ID {survey_id} not found'))
                return
        else:
            # Get the most recent survey
            survey = Survey.objects.order_by('-created_at').first()
            if not survey:
                self.stdout.write(self.style.ERROR('No surveys found in the database'))
                return

        # Get questions for the survey
        questions = Question.objects.filter(survey=survey).order_by('id')
        if not questions:
            self.stdout.write(self.style.ERROR(f'No questions found for survey {survey.id}'))
            return

        # Get or create a test company
        company = survey.company

        self.stdout.write(f'Adding {count} test submissions to survey "{survey.title}" (ID: {survey.id})')

        created_count = 0
        for i in range(count):
            # Select a random location and add some variation
            location = random.choice(brazilian_locations)
            lat_variation = random.uniform(-0.1, 0.1)  # Small variation around the city
            lng_variation = random.uniform(-0.1, 0.1)
            
            # Create submission
            submission = Submission.objects.create(
                survey=survey,
                company=company,
                survey_token=survey.token,
                ip_address=f'192.168.{random.randint(1, 254)}.{random.randint(1, 254)}',
                latitude=Decimal(str(location['lat'] + lat_variation)),
                longitude=Decimal(str(location['lng'] + lng_variation)),
                user_agent='Mozilla/5.0 (Test Bot)',
                occurred_at=timezone.now()
            )

            # Answer questions
            for question in questions:
                if question.question_type in (Question.SINGLE_CHOICE, Question.MULTIPLE_CHOICE):
                    # Get options for this question
                    options = Option.objects.filter(question=question)
                    if options:
                        if question.question_type == Question.SINGLE_CHOICE:
                            # Select one random option
                            selected_option = random.choice(options)
                            SubmissionAnswer.objects.create(
                                submission=submission,
                                question=question,
                                selected_option=selected_option
                            )
                        else:
                            # Select multiple random options
                            num_selections = random.randint(1, min(3, len(options)))
                            selected_options = random.sample(list(options), num_selections)
                            for option in selected_options:
                                SubmissionAnswer.objects.create(
                                    submission=submission,
                                    question=question,
                                    selected_option=option
                                )
                elif question.question_type == Question.SHORT_TEXT:
                    # Generate random text answer
                    SubmissionAnswer.objects.create(
                        submission=submission,
                        question=question,
                        text_response=f'Test answer {i+1} from {location["name"]}'
                    )
                elif question.question_type == Question.LONG_TEXT:
                    # Generate random long text answer
                    SubmissionAnswer.objects.create(
                        submission=submission,
                        question=question,
                        text_response=f'This is a longer test answer {i+1} from {location["name"]}. '
                                    f'The respondent is located at approximately {location["lat"]:.2f}, {location["lng"]:.2f}.'
                    )

            created_count += 1
            self.stdout.write(f'Created submission {created_count}/{count} from {location["name"]}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} test submissions for survey "{survey.title}"'
            )
        )
