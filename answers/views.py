from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from io import BytesIO
import json

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from companies.models import Company
from surveys.models import Survey, Question
from .models import State, City, Submission, SubmissionAnswer
from .serializers import SubmissionCreateSerializer, SubmissionResponseSerializer
from .schema import submit_answers_schema
from companies.decorators import require_token_not_revoked


def test_csv_export(request, survey_id: int):
    """Test CSV export without authentication for debugging."""
    survey = get_object_or_404(Survey.objects.select_related('company'), id=survey_id)
    
    import csv
    resp = HttpResponse(content_type='text/csv')
    resp['Content-Disposition'] = f'attachment; filename="test_export_{survey_id}.csv"'
    writer = csv.writer(resp)
    
    writer.writerow(['Test', 'Export', 'Working'])
    writer.writerow(['Survey ID', survey_id])
    writer.writerow(['Survey Title', survey.title])
    
    return resp


@submit_answers_schema
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@require_token_not_revoked
def submit_answers(request):
    serializer = SubmissionCreateSerializer(data=request.data, context={'request': request})
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    submission = serializer.save()
    return Response(SubmissionResponseSerializer(submission).data, status=status.HTTP_201_CREATED)



# ---------------------- Admin-like HTML Views ----------------------

@login_required
def surveys_index(request):
    """List surveys with optional company filter and total submissions count."""
    surveys_qs = Survey.objects.select_related('company')
    company_filter = request.GET.get('company')
    token_filter = request.GET.get('token')
    if company_filter:
        surveys_qs = surveys_qs.filter(company_id=company_filter)
    if token_filter:
        surveys_qs = surveys_qs.filter(token__icontains=token_filter)

    # Annotate counts via separate query for performance
    counts = (
        Submission.objects.values('survey_id').annotate(total=Count('id'))
    )
    count_map = {c['survey_id']: c['total'] for c in counts}

    page_size = int(request.GET.get('page_size') or 15)
    paginator = Paginator(surveys_qs.order_by('-created_at'), page_size)
    page = request.GET.get('page')
    surveys_page = paginator.get_page(page)

    companies = Company.objects.all().order_by('name')
    return render(request, 'answers/surveys_index.html', {
        'surveys': surveys_page,
        'count_map': count_map,
        'companies': companies,
        'page_obj': surveys_page,
        'page_size': page_size,
        'extra_query': _build_extra_query(request, exclude_keys={'page'}),
    })


