/*
  # Create fuel stations table

  1. New Tables
    - `fuel_stations`
      - `id` (uuid, primary key) - Unique identifier for each fuel station
      - `station_name` (text) - Name of the fuel station
      - `address` (text) - Street address of the station
      - `city` (text) - City where station is located
      - `state` (text) - State abbreviation (e.g., CA, NY)
      - `zip_code` (text) - ZIP code
      - `latitude` (numeric) - Geographic latitude coordinate
      - `longitude` (numeric) - Geographic longitude coordinate
      - `fuel_price` (numeric) - Current fuel price per gallon in USD
      - `last_updated` (timestamptz) - Timestamp of last price update
      - `created_at` (timestamptz) - Record creation timestamp

  2. Indexes
    - Index on state for faster lookups by state
    - Spatial index on latitude/longitude for geographic queries
    - Index on fuel_price for price-based sorting

  3. Security
    - Enable RLS on `fuel_stations` table
    - Add policy for public read access (fuel prices are public data)
    - Restrict write access to authenticated users only
*/

CREATE TABLE IF NOT EXISTS fuel_stations (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  station_name text NOT NULL DEFAULT '',
  address text NOT NULL DEFAULT '',
  city text NOT NULL,
  state text NOT NULL,
  zip_code text NOT NULL DEFAULT '',
  latitude numeric(10, 7) NOT NULL,
  longitude numeric(10, 7) NOT NULL,
  fuel_price numeric(6, 3) NOT NULL,
  last_updated timestamptz DEFAULT now(),
  created_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_fuel_stations_state ON fuel_stations(state);
CREATE INDEX IF NOT EXISTS idx_fuel_stations_location ON fuel_stations(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_fuel_stations_price ON fuel_stations(fuel_price);

ALTER TABLE fuel_stations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can read fuel station data"
  ON fuel_stations
  FOR SELECT
  USING (true);

CREATE POLICY "Only authenticated users can insert fuel stations"
  ON fuel_stations
  FOR INSERT
  TO authenticated
  WITH CHECK (true);

CREATE POLICY "Only authenticated users can update fuel stations"
  ON fuel_stations
  FOR UPDATE
  TO authenticated
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Only authenticated users can delete fuel stations"
  ON fuel_stations
  FOR DELETE
  TO authenticated
  USING (true);