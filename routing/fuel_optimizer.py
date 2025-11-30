import math
from typing import List, Dict

class FuelOptimizer:

    def __init__(self, max_range_miles=500, mpg=10):
        self.max_range_miles = max_range_miles
        self.mpg = mpg

    def calculate_distance(self, lat1, lon1, lat2, lon2):
        R = 3959

        lat1_rad = math.radians(float(lat1))
        lat2_rad = math.radians(float(lat2))
        delta_lat = math.radians(float(lat2) - float(lat1))
        delta_lon = math.radians(float(lon2) - float(lon1))

        a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        distance = R * c
        return distance

    def find_nearby_stations(self, point_lat, point_lng, fuel_stations, max_distance_miles=50):
        nearby = []
        for station in fuel_stations:
            distance = self.calculate_distance(
                point_lat, point_lng,
                station['latitude'], station['longitude']
            )
            if distance <= max_distance_miles:
                nearby.append({
                    **station,
                    'distance_from_point': distance
                })

        return sorted(nearby, key=lambda x: (x['fuel_price'], x['distance_from_point']))

    def optimize_fuel_stops(self, route_coordinates: List[Dict], fuel_stations: List[Dict], total_distance_miles: float):
        if total_distance_miles <= self.max_range_miles:
            return [], 0

        fuel_stops = []
        current_fuel_range = self.max_range_miles
        cumulative_distance = 0
        total_cost = 0

        intervals = max(int(math.ceil(total_distance_miles / self.max_range_miles)), 2)
        segment_length = total_distance_miles / intervals

        for i in range(1, intervals):
            target_distance = segment_length * i
            target_index = min(
                int((target_distance / total_distance_miles) * len(route_coordinates)),
                len(route_coordinates) - 1
            )

            search_start = max(0, target_index - 50)
            search_end = min(len(route_coordinates), target_index + 50)

            best_station = None
            best_score = float('inf')

            for idx in range(search_start, search_end):
                coord = route_coordinates[idx]
                nearby_stations = self.find_nearby_stations(
                    coord['lat'], coord['lng'],
                    fuel_stations,
                    max_distance_miles=30
                )

                if nearby_stations:
                    station = nearby_stations[0]
                    score = station['fuel_price'] + (station['distance_from_point'] * 0.1)

                    if score < best_score:
                        best_score = score
                        best_station = station

            if best_station:
                gallons_needed = self.max_range_miles / self.mpg
                cost = gallons_needed * float(best_station['fuel_price'])
                total_cost += cost

                fuel_stops.append({
                    'station_name': best_station['station_name'],
                    'address': best_station['address'],
                    'city': best_station['city'],
                    'state': best_station['state'],
                    'latitude': float(best_station['latitude']),
                    'longitude': float(best_station['longitude']),
                    'fuel_price': float(best_station['fuel_price']),
                    'gallons_to_fill': round(gallons_needed, 2),
                    'cost_at_station': round(cost, 2),
                    'distance_from_route': round(best_station['distance_from_point'], 2)
                })

        if fuel_stops:
            remaining_distance = total_distance_miles - (len(fuel_stops) * self.max_range_miles)
            if remaining_distance > 0:
                last_fillup_gallons = remaining_distance / self.mpg
                last_station = fuel_stops[-1]
                additional_cost = last_fillup_gallons * last_station['fuel_price']
                total_cost += additional_cost
        else:
            total_gallons = total_distance_miles / self.mpg
            if fuel_stations:
                avg_price = sum(float(s['fuel_price']) for s in fuel_stations) / len(fuel_stations)
                total_cost = total_gallons * avg_price

        return fuel_stops, round(total_cost, 2)
