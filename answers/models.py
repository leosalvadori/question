from django.db import models
from django.utils import timezone

from companies.models import Company
from surveys.models import Survey, Question, Option


class State(models.Model):
    """Brazilian states/UF data."""
    
    code = models.CharField(max_length=2, unique=True, db_index=True)
    uf = models.CharField(max_length=2, unique=True, db_index=True)
    name = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=10, decimal_places=6)
    longitude = models.DecimalField(max_digits=10, decimal_places=6)
    region = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'answers_state'
        indexes = [
            models.Index(fields=['region']),
            models.Index(fields=['uf']),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.uf})"


class City(models.Model):
    """Brazilian cities/municipalities data."""
    
    ibge_code = models.CharField(max_length=7, unique=True, db_index=True)
    name = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=10, decimal_places=6)
    longitude = models.DecimalField(max_digits=10, decimal_places=6)
    is_capital = models.BooleanField(default=False)
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='cities')
    siafi_id = models.CharField(max_length=4, blank=True)
    area_code = models.CharField(max_length=2, blank=True)
    timezone = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'answers_city'
        indexes = [
            models.Index(fields=['state']),
            models.Index(fields=['ibge_code']),
            models.Index(fields=['is_capital']),
        ]

    def __str__(self) -> str:
        return f"{self.name} - {self.state.uf}"


class Submission(models.Model):
    """A single submission of answers to a Survey."""

    survey = models.ForeignKey(Survey, on_delete=models.PROTECT, related_name='submissions')
    company = models.ForeignKey(Company, on_delete=models.PROTECT, related_name='submissions')
    survey_token = models.CharField(max_length=20, db_index=True)

    # Geographic information
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, related_name='submissions')
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True, related_name='submissions')
    
    # Legacy location fields (kept for backward compatibility)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    user_agent = models.TextField(blank=True)
    occurred_at = models.DateTimeField(default=timezone.now)

    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'answers_submission'
        indexes = [
            models.Index(fields=['city']),
            models.Index(fields=['state']),
        ]

    def __str__(self) -> str:  # type: ignore[override]
        return f"Submission {self.pk} for survey {self.survey_id} ({self.survey_token})"


class SubmissionAnswer(models.Model):
    """Answer to a single Question as part of a Submission.

    Multiple rows can exist for the same question to support multiple selections
    in multiple-choice questions. For text questions, only one row should exist
    and it must have text_response filled.
    """

    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(Option, null=True, blank=True, on_delete=models.CASCADE)
    text_response = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'answers_submission_answer'
        indexes = [
            models.Index(fields=['submission', 'question']),
        ]

    def __str__(self) -> str:  # type: ignore[override]
        if self.selected_option_id:
            return f"Answer opt#{self.selected_option_id} (Q{self.question_id})"
        return f"Answer text (Q{self.question_id})"


