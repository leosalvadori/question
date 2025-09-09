from django.contrib import admin
from .models import Survey, Question, Option


class OptionInline(admin.TabularInline):
	model = Option
	extra = 1


class QuestionInline(admin.TabularInline):
	model = Question
	extra = 1




@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
	list_display = ('id', 'title', 'company', 'token', 'created_at', 'updated_at')
	list_filter = ('company',)
	search_fields = ('title', 'description', 'token')
	readonly_fields = ('created_at', 'updated_at')
	inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
	list_display = ('id', 'survey', 'question_type', 'short_text', 'created_at', 'updated_at')
	list_filter = ('question_type', 'survey')
	search_fields = ('question_text',)
	readonly_fields = ('created_at', 'updated_at')
	inlines = [OptionInline]

	def short_text(self, obj):  # type: ignore[no-untyped-def]
		return (obj.question_text or '')[:40]
	short_text.short_description = 'Question'


@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
	list_display = ('id', 'question', 'option_type', 'short_text', 'created_at')
	list_filter = ('option_type',)
	search_fields = ('option_text',)
	readonly_fields = ('created_at',)

	def short_text(self, obj):  # type: ignore[no-untyped-def]
		return (obj.option_text or '')[:40]
	short_text.short_description = 'Option'

