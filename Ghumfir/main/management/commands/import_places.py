from django.core.management.base import BaseCommand
import pandas as pd
from main.models import Place  


def parse_numeric(value):
    """
    Safely converts string or numeric input to a float.
    Handles ranges like '0.5-1' -> 0.75, returns None for invalid/empty data.
    """
    if value is None or str(value).strip() == '' or str(value).lower() == 'nan':
        return None
    try:
        value = str(value).strip()
        if '-' in value:
            parts = [float(p) for p in value.split('-') if p]
            if len(parts) == 2:
                return sum(parts) / 2
        return float(value)
    except Exception:
        return None


class Command(BaseCommand):
    help = "Import places data from an Excel file into the database"

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the Excel file')

    def handle(self, *args, **options):
        file_path = options['file_path']
        df = pd.read_excel(file_path)

        # Normalize column names (trim spaces)
        df.columns = df.columns.str.strip()

        imported_count = 0

        for _, row in df.iterrows():
            try:
                Place.objects.update_or_create(
                    name=row['Place Name'].strip(),
                    defaults={
                        'region': row.get('Region/District', ''),
                        'destination_type': row.get('Type of Destination', ''),
                        'popularity': row.get('Popularity', ''),
                        'best_season': row.get('Best Season to Visit', ''),
                        'starting_point': row.get('Starting Point', ''),
                        'route_overview': row.get('Route Overview', ''),
                        'ending_point': row.get('Ending Point', ''),
                        'duration_days': parse_numeric(row.get('Duration (Days)', None)),
                        'altitude_m': parse_numeric(row.get('Altitude/Elevation (Meters)', None)),
                        'difficulty': row.get('Difficulty Level', ''),
                        'transportation_access': row.get('Transportation Access', ''),
                        'lodges_hotels': row.get('Available Lodges/Hotels', ''),
                        'food_availability': row.get('Food Availability', ''),
                        'permit_required': str(row.get('Permit Required', '')).lower() in ['yes', 'true', 'y'],
                        'emergency_facilities': row.get('Emergency Facilities', ''),
                        'local_community': row.get('Local Community/Ethnic Group', ''),
                        'cultural_attractions': row.get('Cultural Attractions', ''),
                        'language_customs': row.get('Language & Customs', ''),
                        'unique_traditions': row.get('Unique Traditions', ''),
                        'adventure_type': row.get('Adventure Type', ''),
                        'not_to_miss_spots': row.get('Not-to-Miss Spots', ''),
                        'wildlife_highlights': row.get('Wildlife/Nature Highlights', ''),
                        'photography_hotspots': row.get('Photography Hotspots', ''),
                        'latitude': parse_numeric(row.get('Latitude', None)),
                        'longitude': parse_numeric(row.get('Longitude', None)),
                    }
                )
                imported_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error importing {row['Place Name']}: {e}"))

        self.stdout.write(self.style.SUCCESS(f"✅ Successfully imported {imported_count} places"))
