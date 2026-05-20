# Data Preparation Notes

This document records the measured facts gathered before building the cleaning
pipeline and the implemented M3 preparation rules. The prepared Parquet dataset
is the canonical input for Spark SQL, Spark Core, and Hive analyses.

## Raw Dataset Source

- Source: Kaggle, `hrishitpatil/flight-data-2024`
- Local file: `data/raw/flight_data_2024.csv`
- Config path: `config/local.yaml` -> `paths.raw_file`
- File size: `1,309,010,752` bytes
- Kaggle credentials: not used for this run because the CSV was downloaded
  manually and placed in `data/raw/`
- Optional redownload instructions: `scripts/download_dataset.md`

## Inspection Command

Run the reproducible inspection from the project root:

```powershell
make inspect-raw
```

If `make` is not available on the local PATH, run the underlying command:

```powershell
.\.venv\Scripts\python.exe scripts\inspect_raw_dataset.py
```

## Raw Shape

- Row count: `7,079,081`
- Column count: `35`
- Header columns:

```text
year, month, day_of_month, day_of_week, fl_date, op_unique_carrier,
op_carrier_fl_num, origin, origin_city_name, origin_state_nm, dest,
dest_city_name, dest_state_nm, crs_dep_time, dep_time, dep_delay,
taxi_out, wheels_off, wheels_on, taxi_in, crs_arr_time, arr_time,
arr_delay, cancelled, cancellation_code, diverted, crs_elapsed_time,
actual_elapsed_time, air_time, distance, carrier_delay, weather_delay,
nas_delay, security_delay, late_aircraft_delay
```

## Inferred Raw Schema

| Column | Inferred type | Non-null rows |
|---|---:|---:|
| year | integer | 7,079,081 |
| month | integer | 7,079,081 |
| day_of_month | integer | 7,079,081 |
| day_of_week | integer | 7,079,081 |
| fl_date | date | 7,079,081 |
| op_unique_carrier | string | 7,079,081 |
| op_carrier_fl_num | float | 7,079,080 |
| origin | string | 7,079,081 |
| origin_city_name | string | 7,079,081 |
| origin_state_nm | string | 7,079,081 |
| dest | string | 7,079,081 |
| dest_city_name | string | 7,079,081 |
| dest_state_nm | string | 7,079,081 |
| crs_dep_time | integer | 7,079,081 |
| dep_time | float | 6,986,422 |
| dep_delay | float | 6,986,111 |
| taxi_out | float | 6,983,347 |
| wheels_off | float | 6,983,347 |
| wheels_on | float | 6,981,225 |
| taxi_in | float | 6,981,225 |
| crs_arr_time | integer | 7,079,081 |
| arr_time | float | 6,981,227 |
| arr_delay | float | 6,965,267 |
| cancelled | integer | 7,079,081 |
| cancellation_code | string | 96,315 |
| diverted | integer | 7,079,081 |
| crs_elapsed_time | float | 7,079,080 |
| actual_elapsed_time | float | 6,965,267 |
| air_time | float | 6,965,267 |
| distance | float | 7,079,081 |
| carrier_delay | integer | 7,079,081 |
| weather_delay | integer | 7,079,081 |
| nas_delay | integer | 7,079,081 |
| security_delay | integer | 7,079,081 |
| late_aircraft_delay | integer | 7,079,081 |

## Canonical Column Mapping

| Canonical column | Source column | Status |
|---|---|---|
| flight_date | fl_date | available |
| month | month | available |
| airline_code | op_unique_carrier | available |
| airline_name | N/A | unavailable in raw CSV |
| origin_airport | origin | available |
| destination_airport | dest | available |
| departure_delay | dep_delay | available |
| arrival_delay | arr_delay | available |
| cancelled | cancelled | available |
| diverted | diverted | available |
| cancellation_code | cancellation_code | available |
| carrier_delay | carrier_delay | available |
| weather_delay | weather_delay | available |
| nas_delay | nas_delay | available |
| security_delay | security_delay | available |
| late_aircraft_delay | late_aircraft_delay | available |

`airline_name` should be treated as unavailable unless a separate airline lookup
is added. Analyses should use `airline_code` as the airline identifier.

## Null Counts For Analysis-Critical Fields

