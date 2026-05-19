WITH ranged AS (
  SELECT
    origin_airport,
    month,
    departure_delay,
    arrival_delay,
    CASE
      WHEN departure_delay < 15 THEN 'low'
      WHEN departure_delay >= 15 AND departure_delay <= 60 THEN 'medium'
      WHEN departure_delay > 60 THEN 'high'
    END AS delay_range,
    CASE
      WHEN cancelled = 1 AND cancellation_code IS NOT NULL
        THEN concat('cancellation:', cancellation_code)
      WHEN coalesce(carrier_delay, 0.0) <= 0.0
        AND coalesce(weather_delay, 0.0) <= 0.0
        AND coalesce(nas_delay, 0.0) <= 0.0
        AND coalesce(security_delay, 0.0) <= 0.0
        AND coalesce(late_aircraft_delay, 0.0) <= 0.0
        THEN 'unknown'
      WHEN coalesce(carrier_delay, 0.0) >= coalesce(weather_delay, 0.0)
        AND coalesce(carrier_delay, 0.0) >= coalesce(nas_delay, 0.0)
        AND coalesce(carrier_delay, 0.0) >= coalesce(security_delay, 0.0)
        AND coalesce(carrier_delay, 0.0) >= coalesce(late_aircraft_delay, 0.0)
        THEN 'delay:carrier'
      WHEN coalesce(weather_delay, 0.0) >= coalesce(nas_delay, 0.0)
        AND coalesce(weather_delay, 0.0) >= coalesce(security_delay, 0.0)
        AND coalesce(weather_delay, 0.0) >= coalesce(late_aircraft_delay, 0.0)
        THEN 'delay:weather'
      WHEN coalesce(nas_delay, 0.0) >= coalesce(security_delay, 0.0)
        AND coalesce(nas_delay, 0.0) >= coalesce(late_aircraft_delay, 0.0)
        THEN 'delay:nas'
      WHEN coalesce(security_delay, 0.0) >= coalesce(late_aircraft_delay, 0.0)
        THEN 'delay:security'
      ELSE 'delay:late_aircraft'
    END AS derived_cause
  FROM flight_delay.flights_2024_clean
  WHERE departure_delay IS NOT NULL
),
grouped AS (
  SELECT
    origin_airport,
    month,
    delay_range,
    count(*) AS flight_count,
    avg(departure_delay) AS avg_departure_delay,
    avg(arrival_delay) AS avg_arrival_delay
  FROM ranged
  GROUP BY origin_airport, month, delay_range
),
cause_counts AS (
  SELECT
    origin_airport,
    month,
    delay_range,
    derived_cause,
    count(*) AS cause_count
  FROM ranged
  GROUP BY origin_airport, month, delay_range, derived_cause
),
ranked_causes AS (
  SELECT
    origin_airport,
    month,
    delay_range,
    derived_cause,
    row_number() OVER (
      PARTITION BY origin_airport, month, delay_range
      ORDER BY cause_count DESC, derived_cause ASC
    ) AS cause_rank
  FROM cause_counts
)
SELECT
  grouped.origin_airport,
  grouped.month,
  grouped.delay_range,
  grouped.flight_count,
  grouped.avg_departure_delay,
  grouped.avg_arrival_delay,
  ranked_causes.derived_cause AS top_delay_or_cancellation_cause
FROM grouped
INNER JOIN ranked_causes
  ON grouped.origin_airport = ranked_causes.origin_airport
  AND grouped.month = ranked_causes.month
  AND grouped.delay_range = ranked_causes.delay_range
  AND ranked_causes.cause_rank = 1
ORDER BY grouped.origin_airport, grouped.month, grouped.delay_range;
