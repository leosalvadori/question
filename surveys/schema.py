from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes, OpenApiExample
from .serializers import SurveyDetailSerializer


get_survey_by_token_schema = extend_schema(
	tags=['Surveys'],
	summary='Get survey by token',
	description='Returns the full survey structure (company, questions, options) given a valid token.',
	operation_id='get_survey_by_token',
	parameters=[
		OpenApiParameter(
			name='token',
			location=OpenApiParameter.QUERY,
			required=True,
			description='Survey access token (query string)',
			type=OpenApiTypes.STR,
			examples=[
				OpenApiExample('TokenExample', value='2-M58TVW'),
			],
		),
	],
	responses={
		200: SurveyDetailSerializer,
		400: OpenApiTypes.OBJECT,
		404: OpenApiTypes.OBJECT,
	},
	examples=[
		OpenApiExample(
			'ExampleSuccess',
			value={
				'id': 3,
				'token': '2-M58TVW',
				'title': 'Satisfação loja 002',
				'description': 'Pesquisa para entender a satisfação dos clientes da loja 002 no período de agosto',
				'created_at': '2025-08-20T00:02:50.527015',
				'updated_at': '2025-08-20T00:05:09.286708',
				'company': {
					'id': 2,
					'name': 'Tramontina Ltda'
				},
				'questions': [
					{
						'id': 2,
						'question_text': 'Você teve uma boa experiência na loja?',
						'question_type': 'single_choice',
						'created_at': '2025-08-20T00:03:17.628071',
						'updated_at': '2025-08-20T00:03:17.628106',
						'options': [
							{
								'id': 3,
								'option_text': 'Sim',
								'option_type': 'choice',
								'created_at': '2025-08-20T00:03:26.326461'
							},
							{
								'id': 4,
								'option_text': 'Não',
								'option_type': 'choice',
								'created_at': '2025-08-20T00:03:32.335794'
							}
						]
					},
					{
						'id': 3,
						'question_text': 'Qual cor mais lhe agradou?',
						'question_type': 'multiple_choice',
						'created_at': '2025-08-20T00:03:42.959355',
						'updated_at': '2025-08-20T00:03:42.959374',
						'options': [
							{
								'id': 5,
								'option_text': 'Preto',
								'option_type': 'choice',
								'created_at': '2025-08-20T00:03:48.753112'
							},
							{
								'id': 6,
								'option_text': 'Branco',
								'option_type': 'choice',
								'created_at': '2025-08-20T00:03:57.268532'
							},
							{
								'id': 7,
								'option_text': 'Vermelho',
								'option_type': 'choice',
								'created_at': '2025-08-20T00:04:02.269944'
							},
							{
								'id': 8,
								'option_text': 'Verde',
								'option_type': 'choice',
								'created_at': '2025-08-20T00:04:05.687078'
							}
						]
					},
					{
						'id': 4,
						'question_text': 'Em poucas palavras, resuma como foi sua experiência no geral',
						'question_type': 'text',
						'created_at': '2025-08-20T00:04:30.213914',
						'updated_at': '2025-08-20T00:04:30.213944',
						'options': []
					}
				]
			},
			response_only=True,
		),
	],
)


