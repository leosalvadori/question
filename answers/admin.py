from django.contrib import admin

from .models import Submission, SubmissionAnswer


class SubmissionAnswerInline(admin.TabularInline):
    model = SubmissionAnswer
    fields = ('question', 'selected_option', 'text_response', 'created_at')
    readonly_fields = ('created_at',)
    extra = 0
    show_change_link = True


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'survey', 'company', 'survey_token', 'ip_address',
        'latitude', 'longitude', 'submitted_at',
    )
    list_filter = (
        'survey', 'company', ('submitted_at', admin.DateFieldListFilter),
    )
    search_fields = (
        'survey__title', 'company__name', 'survey_token', 'ip_address',
    )
    date_hierarchy = 'submitted_at'
    inlines = [SubmissionAnswerInline]
    list_select_related = ('survey', 'company')

    def get_queryset(self, request):  # type: ignore[override]
        qs = super().get_queryset(request)
        return qs.select_related('survey', 'company')


@admin.register(SubmissionAnswer)
class SubmissionAnswerAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'submission', 'question', 'selected_option', 'created_at',
    )
    list_filter = (
        'question', 'selected_option',
    )
    search_fields = (
        'submission__survey__title', 'submission__company__name', 'text_response',
    )
    raw_id_fields = ('submission',)
    list_select_related = ('submission', 'question', 'selected_option')

    def get_queryset(self, request):  # type: ignore[override]
        qs = super().get_queryset(request)
        return qs.select_related('submission', 'question', 'selected_option')



