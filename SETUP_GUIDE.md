# Complete Setup Guide - Fuel Route Optimizer API

This guide will walk you through setting up and testing the Fuel Route Optimizer API from scratch.

## Prerequisites

- Python 3.13+ installed
- Git (for version control)
- Postman or similar API testing tool
- Google Cloud account (for Maps API)

## Step 1: Get Google Maps API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - **Directions API**
   - **Geocoding API**
   - **Maps Static API** (optional, for map visualization)
4. Go to "Credentials" → "Create Credentials" → "API Key"
5. Copy your API key
6. (Recommended) Restrict the API key to only the enabled APIs

**Note**: Google provides $200 free credit per month. This API is designed to minimize API calls through caching.

## Step 2: Configure Environment Variables

Edit the `.env` file in the project root and add your Google Maps API key:

```env
VITE_SUPABASE_URL=https://bsujldjbnzkevfdviycw.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
GOOGLE_MAPS_API_KEY=YOUR_GOOGLE_MAPS_API_KEY_HERE
```

Replace `YOUR_GOOGLE_MAPS_API_KEY_HERE` with your actual API key.

## Step 3: Install Dependencies

```bash
# Activate virtual environment (if not already activated)
source venv/bin/activate

# Install all required packages
pip install -r requirements.txt
```

## Step 4: Verify Database Connection

Run the test script to ensure database is properly configured:

```bash
python test_api.py
```

You should see:
```
Found 51 fuel stations in database
✅ Database connection successful!
```

## Step 5: Start the Django Server

```bash
python manage.py runserver
```

You should see:
```
Starting development server at http://127.0.0.1:8000/
```

Leave this terminal running.

## Step 6: Test the API

### Option A: Using cURL

Open a new terminal and run:

```bash
curl -X POST http://localhost:8000/api/calculate-route/ \
  -H "Content-Type: application/json" \
  -d '{
    "start_location": "New York, NY",
    "end_location": "Boston, MA"
  }'
```

### Option B: Using Postman

1. Open Postman
2. Create a new POST request
3. Set URL: `http://localhost:8000/api/calculate-route/`
4. Go to "Headers" tab:
   - Key: `Content-Type`
   - Value: `application/json`
5. Go to "Body" tab:
   - Select "raw"
   - Select "JSON" from dropdown
   - Enter:
   ```json
   {
     "start_location": "New York, NY",
     "end_location": "Boston, MA"
   }
   ```
6. Click "Send"

### Expected Response

```json
{
  "start_location": "New York, NY, USA",
  "end_location": "Boston, MA, USA",
  "total_distance_miles": 215.8,
  "total_duration_seconds": 13200,
  "route_polyline": "encoded_polyline...",
  "fuel_stops": [],
  "total_fuel_cost": 91.74,
  "total_gallons_needed": 21.58,
  "map_url": "https://maps.googleapis.com/..."
}
```

**Note**: For this short route (215 miles), no fuel stops are needed since it's under the 500-mile range.

### Test with Long Route

Try a longer route that requires fuel stops:

```json
{
  "start_location": "New York, NY",
  "end_location": "Los Angeles, CA"
}
```

Expected response will include multiple fuel stops with:
- Station details
- Fuel prices
- Gallons needed at each stop
- Total fuel cost

## Step 7: Verify All Features

### Test 1: Health Check
```bash
curl http://localhost:8000/api/health/
```

Expected: `{"status": "ok", "message": "Fuel Route API is running"}`

### Test 2: Short Route (No fuel stops)
- Start: "Philadelphia, PA"
- End: "Washington, DC"
- Expected: 0 fuel stops (under 500 miles)

### Test 3: Long Route (Multiple fuel stops)
- Start: "Seattle, WA"
- End: "Miami, FL"
- Expected: Multiple fuel stops with cost calculations

### Test 4: Invalid Input
```json
{
  "start_location": "",
  "end_location": "Boston, MA"
}
```

Expected: 400 error with validation message

### Test 5: Cache Performance
- Send the same request twice
- First request: ~2-3 seconds
- Second request: ~50-100ms (cached)

## Troubleshooting

### Issue: "Could not geocode location"
**Solution**: Verify your Google Maps API key is correct and Geocoding API is enabled.

### Issue: "No fuel station data available"
**Solution**: Import data using:
```bash
python manage.py import_fuel_data sample_fuel_prices.csv
```

### Issue: "Connection refused" or database errors
**Solution**: Check that the Supabase connection details in `.env` are correct.

### Issue: Rate limit exceeded
**Solution**: Google Maps has usage limits. Wait a few minutes or enable billing on your Google Cloud account.

## Adding Your Own Fuel Price Data

### CSV Format Required:
```csv
station_name,address,city,state,zip_code,latitude,longitude,fuel_price
Shell,123 Main St,New York,NY,10001,40.7589,-73.9851,4.25
```

### Import Command:
```bash
python manage.py import_fuel_data your_data.csv
```

## Performance Tips

1. **Caching**: Responses are cached for 1 hour. Same route queries are instant.
2. **API Calls**: Only 1 Google Maps API call per unique route.
3. **Database**: Indexed for fast geographic queries.

## Production Deployment Checklist

- [ ] Set `DEBUG = False` in settings.py
- [ ] Change `SECRET_KEY` to a secure random value
- [ ] Set `ALLOWED_HOSTS` appropriately
- [ ] Use production database with connection pooling
- [ ] Enable HTTPS
- [ ] Use Redis for caching instead of local memory
- [ ] Set up monitoring and logging
- [ ] Implement rate limiting
- [ ] Enable database backups

## API Usage Examples

### Example 1: Cross-country Trip
```json
{
  "start_location": "San Francisco, CA",
  "end_location": "New York, NY"
}
```

### Example 2: Regional Trip
```json
{
  "start_location": "Austin, TX",
  "end_location": "Denver, CO"
}
```

### Example 3: City-to-City
```json
{
  "start_location": "Chicago, IL",
  "end_location": "Detroit, MI"
}
```

## Understanding the Response

### Key Fields:

- **total_distance_miles**: Total trip distance
- **total_duration_seconds**: Estimated driving time
- **route_polyline**: Encoded route path (can be decoded for mapping)
- **fuel_stops**: Array of recommended fuel stops with:
  - Location details
  - Fuel price at that station
  - How much to fill up
  - Cost at that stop
  - Distance from main route
- **total_fuel_cost**: Total estimated fuel expense
- **total_gallons_needed**: Total fuel consumption (at 10 MPG)

## Next Steps

1. Create a Loom video demonstrating the API in Postman
2. Show code overview in the video
3. Share the project code
4. Provide the Loom link

## Support

For questions or issues:
1. Check the API_DOCUMENTATION.md for detailed API specs
2. Review the code comments in each module
3. Verify environment variables are set correctly

---

**Good luck with your Django Developer assignment!** 🚀
