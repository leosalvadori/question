from django.db import models
from django.utils import timezone

from companies.models import Company
from surveys.models import Survey, Question, Option


class Submission(models.Model):
    """A single submission of answers to a Survey."""

    survey = models.ForeignKey(Survey, on_delete=models.PROTECT, related_name='submissions')
    company = models.ForeignKey(Company, on_delete=models.PROTECT, related_name='submissions')
    survey_token = models.CharField(max_length=20, db_index=True)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    user_agent = models.TextField(blank=True)
    occurred_at = models.DateTimeField(default=timezone.now)

    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'answers_submission'

    def __str__(self) -> str:  # type: ignore[override]
        return f"Submission {self.pk} for survey {self.survey_id} ({self.survey_token})"


class SubmissionAnswer(models.Model):
    """Answer to a single Question as part of a Submission.

    Multiple rows can exist for the same question to support multiple selections
    in multiple-choice questions. For text questions, only one row should exist
    and it must have text_response filled.
    """

    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.PROTECT)
    selected_option = models.ForeignKey(Option, null=True, blank=True, on_delete=models.PROTECT)
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