| Canonical column | Source column | Null rows | Null percent |
|---|---|---:|---:|
| flight_date | fl_date | 0 | 0.0000 |
| month | month | 0 | 0.0000 |
| airline_code | op_unique_carrier | 0 | 0.0000 |
| airline_name | N/A | N/A | N/A |
| origin_airport | origin | 0 | 0.0000 |
| destination_airport | dest | 0 | 0.0000 |
| departure_delay | dep_delay | 92,970 | 1.3133 |
| arrival_delay | arr_delay | 113,814 | 1.6078 |
| cancelled | cancelled | 0 | 0.0000 |
| diverted | diverted | 0 | 0.0000 |
| cancellation_code | cancellation_code | 6,982,766 | 98.6394 |
| carrier_delay | carrier_delay | 0 | 0.0000 |
| weather_delay | weather_delay | 0 | 0.0000 |
| nas_delay | nas_delay | 0 | 0.0000 |
| security_delay | security_delay | 0 | 0.0000 |
| late_aircraft_delay | late_aircraft_delay | 0 | 0.0000 |

## Sample Observations

- The first records are January 2024 flights.
- Delay fields include negative values, which represent early departures or
  arrivals and should be preserved in M3.
- Non-cancelled rows commonly have an empty `cancellation_code`.
- Delay-cause fields are present and populated with zeroes when no cause is
  recorded.
- `cancelled` and `diverted` are numeric indicator fields.

## Git Ignore Confirmation

The raw CSV, data dictionary, and sample CSV are ignored by `.gitignore` under
`data/raw/*`; only `data/raw/.gitkeep` should be tracked.

## M3 Preparation Command

Run the preparation pipeline from the project root:

```powershell
make prepare
```

If `make` is not available on the local PATH, run the underlying command:

```powershell
.\.venv\Scripts\python.exe src\preparation\prepare_spark.py
```

The script reads paths and Spark settings from `config/local.yaml`:

- Raw CSV: `data/raw/flight_data_2024.csv`
- Prepared Parquet directory: `data/prepared/flights_2024_clean.parquet`
- Metrics JSON: `data/prepared/preparation_metrics.json`

On Windows, the script selects a local Java 17+ JDK if the active shell points
to an older Java runtime. If Hadoop `winutils.exe` is not installed, Spark still
performs the preparation and the script writes a standard Parquet directory with
PyArrow part files. Future Spark jobs should use `src/common/prepared_data.py`
to read the prepared dataset, because that helper resolves exact part-file paths
on Windows when Hadoop native directory listing is unavailable.

The prepared output is written to a temporary sibling path first and replaces the
previous prepared dataset only after the new write succeeds.

`data/prepared/*` is ignored by Git, so these generated artifacts are not
committed.

## M7 Generated Input Sizes

Run the input-size generator from the project root:

```powershell
make generate-sizes
```

The default command reads the canonical prepared Parquet dataset and writes
exact-size benchmark inputs under `data/generated/`:

- `data/generated/flights_100k.parquet`
- `data/generated/flights_500k.parquet`
- `data/generated/flights_1m.parquet`
- `data/generated/flights_3m.parquet`

Smaller inputs are selected with a deterministic hash-limit method and the
default seed `20240520`, then limited to the requested record count. The
generator hashes a null-safe representation of the canonical source columns,
orders by a seeded hash of that row key, and writes only the original canonical
columns. This keeps the subsets reproducible while avoiding the chronological
bias of taking early-2024 rows only.

Because the deterministic selection requires a global ordering by the seeded
row hash, Spark may print `WindowExec` warnings during forced generation. This
is expected for the default local inputs: the warning documents that Spark moves
the ranking step through a single logical ordering stage so exact row identities
are repeatable. A successful run is determined by the manifest validation, not
by the absence of this warning.

The full-size local input is not copied. The manifest records
`data/prepared/flights_2024_clean.parquet` as the `full` benchmark input and
validates its current row count.

Optional larger datasets are generated only when explicitly requested:

```powershell
make generate-sizes GENERATE_LARGE=1 FORCE=1
```

For targets larger than the prepared source, the generator uses controlled
replication: it writes as many full source repetitions as fit in the target,
then adds a deterministic sampled remainder. For the current `7,079,081`-row
prepared dataset, `14m` is one full repetition plus `6,920,919` sampled rows,
and `28m` is three full repetitions plus `6,762,757` sampled rows. No synthetic
columns are kept in the generated output.

Every run writes `data/generated/input_size_manifest.json` with the label, path,
target records, validated actual records, method, seed, source path, schema
match status, validation status, whether the dataset was generated in that run,
and whether an existing dataset was reused from a compatible manifest. Re-run
with `FORCE=1` to replace existing generated datasets:

```powershell
make generate-sizes FORCE=1
```

`data/generated/*` is ignored by Git, so generated benchmark inputs and the
manifest stay local unless a small curated artifact is intentionally copied
elsewhere.

