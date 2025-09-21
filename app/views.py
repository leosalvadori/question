from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from surveys.models import Company, Survey

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from companies.decorators import require_token_not_revoked


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
    description='Simple endpoint to test JWT authentication. Returns pong if token is valid and not revoked.',
    operation_id='ping',
    responses={
        200: {'type': 'string', 'example': 'pong'},
        401: {'type': 'object', 'example': {'detail': 'Token has been revoked.'}},
    },
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@require_token_not_revoked
def ping(request):
    """Simple ping endpoint to test JWT authentication."""
    return Response('pong', status=status.HTTP_200_OK)


