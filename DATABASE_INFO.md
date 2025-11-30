# Database Information

## Fuel Stations Database

### Statistics
- **Total Stations**: 51
- **States Covered**: 19 (across the USA)
- **Price Range**: $3.35 - $5.20 per gallon
- **Average Price**: $3.99 per gallon

### States Covered
California, Colorado, Delaware, Florida, Georgia, Illinois, Massachusetts, Michigan, Missouri, Nebraska, New Jersey, New York, North Carolina, Ohio, Oklahoma, Pennsylvania, Tennessee, Texas, Wisconsin

### Price Distribution
- **Cheapest**: Loves in Oklahoma City, OK - $3.35/gallon
- **Most Expensive**: Shell in Palo Alto, CA - $5.20/gallon
- **Average**: $3.99/gallon

### Data Source
Sample fuel price data imported from `sample_fuel_prices.csv`

### Database Schema

```sql
CREATE TABLE fuel_stations (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  station_name text NOT NULL,
  address text NOT NULL,
  city text NOT NULL,
  state text NOT NULL,
  zip_code text NOT NULL,
  latitude numeric(10, 7) NOT NULL,
  longitude numeric(10, 7) NOT NULL,
  fuel_price numeric(6, 3) NOT NULL,
  last_updated timestamptz DEFAULT now(),
  created_at timestamptz DEFAULT now()
);
```

### Indexes
- `idx_fuel_stations_state` on `state`
- `idx_fuel_stations_location` on `(latitude, longitude)`
- `idx_fuel_stations_price` on `fuel_price`

### Security
- Row Level Security (RLS) enabled
- Public read access (fuel prices are public data)
- Controlled write access for data imports

### Performance
- Geographic queries optimized with spatial indexes
- Price-based sorting with dedicated index
- State-level filtering for regional queries

### Updating Data

To import new fuel price data:
```bash
python manage.py import_fuel_data your_fuel_data.csv
```

CSV format:
```csv
station_name,address,city,state,zip_code,latitude,longitude,fuel_price
```
