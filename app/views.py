from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from surveys.models import Company, Survey

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema


@login_required(login_url='login')
def home(request):
    context = {
        'companies_count': Company.objects.count(),
        'surveys_count': Survey.objects.count(),
        'recent_surveys': Survey.objects.select_related('company').order_by('-created_at')[:5],
    }
    return render(request, 'home.html', context)


@extend_schema(
    tags=['Health'],
    summary='Ping endpoint',
    description='Simple endpoint to test authentication. Returns pong if authenticated. Supports Basic Auth (username/password) or Bearer Token (JWT).',
    operation_id='ping',
    responses={
        200: {'type': 'string', 'example': 'pong'},
        401: {'type': 'object', 'example': {'detail': 'Authentication credentials were not provided.'}},
    },
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ping(request):
    """Simple ping endpoint to test authentication (Basic Auth or JWT)."""
    return Response('pong', status=status.HTTP_200_OK)


