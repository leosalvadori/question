from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

	initial = True

	dependencies = []

	operations = [
		migrations.CreateModel(
			name='Company',
			fields=[
				('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
				('name', models.CharField(max_length=255)),
				('created_at', models.DateTimeField(auto_now_add=True)),
				('updated_at', models.DateTimeField(auto_now=True)),
			],
		),
		migrations.CreateModel(
			name='Survey',
			fields=[
				('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
				('title', models.CharField(max_length=255)),
				('description', models.TextField(blank=True)),
				('created_at', models.DateTimeField(auto_now_add=True)),
				('updated_at', models.DateTimeField(auto_now=True)),
				('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='surveys', to='surveys.company')),
			],
		),
		migrations.CreateModel(
			name='Question',
			fields=[
				('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
				('question_text', models.TextField()),
				('question_type', models.CharField(choices=[('text', 'Text'), ('multiple_choice', 'Multiple Choice')], default='text', max_length=32)),
				('created_at', models.DateTimeField(auto_now_add=True)),
				('updated_at', models.DateTimeField(auto_now=True)),
				('survey', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='surveys.survey')),
			],
		),
		migrations.CreateModel(
			name='Option',
			fields=[
				('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
				('option_text', models.TextField(blank=True, null=True)),
				('option_type', models.CharField(choices=[('choice', 'Choice'), ('text', 'Text')], default='choice', max_length=16)),
				('created_at', models.DateTimeField(auto_now_add=True)),
				('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='options', to='surveys.question')),
			],
		),
	]


