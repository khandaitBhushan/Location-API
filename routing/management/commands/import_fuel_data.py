from django.core.management.base import BaseCommand
import csv
import random
from routing.supabase_client import bulk_insert_fuel_stations

class Command(BaseCommand):
    help = 'Import fuel station data from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to CSV file with fuel prices')

    def handle(self, *args, **options):
        csv_file = options['csv_file']

        stations = []
        try:
            with open(csv_file, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    station = {
                        'station_name': row.get('station_name', row.get('name', 'Unknown Station')),
                        'address': row.get('address', row.get('street', '')),
                        'city': row.get('city', ''),
                        'state': row.get('state', ''),
                        'zip_code': row.get('zip_code', row.get('zip', '')),
                        'latitude': float(row.get('latitude', row.get('lat', 0))),
                        'longitude': float(row.get('longitude', row.get('lng', row.get('lon', 0)))),
                        'fuel_price': float(row.get('fuel_price', row.get('price', random.uniform(3.0, 5.0)))),
                    }
                    stations.append(station)

            if stations:
                bulk_insert_fuel_stations(stations)
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully imported {len(stations)} fuel stations')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('No stations found in CSV file')
                )

        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f'File not found: {csv_file}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error importing data: {str(e)}')
            )
