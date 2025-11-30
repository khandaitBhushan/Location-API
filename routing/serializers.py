from rest_framework import serializers

class RouteRequestSerializer(serializers.Serializer):
    start_location = serializers.CharField(max_length=500, required=True)
    end_location = serializers.CharField(max_length=500, required=True)

    def validate_start_location(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Start location cannot be empty")
        return value.strip()

    def validate_end_location(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("End location cannot be empty")
        return value.strip()

class FuelStopSerializer(serializers.Serializer):
    station_name = serializers.CharField()
    address = serializers.CharField()
    city = serializers.CharField()
    state = serializers.CharField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    fuel_price = serializers.FloatField()
    gallons_to_fill = serializers.FloatField()
    cost_at_station = serializers.FloatField()
    distance_from_route = serializers.FloatField()

class RouteResponseSerializer(serializers.Serializer):
    start_location = serializers.CharField()
    end_location = serializers.CharField()
    total_distance_miles = serializers.FloatField()
    total_duration_seconds = serializers.IntegerField()
    route_polyline = serializers.CharField()
    fuel_stops = FuelStopSerializer(many=True)
    total_fuel_cost = serializers.FloatField()
    total_gallons_needed = serializers.FloatField()
    map_url = serializers.CharField()
