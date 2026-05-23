# Spark SQL Analyses

This document records the Spark SQL reference implementation added in M4. The
jobs read the canonical prepared Parquet dataset from M3 and write generated
outputs under `outputs/spark_sql/`.

## Command

Run the Spark SQL analyses from the repository root:

```powershell
make run-spark-sql
```

The command executes `src/spark_sql/run_spark_sql.py`, which reads Spark and path
settings from `config/local.yaml`. The script uses
`src.common.prepared_data.read_prepared_parquet()` so local Windows runs can read
the prepared Parquet directory even when Hadoop native tools are unavailable.

On Windows, Spark SQL output writing requires Hadoop `winutils.exe`. Set
`HADOOP_HOME` or `hadoop.home.dir` to a Hadoop directory containing
`bin\winutils.exe` before running `make run-spark-sql`. The job checks this
before clearing existing outputs and exits with an actionable preflight error if
the tool is missing.

## Output Layout

```text
outputs/spark_sql/
  delay_by_airport_month/
    full/
    first_10.csv
  airline_airport_ranking/
    full/
    first_10.csv
  runtime_metrics.json
```

Full outputs are Spark-written CSV directories with headers. The `first_10.csv`
files are single CSV files with headers, intended for report evidence and quick
manual inspection. All generated outputs remain ignored by Git.

## Delay Report By Airport, Month, And Delay Range

Stable output schema:

| Column | Type | Notes |
|---|---|---|
| origin_airport | string | Departure airport code. |
| month | int | Month number from the prepared dataset. |
| delay_range | string | One of `low`, `medium`, `high`, or `cancelled_no_departure_delay`. |
| flight_count | long | Count of flights in the airport-month-range group. |
| avg_departure_delay | double | Average departure delay; Spark SQL ignores nulls. |
| avg_arrival_delay | double | Average arrival delay; Spark SQL ignores nulls. |
| top_1_cause | string | Most frequent derived cause in the group. |
| top_1_count | long | Number of flights assigned to `top_1_cause`. |
| top_2_cause | string | Second most frequent derived cause, or null when unavailable. |
| top_2_count | long | Number of flights assigned to `top_2_cause`, or `0` when unavailable. |
| top_3_cause | string | Third most frequent derived cause, or null when unavailable. |
| top_3_count | long | Number of flights assigned to `top_3_cause`, or `0` when unavailable. |

Delay ranges are implemented as:

```text
low: departure_delay < 15
medium: 15 <= departure_delay <= 60
high: departure_delay > 60
```

Rows with known `departure_delay` use only the three numeric assignment ranges.
Cancelled rows with null `departure_delay` are reported separately in the
supplementary `cancelled_no_departure_delay` bucket. Other rows with null
`departure_delay` are excluded. Negative delays are preserved and fall into the
`low` bucket.

The cause field is derived per flight:

- Cancelled flights with a cancellation code use `cancellation:<code>`.
- Cancelled flights in the null-departure bucket without a code use
  `cancellation:unknown`.
- Otherwise, the largest positive delay-cause column is mapped to
  `delay:carrier`, `delay:weather`, `delay:nas`, `delay:security`, or
  `delay:late_aircraft`.
- Flights without a positive delay cause use `unknown`.

Spark SQL computes the top three causes with a grouped count and
`ROW_NUMBER() OVER (PARTITION BY origin_airport, month, delay_range ORDER BY
cause_count DESC, derived_cause ASC)`, which gives deterministic tie-breaking.
Groups with fewer than three available causes use null cause labels and `0`
counts for the missing slots.

## Airline-Airport Ranking

Stable output schema:

| Column | Type | Notes |
|---|---|---|
| origin_airport | string | Departure airport code. |
| airline | string | Airline code from `airline_code`. |
| flight_count | long | All prepared flights for the airport-airline pair. |
| avg_departure_delay | double | Average departure delay; Spark SQL ignores nulls. |
| avg_arrival_delay | double | Average arrival delay; Spark SQL ignores nulls. |
| cancellation_rate | double | Cancelled flights divided by all flights in the pair. |
| airport_avg_departure_delay | double | Airport-level average departure delay. |
| difference_from_airport_avg_departure_delay | double | Airline average minus airport average. |
| rank_at_airport | int | Airport-partitioned rank; rank 1 is best. |

The ranking job uses `airline_code` because the raw dataset does not provide a
stable airline-name field. Cancellation rates use all relevant prepared flights
as the denominator, including cancelled flights.

The rank is generated with:

```sql
RANK() OVER (
  PARTITION BY origin_airport
  ORDER BY avg_departure_delay ASC NULLS LAST
)
```

Equal average departure delays share the same rank. The final output is still
ordered deterministically by airport, rank, average delay, and airline code.

This makes Spark SQL the reference implementation for the later Spark Core and
Hive milestones, especially around SQL aggregation and window functions.

## Runtime Metrics

`outputs/spark_sql/runtime_metrics.json` captures:

- generation timestamp
- technology name
- input path
- Spark master and shuffle partition settings
- top-level run status
- one metrics object per attempted job with duration, row count, output paths,
  status, and error details for failed jobs

The runner is fail-fast: if one analysis fails, it writes metrics for completed
jobs plus the failed job, then exits nonzero without attempting later analyses.
These metrics are generated for reproducibility evidence. Later benchmark
milestones can build on the same job names and output paths.

Validate generated outputs with:

```powershell
.\.venv\Scripts\python.exe scripts\validate_spark_sql_outputs.py
```
