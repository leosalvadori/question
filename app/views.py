from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from surveys.models import Company, Survey


@login_required(login_url='login')
def home(request):
    context = {
        'companies_count': Company.objects.count(),
        'surveys_count': Survey.objects.count(),
        'recent_surveys': Survey.objects.select_related('company').order_by('-created_at')[:5],
    }
    return render(request, 'home.html', context)
