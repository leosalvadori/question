import csv
import os
from django.core.management.base import BaseCommand
from django.db import transaction
from answers.models import State, City


class Command(BaseCommand):
    help = 'Load Brazilian states and cities data from CSV files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--states-file',
            type=str,
            default='loads/estados.csv',
            help='Path to states CSV file'
        )
        parser.add_argument(
            '--cities-file',
            type=str,
            default='loads/municipios.csv',
            help='Path to cities CSV file'
        )
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Clear existing data before loading'
        )

    def handle(self, *args, **options):
        states_file = options['states_file']
        cities_file = options['cities_file']
        clear_existing = options['clear_existing']

        if not os.path.exists(states_file):
            self.stdout.write(
                self.style.ERROR(f'States file not found: {states_file}')
            )
            return

        if not os.path.exists(cities_file):
            self.stdout.write(
                self.style.ERROR(f'Cities file not found: {cities_file}')
            )
            return

        with transaction.atomic():
            if clear_existing:
                self.stdout.write('Clearing existing data...')
                City.objects.all().delete()
                State.objects.all().delete()

            # Load states
            self.stdout.write('Loading states...')
            states_created = 0
            with open(states_file, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    state, created = State.objects.get_or_create(
                        code=row['codigo_uf'],
                        defaults={
                            'uf': row['uf'],
                            'name': row['nome'],
                            'latitude': float(row['latitude']),
                            'longitude': float(row['longitude']),
                            'region': row['regiao'],
                        }
                    )
                    if created:
                        states_created += 1

            self.stdout.write(
                self.style.SUCCESS(f'Created {states_created} states')
            )

            # Load cities
            self.stdout.write('Loading cities...')
            cities_created = 0
            with open(cities_file, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        state = State.objects.get(code=row['codigo_uf'])
                        city, created = City.objects.get_or_create(
                            ibge_code=row['codigo_ibge'],
                            defaults={
                                'name': row['nome'],
                                'latitude': float(row['latitude']),
                                'longitude': float(row['longitude']),
                                'is_capital': bool(int(row['capital'])),
                                'state': state,
                                'siafi_id': row['siafi_id'],
                                'area_code': row['ddd'],
                                'timezone': row['fuso_horario'],
                            }
                        )
                        if created:
                            cities_created += 1
                    except State.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(
                                f'State with code {row["codigo_uf"]} not found for city {row["nome"]}'
                            )
                        )

            self.stdout.write(
                self.style.SUCCESS(f'Created {cities_created} cities')
            )

        self.stdout.write(
            self.style.SUCCESS('Geographic data loaded successfully!')
        )
