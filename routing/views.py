import os
import math
import json
import requests
import pandas as pd
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

_SIMPLE_CACHE = {}

BASE_DIR = settings.BASE_DIR
FUEL_CSV = os.path.join(BASE_DIR, "sample_fuel_prices.csv")
OSRM_BASE = os.getenv("OSRM_BASE_URL", "https://router.project-osrm.org")

VEHICLE_RANGE_MILES = 500.0
MPG = 10.0
TANK_CAPACITY_GALLONS = VEHICLE_RANGE_MILES / MPG
SEARCH_RADIUS_MILES = 10.0

def haversine_miles(lat1, lon1, lat2, lon2):
    R = 3958.8
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.asin(math.sqrt(a))

def geocode(address):
    geolocator = Nominatim(user_agent="location_api_bhushan")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    loc = geocode(address)
    if loc is None:
        return None
    return (loc.latitude, loc.longitude)

def call_osrm_route(start_lat, start_lon, end_lat, end_lon):
    coords = f"{start_lon},{start_lat};{end_lon},{end_lat}"
    url = f"{OSRM_BASE}/route/v1/driving/{coords}"
    params = {"overview": "full", "geometries": "geojson", "steps": "false"}
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    data = r.json()
    routes = data.get("routes", [])
    if not routes:
        raise ValueError("No route returned by OSRM")
    feat = routes[0]
    distance_m = feat["distance"]
    geometry = feat["geometry"]["coordinates"]
    route_points = [(pt[1], pt[0]) for pt in geometry]
    return distance_m, route_points

def points_along_route(route_points, total_miles, segment_miles=VEHICLE_RANGE_MILES):
    points = []
    acc = 0.0
    last = route_points[0]
    traveled = 0.0
    for i in range(1, len(route_points)):
        cur = route_points[i]
        d = haversine_miles(last[0], last[1], cur[0], cur[1])
        acc += d
        traveled += d
        if acc >= segment_miles and traveled < total_miles - 1.0:
            points.append(cur)
            acc = 0.0
        last = cur
    return points

def load_fuel_df():
    if not os.path.exists(FUEL_CSV):
        raise FileNotFoundError(f"Fuel CSV not found at {FUEL_CSV}")
    df = pd.read_csv(FUEL_CSV)
    for col in df.columns:
        df.rename(columns={col: col.strip()}, inplace=True)
    df["latitude"] = df["latitude"].astype(float)
    df["longitude"] = df["longitude"].astype(float)
    if "fuel_price" in df.columns:
        df = df.rename(columns={"fuel_price": "price_per_gallon"})
    df["price_per_gallon"] = df["price_per_gallon"].astype(float)
    return df

def find_cheapest_near(lat, lon, fuel_df, radius=SEARCH_RADIUS_MILES):
    df = fuel_df.copy()
    df["dist"] = df.apply(lambda r: haversine_miles(lat, lon, r.latitude, r.longitude), axis=1)
    near = df[df["dist"] <= radius]
    if near.empty:
        row = df.sort_values("price_per_gallon").iloc[0]
    else:
        row = near.sort_values("price_per_gallon").iloc[0]
    return {
        "station_name": row.get("station_name", "Unknown"),
        "latitude": float(row.latitude),
        "longitude": float(row.longitude),
        "price_per_gallon": float(row.price_per_gallon),
        "distance_from_point_miles": float(row.dist)
    }

@csrf_exempt
def calculate_route(request):
    if request.method != "POST":
        return JsonResponse({"error": "Use POST"}, status=405)
    try:
        body = json.loads(request.body)
        start = body.get("start")
        end = body.get("end")
        if not start or not end:
            return JsonResponse({"error": "start & end required"}, status=400)

        start_ll = geocode(start)
        end_ll = geocode(end)
        if not start_ll or not end_ll:
            return JsonResponse({"error": "Geocoding failed for start or end"}, status=400)

        cache_key = f"{start}|{end}"
        if cache_key in _SIMPLE_CACHE:
            distance_m, route_points = _SIMPLE_CACHE[cache_key]
        else:
            distance_m, route_points = call_osrm_route(start_ll[0], start_ll[1], end_ll[0], end_ll[1])
            _SIMPLE_CACHE[cache_key] = (distance_m, route_points)

        distance_miles = distance_m / 1609.344
        total_gallons = distance_miles / MPG

        fuel_df = load_fuel_df()
        stop_points = points_along_route(route_points, distance_miles)
        fuel_stops = []
        gallons_remaining = total_gallons

        for idx, p in enumerate(stop_points):
            lat, lon = p[0], p[1]
            station = find_cheapest_near(lat, lon, fuel_df)
            gallons_to_fill = min(TANK_CAPACITY_GALLONS, max(0.0, gallons_remaining))
            cost = gallons_to_fill * station["price_per_gallon"]
            fuel_stops.append({
                "stop_index": idx + 1,
                "station_name": station["station_name"],
                "latitude": station["latitude"],
                "longitude": station["longitude"],
                "price_per_gallon": round(station["price_per_gallon"], 3),
                "distance_from_route_point_miles": round(station["distance_from_point_miles"], 3),
                "gallons_filled": round(gallons_to_fill, 2),
                "cost_at_this_stop": round(cost, 2)
            })
            gallons_remaining -= gallons_to_fill
            if gallons_remaining <= 0:
                break

        if not fuel_stops:
            station = find_cheapest_near(end_ll[0], end_ll[1], fuel_df)
            gallons_needed = total_gallons
            fuel_stops.append({
                "stop_index": 1,
                "station_name": station["station_name"],
                "latitude": station["latitude"],
                "longitude": station["longitude"],
                "price_per_gallon": round(station["price_per_gallon"], 3),
                "distance_from_route_point_miles": round(station["distance_from_point_miles"], 3),
                "gallons_filled": round(gallons_needed, 2),
                "cost_at_this_stop": round(gallons_needed * station["price_per_gallon"], 2)
            })

        total_cost = sum(s["cost_at_this_stop"] for s in fuel_stops)
        preview_points = route_points[:50]

        resp = {
            "start": start,
            "end": end,
            "start_latlon": {"lat": start_ll[0], "lon": start_ll[1]},
            "end_latlon": {"lat": end_ll[0], "lon": end_ll[1]},
            "total_distance_miles": round(distance_miles, 2),
            "total_gallons_needed": round(total_gallons, 2),
            "fuel_stops": fuel_stops,
            "total_cost_usd": round(total_cost, 2),
            "route_coordinates": preview_points
        }
        return JsonResponse(resp, status=200, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
