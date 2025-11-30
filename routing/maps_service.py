import requests
from django.conf import settings
from django.core.cache import cache

class MapsService:

    def __init__(self):
        self.api_key = settings.GOOGLE_MAPS_API_KEY
        self.base_url = "https://maps.googleapis.com/maps/api"

    def geocode_location(self, location):
        cache_key = f"geocode_{location}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result

        url = f"{self.base_url}/geocode/json"
        params = {
            'address': location,
            'key': self.api_key,
            'components': 'country:US'
        }

        response = requests.get(url, params=params)
        data = response.json()

        if data.get('status') == 'OK' and data.get('results'):
            result = {
                'lat': data['results'][0]['geometry']['location']['lat'],
                'lng': data['results'][0]['geometry']['location']['lng'],
                'formatted_address': data['results'][0]['formatted_address']
            }
            cache.set(cache_key, result, 86400)
            return result

        raise ValueError(f"Could not geocode location: {location}")

    def get_directions(self, origin, destination):
        cache_key = f"directions_{origin}_{destination}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result

        url = f"{self.base_url}/directions/json"
        params = {
            'origin': origin,
            'destination': destination,
            'key': self.api_key,
            'region': 'us'
        }

        response = requests.get(url, params=params)
        data = response.json()

        if data.get('status') == 'OK' and data.get('routes'):
            route = data['routes'][0]
            result = {
                'distance_meters': route['legs'][0]['distance']['value'],
                'distance_miles': route['legs'][0]['distance']['value'] * 0.000621371,
                'duration_seconds': route['legs'][0]['duration']['value'],
                'polyline': route['overview_polyline']['points'],
                'steps': route['legs'][0]['steps'],
                'start_location': route['legs'][0]['start_location'],
                'end_location': route['legs'][0]['end_location']
            }
            cache.set(cache_key, result, 86400)
            return result

        raise ValueError(f"Could not get directions from {origin} to {destination}")

    def decode_polyline(self, polyline_str):
        index = 0
        lat = 0
        lng = 0
        coordinates = []

        while index < len(polyline_str):
            shift = 0
            result = 0

            while True:
                b = ord(polyline_str[index]) - 63
                index += 1
                result |= (b & 0x1f) << shift
                shift += 5
                if b < 0x20:
                    break

            dlat = ~(result >> 1) if result & 1 else result >> 1
            lat += dlat

            shift = 0
            result = 0

            while True:
                b = ord(polyline_str[index]) - 63
                index += 1
                result |= (b & 0x1f) << shift
                shift += 5
                if b < 0x20:
                    break

            dlng = ~(result >> 1) if result & 1 else result >> 1
            lng += dlng

            coordinates.append({
                'lat': lat / 1e5,
                'lng': lng / 1e5
            })

        return coordinates
