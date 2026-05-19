CREATE DATABASE IF NOT EXISTS flight_delay;

DROP TABLE IF EXISTS flight_delay.flights_2024_clean;

CREATE EXTERNAL TABLE flight_delay.flights_2024_clean (
  flight_date DATE,
  month INT,
  airline_code STRING,
  airline_name STRING,
  origin_airport STRING,
  destination_airport STRING,
  departure_delay DOUBLE,
  arrival_delay DOUBLE,
  cancelled INT,
  diverted INT,
  cancellation_code STRING,
  carrier_delay DOUBLE,
  weather_delay DOUBLE,
  nas_delay DOUBLE,
  security_delay DOUBLE,
  late_aircraft_delay DOUBLE
)
STORED AS PARQUET
LOCATION 'file:///workspace/data/prepared/flights_2024_clean.parquet'
TBLPROPERTIES ('external.table.purge'='false');
