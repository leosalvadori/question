from django.db import migrations, models
import django.db.models


def generate_tokens(apps, schema_editor):
	Survey = apps.get_model('surveys', 'Survey')
	for survey in Survey.objects.all().iterator():
		if not getattr(survey, 'token', None) and survey.company_id:
			# mimic model logic without get_random_string in migrations to keep deterministic
			# simple fallback: company_id plus pk padded
			base = f"{survey.company_id}-{str(survey.pk).zfill(6)}"
			# ensure uniqueness just in case
			candidate = base
			counter = 0
			while Survey.objects.filter(token=candidate).exists():
				counter += 1
				candidate = f"{base}-{counter}"
			survey.token = candidate
			survey.save(update_fields=['token'])


class Migration(migrations.Migration):

	dependencies = [
		('surveys', '0001_initial'),
	]

	operations = [
		migrations.AddField(
			model_name='survey',
			name='token',
			field=models.CharField(blank=True, db_index=True, max_length=20, unique=True),
		),
		migrations.RunPython(generate_tokens, migrations.RunPython.noop),
	]


