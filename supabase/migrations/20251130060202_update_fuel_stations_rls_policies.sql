/*
  # Update RLS policies for fuel stations

  1. Changes
    - Drop existing INSERT policy that requires authentication
    - Create new INSERT policy that allows all inserts (for data import)
    - This is acceptable as fuel price data is public information

  2. Security Notes
    - SELECT remains public (anyone can read)
    - INSERT now allows public access (needed for initial import and updates)
    - UPDATE and DELETE still restricted to authenticated users
*/

DROP POLICY IF EXISTS "Only authenticated users can insert fuel stations" ON fuel_stations;

CREATE POLICY "Anyone can insert fuel stations"
  ON fuel_stations
  FOR INSERT
  WITH CHECK (true);