from drf_spectacular.utils import extend_schema, OpenApiExample
from .serializers import SubmissionCreateSerializer, SubmissionResponseSerializer


submit_answers_schema = extend_schema(
    tags=['Answers'],
    summary='Submit answers for a survey',
    description='Accepts a bearer-authenticated POST with a survey token and answers. Records metadata like IP, lat/lon, and occurred_at.',
    request=SubmissionCreateSerializer,
    responses={
        201: SubmissionResponseSerializer,
        400: dict,
        404: dict,
    },
    examples=[
        OpenApiExample(
            'SubmitMultipleChoiceAndText',
            value={
                'token': '2-M58TVW',
                'occurred_at': '2025-08-20T12:34:56',
                'latitude': -23.55052,
                'longitude': -46.633308,
                'answers': [
                    {'question_id': 2, 'option_ids': [3]},
                    {'question_id': 3, 'option_ids': [5, 8]},
                    {'question_id': 4, 'text_response': 'Atendimento ótimo'}
                ]
            },
            request_only=True,
        )
    ],
)


