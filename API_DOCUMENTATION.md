# Fuel Route Optimizer API

A Django REST API that calculates optimal fuel stops for road trips across the USA based on cost-effectiveness and vehicle range constraints.

## Overview

This API takes a start and end location within the USA, calculates the route, and returns optimal fuel stops along the way. It considers:
- Vehicle range (500 miles maximum)
- Fuel prices at different locations
- Route distance and duration
- Cost-effectiveness (prioritizes cheaper fuel)

## Requirements Met

✅ **Django**: Built with Django 5.2.8 and Django REST Framework
✅ **Input**: Accepts start and finish locations within USA
✅ **Route Map**: Returns route polyline for map visualization
✅ **Optimal Fuel Stops**: Calculates cost-effective stops based on fuel prices
✅ **Range Constraint**: Handles 500-mile maximum range with multiple stops
✅ **Fuel Cost**: Returns total money spent assuming 10 MPG
✅ **Performance**: Uses caching to minimize external API calls (1 call per unique route)
✅ **Fast Response**: Cached responses are instant; initial calculation is optimized

## Technology Stack

- **Framework**: Django 5.2.8
- **API**: Django REST Framework 3.16.1
- **Database**: PostgreSQL (Supabase)
- **Mapping**: Google Maps Directions & Geocoding API
- **Caching**: Django Local Memory Cache
- **Python**: 3.13.5

## Setup Instructions

### 1. Prerequisites

- Python 3.13+
- PostgreSQL database (Supabase provided)
- Google Maps API key

### 2. Environment Variables

Create a `.env` file in the project root:

```env
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_DB_PASSWORD=your_database_password
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
```

### 3. Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install django djangorestframework django-cors-headers psycopg2-binary requests python-dotenv supabase

# Run migrations
python manage.py migrate

# Import fuel price data
python manage.py import_fuel_data sample_fuel_prices.csv

# Start development server
python manage.py runserver
```

## API Endpoints

### 1. Calculate Route with Fuel Stops

**Endpoint**: `POST /api/calculate-route/`

**Description**: Calculates the optimal route with fuel stops between two locations in the USA.

**Request Body**:
```json
{
  "start_location": "New York, NY",
  "end_location": "Los Angeles, CA"
}
```

**Response** (200 OK):
```json
{
  "start_location": "New York, NY, USA",
  "end_location": "Los Angeles, CA, USA",
  "total_distance_miles": 2789.5,
  "total_duration_seconds": 147600,
  "route_polyline": "encoded_polyline_string...",
  "fuel_stops": [
    {
      "station_name": "Shell",
      "address": "123 Main St",
      "city": "Chicago",
      "state": "IL",
      "latitude": 41.8781,
      "longitude": -87.6298,
      "fuel_price": 3.95,
      "gallons_to_fill": 50.0,
      "cost_at_station": 197.50,
      "distance_from_route": 2.3
    },
    {
      "station_name": "Valero",
      "address": "987 Congress Ave",
      "city": "Denver",
      "state": "CO",
      "latitude": 39.7392,
      "longitude": -104.9903,
      "fuel_price": 3.95,
      "gallons_to_fill": 50.0,
      "cost_at_station": 197.50,
      "distance_from_route": 1.8
    }
  ],
  "total_fuel_cost": 1102.35,
  "total_gallons_needed": 278.95,
  "map_url": "https://maps.googleapis.com/maps/api/staticmap?..."
}
```

**Error Responses**:

400 Bad Request:
```json
{
  "error": "Invalid request data",
  "details": {
    "start_location": ["This field is required."]
  }
}
```

503 Service Unavailable:
```json
{
  "error": "No fuel station data available. Please import fuel prices first."
}
```

### 2. Health Check

**Endpoint**: `GET /api/health/`

**Response** (200 OK):
```json
{
  "status": "ok",
  "message": "Fuel Route API is running"
}
```

## Algorithm Explanation

### Route Calculation
1. Geocodes start and end locations using Google Maps Geocoding API
2. Retrieves route data using Google Maps Directions API (1 call)
3. Decodes the polyline to get coordinate points along the route

### Fuel Stop Optimization
1. Divides the route into segments based on 500-mile range
2. For each segment, identifies the optimal refueling point:
   - Searches nearby stations (within 30 miles of route)
   - Prioritizes stations by fuel price
   - Considers distance from route as secondary factor
3. Calculates total fuel cost assuming 10 MPG consumption

### Performance Optimization
- **Caching**: Route calculations are cached for 1 hour
- **Single API Call**: Only 1 call to Google Maps Directions API per unique route
- **Efficient Queries**: Database queries are optimized with indexes on latitude, longitude, state, and price

## Database Schema

### fuel_stations Table

| Column | Type | Description |
|--------|------|-------------|
| id | uuid | Primary key |
| station_name | text | Station name |
| address | text | Street address |
| city | text | City name |
| state | text | State abbreviation |
| zip_code | text | ZIP code |
| latitude | numeric(10,7) | Geographic latitude |
| longitude | numeric(10,7) | Geographic longitude |
| fuel_price | numeric(6,3) | Price per gallon (USD) |
| last_updated | timestamptz | Last price update |
| created_at | timestamptz | Record creation time |

### Indexes
- `idx_fuel_stations_state` on `state`
- `idx_fuel_stations_location` on `(latitude, longitude)`
- `idx_fuel_stations_price` on `fuel_price`

## Import Fuel Data

### CSV Format

The CSV file should have the following columns:
```csv
station_name,address,city,state,zip_code,latitude,longitude,fuel_price
Shell,123 Main St,New York,NY,10001,40.7589,-73.9851,4.25
```

### Import Command

```bash
python manage.py import_fuel_data path/to/your/fuel_prices.csv
```

## Testing with Postman

### Example Request

1. **Method**: POST
2. **URL**: `http://localhost:8000/api/calculate-route/`
3. **Headers**: `Content-Type: application/json`
4. **Body** (raw JSON):
```json
{
  "start_location": "New York, NY",
  "end_location": "Miami, FL"
}
```

### Example cURL

```bash
curl -X POST http://localhost:8000/api/calculate-route/ \
  -H "Content-Type: application/json" \
  -d '{
    "start_location": "San Francisco, CA",
    "end_location": "Seattle, WA"
  }'
```

## Performance Characteristics

- **First Request**: ~2-3 seconds (includes Google Maps API call)
- **Cached Request**: ~50-100ms (instant response from cache)
- **External API Calls**: 1 per unique route (Directions API)
- **Cache Duration**: 1 hour (configurable)

## Architecture Highlights

### Separation of Concerns
- **maps_service.py**: Handles all Google Maps API interactions
- **fuel_optimizer.py**: Contains fuel stop optimization algorithm
- **supabase_client.py**: Database operations wrapper
- **views.py**: API endpoints and request handling
- **serializers.py**: Request/response validation

### Error Handling
- Validates input locations
- Handles API failures gracefully
- Provides meaningful error messages
- Catches and logs exceptions

### Security
- Row Level Security (RLS) enabled on database
- CORS configured for cross-origin requests
- Environment variables for sensitive data
- Input validation on all endpoints

## Future Enhancements

- Real-time fuel price updates
- Alternative route suggestions
- Vehicle type and MPG customization
- Preferred fuel station brands
- Rest stop recommendations
- Weather and traffic considerations

## Support

For issues or questions, please refer to the code documentation or create an issue in the repository.
