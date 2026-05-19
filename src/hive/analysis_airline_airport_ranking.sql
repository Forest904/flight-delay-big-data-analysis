WITH airline_stats AS (
  SELECT
    origin_airport,
    airline_code AS airline,
    count(*) AS flight_count,
    avg(departure_delay) AS avg_departure_delay,
    avg(arrival_delay) AS avg_arrival_delay,
    cast(sum(CASE WHEN cancelled = 1 THEN 1 ELSE 0 END) AS DOUBLE) / count(*) AS cancellation_rate
  FROM flight_delay.flights_2024_clean
  GROUP BY origin_airport, airline_code
),
airport_stats AS (
  SELECT
    origin_airport,
    avg(departure_delay) AS airport_avg_departure_delay
  FROM flight_delay.flights_2024_clean
  GROUP BY origin_airport
),
ranked AS (
  SELECT
    airline_stats.origin_airport,
    airline_stats.airline,
    airline_stats.flight_count,
    airline_stats.avg_departure_delay,
    airline_stats.avg_arrival_delay,
    airline_stats.cancellation_rate,
    airport_stats.airport_avg_departure_delay,
    airline_stats.avg_departure_delay - airport_stats.airport_avg_departure_delay
      AS difference_from_airport_avg_departure_delay,
    rank() OVER (
      PARTITION BY airline_stats.origin_airport
      ORDER BY
        CASE WHEN airline_stats.avg_departure_delay IS NULL THEN 1 ELSE 0 END,
        airline_stats.avg_departure_delay ASC
    ) AS rank_at_airport
  FROM airline_stats
  INNER JOIN airport_stats
    ON airline_stats.origin_airport = airport_stats.origin_airport
)
SELECT
  origin_airport,
  airline,
  flight_count,
  avg_departure_delay,
  avg_arrival_delay,
  cancellation_rate,
  airport_avg_departure_delay,
  difference_from_airport_avg_departure_delay,
  rank_at_airport
FROM ranked
ORDER BY
  origin_airport,
  rank_at_airport,
  CASE WHEN avg_departure_delay IS NULL THEN 1 ELSE 0 END,
  avg_departure_delay ASC,
  airline;
