from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

	dependencies = [
		('companies', '0001_initial'),
	]

	operations = [
		migrations.CreateModel(
			name='CompanyToken',
			fields=[
				('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
				('label', models.CharField(blank=True, max_length=100)),
				('refresh_jti', models.CharField(db_index=True, max_length=50)),
				('created_at', models.DateTimeField(auto_now_add=True)),
				('revoked_at', models.DateTimeField(blank=True, null=True)),
				('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='api_tokens', to='companies.company')),
			],
		),
	]


