# Benchmarking

This document describes how benchmark evidence is generated, labeled, and
accepted for the report.

## Input Ladder

Configured inputs come from `config/local.yaml` and the generated input manifest:

| Label | Source |
|---|---|
| `100k` | Generated deterministic subset |
| `500k` | Generated deterministic subset |
| `1m` | Generated deterministic subset |
| `3m` | Generated deterministic subset |
| `full` | `data/prepared/flights_2024_clean.parquet` |
| `14m` | Optional controlled replication stress input |
| `28m` | Optional controlled replication stress input |
| `1m_hc8` | Optional synthetic high-cardinality stress input derived from `1m` |

The `14m` and `28m` inputs are scalability stress data. They must not be
described as new statistical observations.

Manifest entries include an `input_kind` field:

- `original_prepared`: the canonical prepared Parquet input.
- `deterministic_subset`: hash-limited row-count subsets.
- `row_volume_replication`: replicated row-volume stress inputs such as `14m`
  and `28m`.
- `high_cardinality_stress`: synthetic cardinality/shuffle stress inputs such
  as `1m_hc8`.

The `1m_hc8` input keeps the source row count, schema, and numeric values from
`1m`, but suffixes `origin_airport`, `airline_code`, and non-null
`airline_name` values with deterministic variants `_HC00` through `_HC07`.
It is benchmark-only stress evidence and must not be interpreted as additional
flight-behavior observations.

## Required Evidence

Local baseline:

- Technologies: Spark SQL, Spark Core, Hive.
- Inputs: `100k`, `500k`, `1m`, `3m`, `full`.
- Target repetitions: 3 for report-critical cells.

Docker standalone simulation baseline:

- Technologies: Spark SQL, Spark Core, Hive.
- Inputs: `100k`, `500k`, `1m`.
- Target repetitions: 3 for report-critical cells.

MapReduce is stretch evidence. AWS EMR is managed Spark evidence when budget and
credentials allow.

## Commands

Generate benchmark inputs first:

```powershell
make generate-sizes
```

Generate the optional high-cardinality stress input:

```powershell
make generate-sizes GENERATE_CARDINALITY_STRESS=1
```

Run local benchmarks:

```powershell
make benchmark-local
```

Run Docker standalone simulation:

```powershell
make benchmark-docker-simulation
```

Run the optional MapReduce stretch benchmark:

```powershell
make benchmark-mapreduce-local BENCHMARK_FLAGS="--input-label 100k --input-label 500k --input-label 1m --input-label 3m --input-label full --repetitions 3"
```

Useful flags:

```powershell
make benchmark-local BENCHMARK_FLAGS="--input-label 1m --technology spark_sql --repetitions 3"
make benchmark-local BENCHMARK_FLAGS="--include-optional --input-label 14m --repetitions 3"
make benchmark-local BENCHMARK_FLAGS="--input-label 1m --input-label 1m_hc8 --technology spark_sql --technology spark_core --repetitions 3"
make benchmark-docker-simulation BENCHMARK_FLAGS="--input-label 1m --input-label 1m_hc8 --technology spark_sql --technology spark_core --repetitions 3"
```

## Output Files

Benchmark runs write timestamped CSVs under:

```text
experiments/results/local/
experiments/results/docker-simulation/
experiments/results/aws-emr/
experiments/results/aws-emr-larger/
```

The raw CSV schema includes:

```text
run_id
repetition
technology
job_name
input_label
records
input_kind
synthetic_input
source_input_label
stress_variant_factor
environment
execution_setting
duration_seconds
input_read_seconds
plan_build_seconds
result_collect_seconds
full_output_write_seconds
sample_output_write_seconds
materialization_mode
output_rows
status
timestamp_utc
input_path
metrics_path
error
stage
```

`make charts` aggregates successful rows into `report/tables/benchmark_summary.*`
with runs, median, mean, min, max, and standard deviation. It also writes
`report/tables/benchmark_phase_summary.*`, which keeps the same grouping but
adds median phase timings when the raw benchmark rows expose them. Older raw
benchmark CSVs remain readable; missing phase fields are left blank in the
phase table.

`make charts` also writes `report/tables/cardinality_stress_comparison.*` when
both baseline and stress rows are available. That table compares `1m` with
`1m_hc8` by environment, job, and Spark technology using median duration and
aggregate output-row cardinality ratios. High-cardinality stress rows are kept
out of row-volume scalability ratios so the two stress dimensions remain
separate.

## Single-Run Evidence Policy

Report-critical `runs=1` rows must be explicit. The submission gate checks
`report/tables/benchmark_notes.csv`, whose columns are:

```text
environment,input_label,job_name,technology,run_id,classification,note
```

Allowed classifications:

- `smoke`
- `budget_limited`
- `resource_limited`

Use `*` as a wildcard only when one note intentionally covers a group of cells.
Single-run rows without a note fail `make submission-check`.

## Interpretation Limits

- Docker standalone simulation runs on one host and is not a real cluster.
- AWS EMR rows include service overhead and can be budget-limited.
- Spark and Hive startup costs can dominate small inputs.
- Spark SQL and Spark Core use the same small-result materialization policy:
  the ordered aggregate result is collected once to the driver, then
  `full/part-00000.csv` and `first_10.csv` are written from those rows.
- For Spark SQL and Spark Core, `duration_seconds` is total per-analysis
  elapsed time, not pure compute time. `result_collect_seconds` is the main
  Spark action boundary, so it includes transformation, aggregation, ordering,
  and driver collection forced by `toPandas()`.
- Prepared Parquet and warm local caches affect throughput.
- Aggregate output cardinality is small relative to input size.
- Controlled replication tests processing scale, not additional flight behavior.
- High-cardinality stress inputs test shuffle/output-key cardinality, not
  additional flight behavior.
