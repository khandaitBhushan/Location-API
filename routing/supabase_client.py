from supabase import create_client
from django.conf import settings

supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

def get_all_fuel_stations():
    response = supabase.table('fuel_stations').select('*').execute()
    return response.data

def get_fuel_stations_by_states(states):
    response = supabase.table('fuel_stations').select('*').in_('state', states).execute()
    return response.data

def bulk_insert_fuel_stations(stations):
    response = supabase.table('fuel_stations').insert(stations).execute()
    return response.data
