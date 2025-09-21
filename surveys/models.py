from django.db import models
from django.utils.crypto import get_random_string
from companies.models import Company


class Survey(models.Model):
	company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='surveys')
	title = models.CharField(max_length=255)
	description = models.TextField(blank=True)
	token = models.CharField(max_length=20, unique=True, db_index=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self) -> str:
		return self.title

	def save(self, *args, **kwargs):  # type: ignore[no-untyped-def]
		# Generate a mobile-friendly unique token on first creation
		if not self.token and self.company_id:
			# Exclude easily confusable characters
			allowed_chars = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789'
			while True:
				random_part = get_random_string(6, allowed_chars)
				token_candidate = f"{self.company_id}-{random_part}"
				if not Survey.objects.filter(token=token_candidate).exists():
					self.token = token_candidate
					break
		return super().save(*args, **kwargs)


class Question(models.Model):
	TEXT = 'text'
	SINGLE_CHOICE = 'single_choice'
	MULTIPLE_CHOICE = 'multiple_choice'
	QUESTION_TYPES = [
		(TEXT, 'Texto'),
		(SINGLE_CHOICE, 'Escolha única'),
		(MULTIPLE_CHOICE, 'Múltiplas escolhas'),
	]

	survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='questions')
	question_text = models.TextField()
	question_type = models.CharField(max_length=32, choices=QUESTION_TYPES, default=TEXT)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self) -> str:
		return f"{self.survey.title} - {self.question_text[:30]}"


class Option(models.Model):
	CHOICE = 'choice'
	TEXT = 'text'
	OPTION_TYPES = [
		(CHOICE, 'Opção'),
		(TEXT, 'Texto'),
	]

	question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
	option_text = models.TextField(null=True, blank=True)
	option_type = models.CharField(max_length=16, choices=OPTION_TYPES, default=CHOICE)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self) -> str:
		prefix = 'TXT' if self.option_type == self.TEXT else 'OPT'
		return f"{prefix}: {self.option_text if self.option_text else '—'}"

