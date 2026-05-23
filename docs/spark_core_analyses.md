# Spark Core Analyses

This document records the Spark Core implementation added in M5. The jobs read
the canonical prepared Parquet dataset from M3, reimplement the M4 Spark SQL
reference logic with RDD transformations, and write generated outputs under
`outputs/spark_core/`.

## Command

Run the Spark Core analyses from the repository root:

```powershell
make run-spark-core
```

On Windows, this stable command runs the Docker Compose Spark Core service
because native PySpark RDD workers are unstable in this environment. On
Linux/WSL/macOS, it runs the native Spark Core runner directly. The runner reads
Spark and path settings from `config/local.yaml`, configures Java and the
PySpark Python worker before importing PySpark, then runs a small RDD smoke
check before clearing old Spark Core outputs.

Spark Core writes its final aggregate CSV files locally with pandas after the
RDD analysis has produced the small result tables. This keeps the output layout
compatible with Spark SQL while avoiding Hadoop native-tool fragility for local
CSV writing on Windows. Spark SQL still uses Spark's CSV writer and may require
`winutils.exe` on Windows.

Run only the Spark Core RDD worker smoke check with:

```powershell
.\.venv\Scripts\python.exe src\spark_core\run_spark_core.py --smoke-rdd
```

Run the native Spark Core path directly for diagnostics with:

```powershell
make run-spark-core-native
```

If the native Windows smoke check fails with a PySpark worker-startup error, use
the stable Docker-backed command from the repository root:

```powershell
make run-spark-core
```

The Docker path uses the `spark-core` Compose service, which runs Python 3.12
and Java 17 inside Linux, mounts the repository at `/workspace`, and writes the
same `outputs/spark_core/` files as the native command. This is the accepted M5
evidence path on Windows.

WSL can also be used with the repository mounted at the same project root. For
example:

```bash
cd /mnt/c/Users/lucap/Documents/VSC\ Repository/flight-delay-big-data-analysis
make setup
make run-spark-core
```

## Output Layout

```text
outputs/spark_core/
  delay_by_airport_month/
    full/
    first_10.csv
  delay_by_airport_month_all_causes/
    full/
    first_10.csv
  airline_airport_ranking/
    full/
    first_10.csv
  runtime_metrics.json
```

Full outputs are CSV directories with a headered `part-00000.csv`. The
`first_10.csv` files are single CSV files with headers, intended for report
evidence and quick manual inspection. The output schemas match the Spark SQL
reference exactly.

Spark Core uses the same `small_result_collect_once` output materialization
policy as Spark SQL for these aggregate tables: collect the ordered small result
once to the driver, write `full/part-00000.csv`, and derive `first_10.csv` from
the same rows. Runtime metrics include run-level `input_read_seconds` and
job-level phase fields for plan construction, Spark result collection, full CSV
writing, and first-10 CSV writing. The Spark Core RDD worker smoke check remains
outside these benchmark phase fields.

## RDD Aggregation Strategy

The delay report assigns known `departure_delay` values to the same numeric
delay ranges as Spark SQL. Cancelled rows with null `departure_delay` are kept
in the supplementary `cancelled_no_departure_delay` bucket, while other null
departure-delay rows are excluded. It then derives cause labels and aggregates
with `reduceByKey`.
One keyed RDD computes flight counts and averages by `(origin_airport, month,
delay_range)`. A second keyed RDD counts causes by `(origin_airport, month,
delay_range, cause)`, sorts the reduced cause counts by count descending and
cause label ascending, and emits the first three causes. Groups with fewer than
three available causes are padded with null cause labels and `0` counts.

The companion all-positive cause job uses the same eligible flight population
but emits one event for every positive delay-cause field and one cancellation
event for cancelled flights with an available `cancellation_code`. It reduces by
`(origin_airport, month, delay_range, cause)`, ranks each group by count
descending and cause label ascending, and writes the normalized
`delay_by_airport_month_all_causes` schema.

The airline-airport ranking aggregates airline statistics with `reduceByKey` on
`(origin_airport, airline_code)` and airport averages with `reduceByKey` on
`origin_airport`. The two aggregated RDDs are joined by airport. Airline rows are
then collected into small per-airport lists with `combineByKey` so each airport
partition can be sorted and ranked with Spark SQL `RANK()` semantics.

The implementation avoids `groupByKey` for aggregation because the safer
patterns combine records map-side before shuffling. This reduces shuffled data
volume for repeated keys and keeps accumulator state compact.

Grouping, aggregation, joins, ranking, and final result ordering are RDD logic.
DataFrames are used only at the boundary to materialize stable schemas before
writing the small CSV result tables locally.

## Shuffle And Cost Examples

- Delay grouping shuffles compact accumulators per airport-month-range, not all
  flight records for the group.
- Delay cause counting performs a second shuffle because top-three cause
  selection is a separate grouped aggregate.
- Airline and airport statistics each shuffle once by their aggregation key, then
  the ranking job shuffles the compact aggregate rows for the airport join.
- Ranking requires per-airport sorting after aggregation; this is the lower-level
  RDD equivalent of Spark SQL's window function.
- Final output ordering performs one additional RDD sort so the generated CSV
  rows match Spark SQL's presentation order without using DataFrame `orderBy`.

## Validation

Validate generated Spark Core outputs against the Spark SQL reference with:

```powershell
.\.venv\Scripts\python.exe scripts\validate_spark_core_outputs.py
```

The validator checks duplicate keys, exact row counts, matching keys, exact
delay top-three cause labels and counts, ranking order, `rank_at_airport`, and
numeric fields within a `1e-6` tolerance.