@login_required
def submissions_detail(request, survey_id: int):
    survey = get_object_or_404(Survey.objects.select_related('company'), id=survey_id)
    # Load submissions and group answers per submission
    submissions = Submission.objects.filter(survey=survey)
    # Bulk delete handling
    if request.method == 'POST' and request.POST.get('action') == 'bulk_delete':
        ids = request.POST.getlist('selected_ids')
        Submission.objects.filter(survey=survey, id__in=ids).delete()
        params = []
        for key in ('from', 'to', 'state', 'city', 'page', 'page_size'):
            val = request.POST.get(key)
            if val:
                params.append(f"{key}={val}")
        query = ('?' + '&'.join(params)) if params else ''
        return redirect(f"{reverse('answers_detail', args=[survey_id])}{query}")
    
    # Get filter options
    states = _get_states_with_submissions(survey_id)
    selected_state_id = request.GET.get('state')
    selected_city_id = request.GET.get('city')
    
    # Get cities based on selected state
    cities = []
    if selected_state_id:
        cities = _get_cities_with_submissions(survey_id, int(selected_state_id))
    
    # Apply filters
    date_from = request.GET.get('from')
    date_to = request.GET.get('to')
    if date_from:
        submissions = submissions.filter(submitted_at__date__gte=date_from)
    if date_to:
        submissions = submissions.filter(submitted_at__date__lte=date_to)
    if selected_state_id:
        submissions = submissions.filter(state_id=selected_state_id)
    if selected_city_id:
        submissions = submissions.filter(city_id=selected_city_id)
    
    submissions = submissions.order_by('-submitted_at')
    paginator = Paginator(submissions, 15)
    submissions_page = paginator.get_page(request.GET.get('page'))
    answers_by_submission: dict[int, list[SubmissionAnswer]] = {}
    answers = (
        SubmissionAnswer.objects
        .filter(submission__in=submissions_page)
        .select_related('question', 'selected_option', 'submission')
        .order_by('question_id', 'id')
    )
    for a in answers:
        answers_by_submission.setdefault(a.submission_id, []).append(a)

    # Preload questions
    questions = list(Question.objects.filter(survey=survey).order_by('id'))
    fmt = request.GET.get('format')
    if fmt == 'json':
        # Export a simple JSON structure
        data = []
        for sub in submissions_page:
            item = {
                'submission_id': sub.id,
                'submitted_at': sub.submitted_at.isoformat(),
                'ip_address': sub.ip_address,
                'latitude': float(sub.latitude) if sub.latitude is not None else None,
                'longitude': float(sub.longitude) if sub.longitude is not None else None,
                'state': sub.state.name if sub.state else None,
                'city': sub.city.name if sub.city else None,
                'answers': [],
            }
            for ans in answers_by_submission.get(sub.id, []):
                item['answers'].append({
                    'question_id': ans.question_id,
                    'question_text': ans.question.question_text,
                    'selected_option_id': ans.selected_option_id,
                    'selected_option_text': ans.selected_option.option_text if ans.selected_option_id else None,
                    'text_response': ans.text_response,
                })
            data.append(item)
        return JsonResponse(data, safe=False)

    if fmt == 'csv':
        import csv
        resp = HttpResponse(content_type='text/csv')
        resp['Content-Disposition'] = 'attachment; filename="submissions_detail.csv"'
        writer = csv.writer(resp)
        writer.writerow(['Submission ID', 'Submitted At', 'IP', 'State', 'City', 'Latitude', 'Longitude', 'Question', 'Answer'])
        for sub in submissions_page:
            for ans in answers_by_submission.get(sub.id, []):
                if ans.selected_option_id:
                    answer_text = ans.selected_option.option_text
                else:
                    answer_text = ans.text_response or ''
                writer.writerow([
                    sub.id,
                    sub.submitted_at,
                    sub.ip_address or '',
                    sub.state.name if sub.state else '',
                    sub.city.name if sub.city else '',
                    sub.latitude or '',
                    sub.longitude or '',
                    ans.question.question_text,
                    answer_text,
                ])
        return resp

    return render(request, 'answers/submissions_detail.html', {
        'survey': survey,
        'submissions': submissions_page,
        'answers_by_submission': answers_by_submission,
        'questions': questions,
        'page_obj': submissions_page,
        'states': states,
        'cities': cities,
        'selected_state_id': selected_state_id,
        'selected_city_id': selected_city_id,
        'extra_query': _build_extra_query(request, exclude_keys={'page'}),
    })


