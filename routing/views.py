from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
import hashlib
import json

from .serializers import RouteRequestSerializer, RouteResponseSerializer
from .maps_service import MapsService
from .fuel_optimizer import FuelOptimizer
from .supabase_client import get_all_fuel_stations

class FuelRouteAPIView(APIView):

    def post(self, request):
        serializer = RouteRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'error': 'Invalid request data',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        start_location = serializer.validated_data['start_location']
        end_location = serializer.validated_data['end_location']

        cache_key = hashlib.md5(
            f"{start_location}_{end_location}".encode()
        ).hexdigest()
        cached_response = cache.get(cache_key)

        if cached_response:
            return Response(cached_response, status=status.HTTP_200_OK)

        try:
            maps_service = MapsService()

            start_coords = maps_service.geocode_location(start_location)
            end_coords = maps_service.geocode_location(end_location)

            directions = maps_service.get_directions(start_location, end_location)

            route_coordinates = maps_service.decode_polyline(directions['polyline'])

            fuel_stations = get_all_fuel_stations()

            if not fuel_stations:
                return Response({
                    'error': 'No fuel station data available. Please import fuel prices first.'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

            optimizer = FuelOptimizer(max_range_miles=500, mpg=10)

            fuel_stops, total_fuel_cost = optimizer.optimize_fuel_stops(
                route_coordinates,
                fuel_stations,
                directions['distance_miles']
            )

            total_gallons_needed = directions['distance_miles'] / 10

            markers = []
            if fuel_stops:
                for idx, stop in enumerate(fuel_stops):
                    markers.append(f"markers=color:red%7Clabel:{idx+1}%7C{stop['latitude']},{stop['longitude']}")

            markers_str = '&'.join(markers) if markers else ''
            map_url = (
                f"https://maps.googleapis.com/maps/api/staticmap?"
                f"size=800x600&path=enc:{directions['polyline']}&"
                f"{markers_str}&key=YOUR_API_KEY"
            )

            response_data = {
                'start_location': start_coords['formatted_address'],
                'end_location': end_coords['formatted_address'],
                'total_distance_miles': round(directions['distance_miles'], 2),
                'total_duration_seconds': directions['duration_seconds'],
                'route_polyline': directions['polyline'],
                'fuel_stops': fuel_stops,
                'total_fuel_cost': total_fuel_cost,
                'total_gallons_needed': round(total_gallons_needed, 2),
                'map_url': map_url
            }

            response_serializer = RouteResponseSerializer(data=response_data)
            if response_serializer.is_valid():
                cache.set(cache_key, response_serializer.validated_data, 3600)
                return Response(response_serializer.validated_data, status=status.HTTP_200_OK)
            else:
                return Response(response_data, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': 'An unexpected error occurred',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class HealthCheckView(APIView):

    def get(self, request):
        return Response({
            'status': 'ok',
            'message': 'Fuel Route API is running'
        }, status=status.HTTP_200_OK)
