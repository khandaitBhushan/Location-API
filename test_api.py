import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fuel_route_api.settings')
django.setup()

from routing.supabase_client import get_all_fuel_stations

print("Testing database connection and data...")
stations = get_all_fuel_stations()
print(f"Found {len(stations)} fuel stations in database")

if stations:
    print(f"\nSample station:")
    print(f"  Name: {stations[0]['station_name']}")
    print(f"  City: {stations[0]['city']}, {stations[0]['state']}")
    print(f"  Price: ${stations[0]['fuel_price']}/gallon")
    print(f"  Location: {stations[0]['latitude']}, {stations[0]['longitude']}")

print("\n✅ Database connection successful!")
print("\nTo test the API:")
print("1. Ensure you have a Google Maps API key in your .env file:")
print("   GOOGLE_MAPS_API_KEY=your_api_key_here")
print("\n2. Start the server:")
print("   python manage.py runserver")
print("\n3. Send a POST request to http://localhost:8000/api/calculate-route/")
print("   with JSON body:")
print('   {"start_location": "New York, NY", "end_location": "Boston, MA"}')