Future benchmark runners should treat `data/generated/input_size_manifest.json`
as the source of truth for available input paths and validated actual row
counts. Optional config entries such as `14m` and `28m` should be skipped unless
they are present in the manifest with `validation_status` set to `success`.

## Canonical Prepared Schema

The prepared dataset contains only the canonical analysis columns from
`config/columns.yaml`, in this exact order:

| Column | Type | Source | Notes |
|---|---|---|---|
| flight_date | date | fl_date | Parsed as a Spark date. |
| month | integer | month | Month number from the raw file. |
| airline_code | string | op_unique_carrier | Stable airline identifier used by analyses. |
| airline_name | string | N/A | Intentionally nullable because the raw file has no airline name. |
| origin_airport | string | origin | Departure airport code. |
| destination_airport | string | dest | Arrival airport code. |
| departure_delay | double | dep_delay | Preserves null and negative values. |
| arrival_delay | double | arr_delay | Preserves null and negative values. |
| cancelled | integer | cancelled | Indicator, expected values `0` or `1`. |
| diverted | integer | diverted | Indicator, expected values `0` or `1`. |
| cancellation_code | string | cancellation_code | Empty values are normalized to null. |
| carrier_delay | double | carrier_delay | Delay-cause minutes. |
| weather_delay | double | weather_delay | Delay-cause minutes. |
| nas_delay | double | nas_delay | Delay-cause minutes. |
| security_delay | double | security_delay | Delay-cause minutes. |
| late_aircraft_delay | double | late_aircraft_delay | Delay-cause minutes. |

## Cleaning Rules

The preparation script is intentionally conservative because later analyses need
cancelled flights, diverted flights, null delay values, and early-flight negative
delays.

Rows are removed only when a structural field is invalid after casting:

- `flight_date` is missing or cannot be parsed as a date.
- `month` is missing or cannot be cast to integer.
- `airline_code` is missing after trimming.
- `origin_airport` is missing after trimming.
- `destination_airport` is missing after trimming.
- `cancelled` is not `0` or `1`.
- `diverted` is not `0` or `1`.

Rows are kept when:

- The flight is cancelled.
- The flight is diverted.
- `departure_delay` or `arrival_delay` is null.
- Delay values are negative.

## Null Handling Policy

Empty strings in string fields are normalized to null. Delay fields are cast to
numeric types but are not imputed or filled. This matters because Spark aggregate
functions such as `avg` ignore null values, so null delay records do not distort
delay averages.

Cancelled flights often have null operational delay fields. They are preserved
so cancellation-rate analysis in later milestones uses the correct denominator.

`airline_name` is included as a nullable canonical column to keep the schema
stable across technologies. No external airline lookup is used in M3; analyses
should use `airline_code`.

## Preparation Metrics

Each `make prepare` run prints a JSON metrics report to stdout and writes the
same metrics to `data/prepared/preparation_metrics.json`.

The metrics include:

- input rows
- output rows
- output shape and writer mode
- removed rows
- removed row percentage
- canonical source-column mapping
- null counts before cleaning
- null counts after cleaning
- delay null counts after cleaning
- structural invalid rule counts
- cancelled row count
- diverted row count
- negative departure-delay row count
- negative arrival-delay row count

## Validation Checks

After `make prepare`, verify Spark can load the prepared Parquet:

```powershell
.\.venv\Scripts\python.exe -c "import sys; sys.path.insert(0, 'src/preparation'); import prepare_spark; prepare_spark.ensure_java_17(); from pyspark.sql import SparkSession; from src.common.prepared_data import read_prepared_parquet; spark = SparkSession.builder.master('local[*]').appName('validate-prepared').getOrCreate(); df = read_prepared_parquet(spark, 'data/prepared/flights_2024_clean.parquet'); print(df.count()); df.printSchema(); spark.stop()"
```

Acceptance checks can be run with:

```powershell
.\.venv\Scripts\python.exe -c "import sys; sys.path.insert(0, 'src/preparation'); import prepare_spark; prepare_spark.ensure_java_17(); from pyspark.sql import SparkSession, functions as F; from src.common.prepared_data import read_prepared_parquet; spark = SparkSession.builder.master('local[*]').appName('validate-m3').getOrCreate(); df = read_prepared_parquet(spark, 'data/prepared/flights_2024_clean.parquet'); df.agg(F.sum((F.col('cancelled') == 1).cast('int')).alias('cancelled_rows'), F.sum(F.col('departure_delay').isNull().cast('int')).alias('null_departure_delay_rows'), F.sum((F.col('departure_delay') < 0).cast('int')).alias('negative_departure_delay_rows'), F.avg('departure_delay').alias('avg_departure_delay')).show(truncate=False); spark.stop()"
```
