from typing import Any, Dict, List

from django.db import transaction
from rest_framework import serializers

from companies.models import Company
from surveys.models import Survey, Question, Option
from .models import Submission, SubmissionAnswer


class SubmissionAnswerInputSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    # For multiple choice: list of option IDs (one or more)
    option_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False, allow_empty=False
    )
    # For single choice: allow a single option as convenience
    option_id = serializers.IntegerField(required=False)
    # For text questions: a text response
    text_response = serializers.CharField(required=False, allow_blank=True)


class SubmissionCreateSerializer(serializers.Serializer):
    token = serializers.CharField()
    occurred_at = serializers.DateTimeField(required=False, allow_null=True)
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)
    # Geographic data for preview/testing
    ibge_code = serializers.CharField(required=False, allow_blank=True)
    state_code = serializers.CharField(required=False, allow_blank=True)
    answers = SubmissionAnswerInputSerializer(many=True)

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        token = attrs['token']
        survey = Survey.objects.filter(token=token).select_related('company').first()
        if not survey:
            raise serializers.ValidationError({'token': 'invalid or unknown survey token'})
        attrs['survey'] = survey

        # Load referenced questions and options in bulk for validation
        question_ids = [a['question_id'] for a in attrs['answers']]
        questions = Question.objects.filter(id__in=question_ids, survey=survey)
        question_map = {q.id: q for q in questions}
        if len(question_map) != len(set(question_ids)):
            raise serializers.ValidationError('One or more questions are invalid for this survey')

        # Build option map by question where provided
        option_ids: List[int] = []
        for ans in attrs['answers']:
            if 'option_ids' in ans:
                option_ids.extend(ans['option_ids'])
            if 'option_id' in ans:
                option_ids.append(ans['option_id'])
        options = Option.objects.filter(id__in=option_ids, question__survey=survey)
        option_map = {opt.id: opt for opt in options}
        if len(option_map) != len(set(option_ids)):
            raise serializers.ValidationError('One or more options are invalid for this survey')

        # Per-answer rule checks
        for ans in attrs['answers']:
            question = question_map[ans['question_id']]
            option_ids_for_answer = ans.get('option_ids')
            text_response = ans.get('text_response')

            if question.question_type == Question.MULTIPLE_CHOICE:
                if not option_ids_for_answer:
                    raise serializers.ValidationError(
                        f'Question {question.id} expects option_ids'
                    )
                # Ensure all options belong to this question
                for oid in option_ids_for_answer:
                    opt = option_map.get(oid)
                    if not opt or opt.question_id != question.id:
                        raise serializers.ValidationError(
                            f'Option {oid} does not belong to question {question.id}'
                        )
                # Text should not be present for pure multiple choice
                if text_response:
                    raise serializers.ValidationError(
                        f'Question {question.id} does not accept text_response'
                    )
            elif question.question_type == Question.SINGLE_CHOICE:
                # Normalize to option_ids with exactly one element
                if option_ids_for_answer is None and 'option_id' in ans:
                    option_ids_for_answer = [ans['option_id']]
                    ans['option_ids'] = option_ids_for_answer
                if not option_ids_for_answer or len(option_ids_for_answer) != 1:
                    raise serializers.ValidationError(
                        f'Question {question.id} expects exactly one option'
                    )
                oid = option_ids_for_answer[0]
                opt = option_map.get(oid)
                if not opt or opt.question_id != question.id:
                    raise serializers.ValidationError(
                        f'Option {oid} does not belong to question {question.id}'
                    )
                if text_response:
                    raise serializers.ValidationError(
                        f'Question {question.id} does not accept text_response'
                    )
            else:  # TEXT
                if option_ids_for_answer:
                    raise serializers.ValidationError(
                        f'Question {question.id} does not accept options'
                    )
                if text_response is None:
                    raise serializers.ValidationError(
                        f'Question {question.id} requires text_response'
                    )

        attrs['question_map'] = question_map
        attrs['option_map'] = option_map
        return attrs

    @transaction.atomic
    def create(self, validated_data: Dict[str, Any]) -> Submission:
        request = self.context.get('request')
        survey: Survey = validated_data['survey']

        # Process geographic data if provided
        city = None
        state = None
        ibge_code = validated_data.get('ibge_code')
        state_code = validated_data.get('state_code')
        
        if ibge_code and state_code:
            try:
                from .models import City, State
                city = City.objects.get(ibge_code=ibge_code)
                state = State.objects.get(code=state_code)
                
                # Validate that the city belongs to the state
                if city.state != state:
                    raise serializers.ValidationError(
                        f'City {city.name} does not belong to state {state.name}'
                    )
            except City.DoesNotExist:
                raise serializers.ValidationError(f'City with IBGE code {ibge_code} not found')
            except State.DoesNotExist:
                raise serializers.ValidationError(f'State with code {state_code} not found')

        submission = Submission.objects.create(
            survey=survey,
            company=survey.company,
            survey_token=survey.token,
            occurred_at=validated_data.get('occurred_at') or None,
            latitude=validated_data.get('latitude'),
            longitude=validated_data.get('longitude'),
            city=city,
            state=state,
            ip_address=self._get_ip_from_request(request),
            user_agent=self._get_ua_from_request(request),
        )

        answers_in = validated_data['answers']
        option_map = validated_data['option_map']
        question_map = validated_data['question_map']

        submission_answers: List[SubmissionAnswer] = []
        for ans in answers_in:
            question = question_map[ans['question_id']]
            if question.question_type == Question.MULTIPLE_CHOICE:
                for oid in ans['option_ids']:
                    submission_answers.append(
                        SubmissionAnswer(
                            submission=submission,
                            question=question,
                            selected_option=option_map[oid],
                        )
                    )
            elif question.question_type == Question.SINGLE_CHOICE:
                oid = ans['option_ids'][0]
                submission_answers.append(
                    SubmissionAnswer(
                        submission=submission,
                        question=question,
                        selected_option=option_map[oid],
                    )
                )
            else:
                submission_answers.append(
                    SubmissionAnswer(
                        submission=submission,
                        question=question,
                        text_response=ans.get('text_response', ''),
                    )
                )

        SubmissionAnswer.objects.bulk_create(submission_answers)
        return submission

    def _get_ip_from_request(self, request) -> str | None:  # type: ignore[override]
        if not request:
            return None
        # X-Forwarded-For support (take first)
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        if xff:
            return xff.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')

    def _get_ua_from_request(self, request) -> str:  # type: ignore[override]
        if not request:
            return ''
        return request.META.get('HTTP_USER_AGENT', '')


class SubmissionResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ['id', 'survey_token', 'submitted_at']


