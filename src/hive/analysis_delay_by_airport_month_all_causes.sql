WITH known_departure_delay AS (
  SELECT
    origin_airport,
    month,
    cancelled,
    cancellation_code,
    carrier_delay,
    weather_delay,
    nas_delay,
    security_delay,
    late_aircraft_delay,
    CASE
      WHEN departure_delay < 15 THEN 'low'
      WHEN departure_delay >= 15 AND departure_delay <= 60 THEN 'medium'
      WHEN departure_delay > 60 THEN 'high'
    END AS delay_range
  FROM flight_delay.flights_2024_clean
  WHERE departure_delay IS NOT NULL
),
cancelled_no_departure_delay AS (
  SELECT
    origin_airport,
    month,
    cancelled,
    cancellation_code,
    carrier_delay,
    weather_delay,
    nas_delay,
    security_delay,
    late_aircraft_delay,
    'cancelled_no_departure_delay' AS delay_range
  FROM flight_delay.flights_2024_clean
  WHERE cancelled = 1 AND departure_delay IS NULL
),
ranged AS (
  SELECT * FROM known_departure_delay
  UNION ALL
  SELECT * FROM cancelled_no_departure_delay
),
cause_events AS (
  SELECT origin_airport, month, delay_range, 'delay:carrier' AS cause
  FROM ranged
  WHERE coalesce(carrier_delay, 0.0) > 0.0
  UNION ALL
  SELECT origin_airport, month, delay_range, 'delay:weather' AS cause
  FROM ranged
  WHERE coalesce(weather_delay, 0.0) > 0.0
  UNION ALL
  SELECT origin_airport, month, delay_range, 'delay:nas' AS cause
  FROM ranged
  WHERE coalesce(nas_delay, 0.0) > 0.0
  UNION ALL
  SELECT origin_airport, month, delay_range, 'delay:security' AS cause
  FROM ranged
  WHERE coalesce(security_delay, 0.0) > 0.0
  UNION ALL
  SELECT origin_airport, month, delay_range, 'delay:late_aircraft' AS cause
  FROM ranged
  WHERE coalesce(late_aircraft_delay, 0.0) > 0.0
  UNION ALL
  SELECT origin_airport, month, delay_range, concat('cancellation:', cancellation_code) AS cause
  FROM ranged
  WHERE cancelled = 1 AND cancellation_code IS NOT NULL
),
cause_counts AS (
  SELECT
    origin_airport,
    month,
    delay_range,
    cause,
    count(*) AS cause_count
  FROM cause_events
  GROUP BY origin_airport, month, delay_range, cause
),
ranked AS (
  SELECT
    origin_airport,
    month,
    delay_range,
    row_number() OVER (
      PARTITION BY origin_airport, month, delay_range
      ORDER BY cause_count DESC, cause ASC
    ) AS cause_rank,
    cause,
    cause_count
  FROM cause_counts
)
SELECT
  origin_airport,
  month,
  delay_range,
  cause_rank,
  cause,
  cause_count
FROM ranked
ORDER BY
  origin_airport,
  month,
  CASE delay_range
    WHEN 'cancelled_no_departure_delay' THEN 0
    WHEN 'low' THEN 1
    WHEN 'medium' THEN 2
    WHEN 'high' THEN 3
    ELSE 4
  END,
  delay_range,
  cause_rank,
  cause;
