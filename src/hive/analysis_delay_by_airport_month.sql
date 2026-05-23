WITH known_departure_delay AS (
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
cancelled_no_departure_delay AS (
  SELECT
    origin_airport,
    month,
    departure_delay,
    arrival_delay,
    'cancelled_no_departure_delay' AS delay_range,
    concat('cancellation:', coalesce(cancellation_code, 'unknown')) AS derived_cause
  FROM flight_delay.flights_2024_clean
  WHERE cancelled = 1 AND departure_delay IS NULL
),
ranged AS (
  SELECT * FROM known_departure_delay
  UNION ALL
  SELECT * FROM cancelled_no_departure_delay
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
    cause_count,
    row_number() OVER (
      PARTITION BY origin_airport, month, delay_range
      ORDER BY cause_count DESC, derived_cause ASC
    ) AS cause_rank
  FROM cause_counts
),
top_causes AS (
  SELECT
    origin_airport,
    month,
    delay_range,
    max(CASE WHEN cause_rank = 1 THEN derived_cause END) AS top_1_cause,
    coalesce(max(CASE WHEN cause_rank = 1 THEN cause_count END), 0) AS top_1_count,
    max(CASE WHEN cause_rank = 2 THEN derived_cause END) AS top_2_cause,
    coalesce(max(CASE WHEN cause_rank = 2 THEN cause_count END), 0) AS top_2_count,
    max(CASE WHEN cause_rank = 3 THEN derived_cause END) AS top_3_cause,
    coalesce(max(CASE WHEN cause_rank = 3 THEN cause_count END), 0) AS top_3_count
  FROM ranked_causes
  WHERE cause_rank <= 3
  GROUP BY origin_airport, month, delay_range
)
SELECT
  grouped.origin_airport,
  grouped.month,
  grouped.delay_range,
  grouped.flight_count,
  grouped.avg_departure_delay,
  grouped.avg_arrival_delay,
  top_causes.top_1_cause,
  coalesce(top_causes.top_1_count, 0) AS top_1_count,
  top_causes.top_2_cause,
  coalesce(top_causes.top_2_count, 0) AS top_2_count,
  top_causes.top_3_cause,
  coalesce(top_causes.top_3_count, 0) AS top_3_count
FROM grouped
LEFT JOIN top_causes
  ON grouped.origin_airport = top_causes.origin_airport
  AND grouped.month = top_causes.month
  AND grouped.delay_range = top_causes.delay_range
ORDER BY
  grouped.origin_airport,
  grouped.month,
  CASE grouped.delay_range
    WHEN 'cancelled_no_departure_delay' THEN 0
    WHEN 'low' THEN 1
    WHEN 'medium' THEN 2
    WHEN 'high' THEN 3
    ELSE 4
  END,
  grouped.delay_range;
