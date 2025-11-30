# Quick Start Guide - 5 Minutes to Running API

## 1. Add Google Maps API Key (2 minutes)

Edit `.env` file:
```env
GOOGLE_MAPS_API_KEY=your_actual_api_key_here
```

Get a key at: https://console.cloud.google.com/
Enable: Directions API + Geocoding API

## 2. Start the Server (1 minute)

```bash
source venv/bin/activate
python manage.py runserver
```

## 3. Test in Postman (2 minutes)

**Import Collection**:
- File → Import → `Fuel_Route_API.postman_collection.json`

**Or Create Manual Request**:
- Method: POST
- URL: `http://localhost:8000/api/calculate-route/`
- Headers: `Content-Type: application/json`
- Body (raw JSON):
```json
{
  "start_location": "New York, NY",
  "end_location": "Miami, FL"
}
```

## Expected Response

```json
{
  "start_location": "New York, NY, USA",
  "end_location": "Miami, FL, USA",
  "total_distance_miles": 1280.5,
  "fuel_stops": [
    {
      "station_name": "ExxonMobil",
      "city": "Wilmington",
      "state": "NC",
      "fuel_price": 3.85,
      "cost_at_station": 192.50
    }
  ],
  "total_fuel_cost": 507.35,
  "total_gallons_needed": 128.05
}
```

## That's It!

✅ API is running and ready for your demo video

## Test Routes for Demo

1. **Short** (no stops): NY → Boston
2. **Medium** (1-2 stops): NY → Miami
3. **Long** (5+ stops): NY → Los Angeles

## Making Your Loom Video

1. Open Postman
2. Show 2-3 different routes
3. Explain the response data
4. Quick code tour (5 min max)
5. Done!

---

**Need Help?** See SETUP_GUIDE.md for detailed instructions.
