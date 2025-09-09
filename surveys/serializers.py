from rest_framework import serializers
from companies.models import Company
from .models import Survey, Question, Option


class CompanyBriefSerializer(serializers.ModelSerializer):
	class Meta:
		model = Company
		fields = ['id', 'name']


class OptionSerializer(serializers.ModelSerializer):
	class Meta:
		model = Option
		fields = ['id', 'option_text', 'option_type', 'created_at']


class QuestionSerializer(serializers.ModelSerializer):
	options = OptionSerializer(many=True, read_only=True)

	class Meta:
		model = Question
		fields = ['id', 'question_text', 'question_type', 'created_at', 'updated_at', 'options']


class SurveyDetailSerializer(serializers.ModelSerializer):
	company = CompanyBriefSerializer(read_only=True)
	questions = QuestionSerializer(many=True, read_only=True)

	class Meta:
		model = Survey
		fields = ['id', 'token', 'title', 'description', 'created_at', 'updated_at', 'company', 'questions']
from rest_framework import serializers
from .models import Company, Survey, Question, Option


class CompanyBriefSerializer(serializers.ModelSerializer):
	class Meta:
		model = Company
		fields = ['id', 'name']


class OptionSerializer(serializers.ModelSerializer):
	class Meta:
		model = Option
		fields = ['id', 'option_text', 'option_type', 'created_at']


class QuestionSerializer(serializers.ModelSerializer):
	options = OptionSerializer(many=True, read_only=True)

	class Meta:
		model = Question
		fields = ['id', 'question_text', 'question_type', 'created_at', 'updated_at', 'options']


class SurveyDetailSerializer(serializers.ModelSerializer):
	company = CompanyBriefSerializer(read_only=True)
	questions = QuestionSerializer(many=True, read_only=True)

	class Meta:
		model = Survey
		fields = ['id', 'token', 'title', 'description', 'created_at', 'updated_at', 'company', 'questions']