@login_required
def survey_dashboard(request, survey_id: int):
    survey = get_object_or_404(Survey.objects.select_related('company'), id=survey_id)
    
    # Get filter options
    states = _get_states_with_submissions(survey_id)
    selected_state_id = request.GET.get('state')
    selected_city_id = request.GET.get('city')
    
    # Get cities based on selected state
    cities = []
    if selected_state_id:
        cities = _get_cities_with_submissions(survey_id, int(selected_state_id))
    
    # Apply filters to submissions
    submissions_qs = Submission.objects.filter(survey=survey)
    if selected_state_id:
        submissions_qs = submissions_qs.filter(state_id=selected_state_id)
    if selected_city_id:
        submissions_qs = submissions_qs.filter(city_id=selected_city_id)
    
    total_submissions = submissions_qs.count()
    last_submission = submissions_qs.order_by('-submitted_at').first()

    # Check for export format
    fmt = request.GET.get('format')
    if fmt == 'csv':
        import csv
        resp = HttpResponse(content_type='text/csv; charset=utf-8')
        resp['Content-Disposition'] = f'attachment; filename="dashboard_{survey.title}_{survey_id}.csv"'
        resp['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        resp['Pragma'] = 'no-cache'
        resp['Expires'] = '0'
        writer = csv.writer(resp)
        
        # Get all questions for this survey
        questions = Question.objects.filter(survey=survey).order_by('id')
        
        # Create header with basic info + all questions
        header = ['Submission ID', 'Submitted At', 'IP Address', 'State', 'City', 'Latitude', 'Longitude']
        for q in questions:
            header.append(f'Q{q.id}: {q.question_text}')
        writer.writerow(header)
        
        # Get all answers for submissions
        answers_by_submission = {}
        for ans in SubmissionAnswer.objects.filter(
            submission__in=submissions_qs
        ).select_related('question', 'selected_option'):
            if ans.submission_id not in answers_by_submission:
                answers_by_submission[ans.submission_id] = {}
            answers_by_submission[ans.submission_id][ans.question_id] = ans
        
        # Write submissions data
        for sub in submissions_qs.select_related('state', 'city'):
            row = [
                sub.id,
                sub.submitted_at.strftime('%Y-%m-%d %H:%M:%S') if sub.submitted_at else '',
                sub.ip_address or '',
                sub.state.name if sub.state else '',
                sub.city.name if sub.city else '',
                sub.latitude or '',
                sub.longitude or '',
            ]
            
            # Add answers for each question
            for q in questions:
                answer = answers_by_submission.get(sub.id, {}).get(q.id)
                if answer:
                    if answer.selected_option_id:
                        answer_text = answer.selected_option.option_text
                    else:
                        answer_text = answer.text_response or ''
                else:
                    answer_text = ''
                row.append(answer_text)
            
            writer.writerow(row)
        return resp
    
    if fmt == 'json':
        data = []
        
        # Get all answers for submissions
        answers_by_submission = {}
        for ans in SubmissionAnswer.objects.filter(
            submission__in=submissions_qs
        ).select_related('question', 'selected_option'):
            if ans.submission_id not in answers_by_submission:
                answers_by_submission[ans.submission_id] = {}
            answers_by_submission[ans.submission_id][ans.question_id] = ans
        
        for sub in submissions_qs.select_related('state', 'city'):
            submission_data = {
                'id': sub.id,
                'submitted_at': sub.submitted_at.isoformat() if sub.submitted_at else None,
                'ip_address': sub.ip_address,
                'state': sub.state.name if sub.state else None,
                'city': sub.city.name if sub.city else None,
                'latitude': float(sub.latitude) if sub.latitude else None,
                'longitude': float(sub.longitude) if sub.longitude else None,
                'answers': []
            }
            
            # Add answers
            for ans in answers_by_submission.get(sub.id, {}).values():
                answer_data = {
                    'question_id': ans.question_id,
                    'question_text': ans.question.question_text,
                    'selected_option_id': ans.selected_option_id,
                    'selected_option_text': ans.selected_option.option_text if ans.selected_option_id else None,
                    'text_response': ans.text_response,
                }
                submission_data['answers'].append(answer_data)
            
            data.append(submission_data)
        return JsonResponse(data, safe=False)

    # Collect geo points for heatmap
    geo_points = []
    for sub in submissions_qs.exclude(
        latitude__isnull=True
    ).exclude(
        longitude__isnull=True
    ).only('latitude', 'longitude'):
        try:
            lat = float(sub.latitude)
            lng = float(sub.longitude)
            geo_points.append({
                'lat': lat,
                'lng': lng,
                'intensity': 1.0  # Fixed intensity for each point
            })
        except (TypeError, ValueError):
            continue

    distributions = []
    for q in Question.objects.filter(survey=survey).order_by('id'):
        if q.question_type in (Question.MULTIPLE_CHOICE, Question.SINGLE_CHOICE):
            # Apply same filters to answers
            answers_qs = SubmissionAnswer.objects.filter(question=q, selected_option__isnull=False)
            if selected_state_id:
                answers_qs = answers_qs.filter(submission__state_id=selected_state_id)
            if selected_city_id:
                answers_qs = answers_qs.filter(submission__city_id=selected_city_id)
            
            opts = (
                answers_qs
                .values('selected_option_id', 'selected_option__option_text')
                .annotate(total=Count('id'))
                .order_by('-total')
            )
            distributions.append({'question': q, 'options': list(opts)})
    
    return render(request, 'answers/survey_dashboard.html', {
        'survey': survey,
        'total_submissions': total_submissions,
        'last_submission': last_submission,
        'distributions': distributions,
        'geo_points': geo_points,
        'states': states,
        'cities': cities,
        'selected_state_id': selected_state_id,
        'selected_city_id': selected_city_id,
    })

@login_required
def delete_submission(request, survey_id: int, submission_id: int):
    submission = get_object_or_404(Submission, id=submission_id, survey_id=survey_id)
    if request.method == 'POST':
        submission.delete()
        # Preserve filters and pagination
        params = []
        for key in ('from', 'to', 'page', 'page_size'):
            val = request.POST.get(key)
            if val:
                params.append(f"{key}={val}")
        query = ('?' + '&'.join(params)) if params else ''
        return redirect(f"{reverse('answers_detail', args=[survey_id])}{query}")
    # Fallback redirect
    return redirect('answers_detail', survey_id=survey_id)


def _build_extra_query(request, exclude_keys: set[str] | None = None) -> str:
    exclude_keys = exclude_keys or set()
    parts = []
    for k, v in request.GET.items():
        if k in exclude_keys or k == 'page' or v == '':
            continue
        parts.append(f"&{k}={v}")
    return ''.join(parts)


def _get_states_with_submissions(survey_id: int) -> list[State]:
    """Get all states that have submissions for a specific survey."""
    return list(
        State.objects
        .filter(submissions__survey_id=survey_id)
        .distinct()
        .order_by('name')
    )


def _get_cities_with_submissions(survey_id: int, state_id: int = None) -> list[City]:
    """Get all cities that have submissions for a specific survey, optionally filtered by state."""
    queryset = City.objects.filter(submissions__survey_id=survey_id).distinct()
    if state_id:
        queryset = queryset.filter(state_id=state_id)
    return list(queryset.order_by('name'))


@login_required
@require_http_methods(["GET"])
def get_cities_for_state(request, survey_id: int):
    """AJAX endpoint to get cities for a specific state and survey."""
    state_id = request.GET.get('state_id')
    if not state_id:
        return JsonResponse({'cities': []})
    
    cities = _get_cities_with_submissions(survey_id, int(state_id))
    return JsonResponse({
        'cities': [
            {'id': city.id, 'name': city.name, 'uf': city.state.uf}
            for city in cities
        ]
    })


def _build_heat_grid(points: list[tuple[float, float]], rows: int, cols: int) -> dict:
    """Bucket lat/lon points into a rows x cols grid and compute counts and colors.

    Returns dict with: { 'rows': [[{'count': int, 'color': '#rrggbb'}, ...], ...], 'max': int }
    """
    if not points:
        return {'rows': [[{'count': 0, 'color': '#ffffff'} for _ in range(cols)] for _ in range(rows)], 'max': 0}

    lats = [p[0] for p in points]
    lons = [p[1] for p in points]
    min_lat, max_lat = min(lats), max(lats)
    min_lon, max_lon = min(lons), max(lons)

    # Avoid zero span
    if max_lat - min_lat == 0:
        max_lat += 0.0001
        min_lat -= 0.0001
    if max_lon - min_lon == 0:
        max_lon += 0.0001
        min_lon -= 0.0001

    # Initialize grid counts
    grid = [[0 for _ in range(cols)] for _ in range(rows)]
    for lat, lon in points:
        r = int((lat - min_lat) / (max_lat - min_lat) * (rows - 1))
        c = int((lon - min_lon) / (max_lon - min_lon) * (cols - 1))
        # Clamp just in case
        r = max(0, min(rows - 1, r))
        c = max(0, min(cols - 1, c))
        grid[r][c] += 1

    max_count = max(max(row) for row in grid) if points else 0

    def color_for(value: int) -> str:
        if max_count == 0:
            return '#ffffff'
        # Intensity 0..1 maps white -> red
        t = value / max_count
        r = 255
        g = int(255 * (1.0 - t))
        b = int(255 * (1.0 - t))
        return f"#{r:02x}{g:02x}{b:02x}"

    colored_rows: list[list[dict]] = []
    for r in range(rows):
        row_out: list[dict] = []
        for c in range(cols):
            val = grid[r][c]
            row_out.append({'count': val, 'color': color_for(val)})
        colored_rows.append(row_out)

    return {'rows': colored_rows, 'max': max_count}


