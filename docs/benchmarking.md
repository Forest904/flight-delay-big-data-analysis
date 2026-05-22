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

The `14m` and `28m` inputs are scalability stress data. They must not be
described as new statistical observations.

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
environment
execution_setting
duration_seconds
output_rows
status
timestamp_utc
input_path
metrics_path
error
stage
```

`make charts` aggregates successful rows into `report/tables/benchmark_summary.*`
with runs, median, mean, min, max, and standard deviation.

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
- Prepared Parquet and warm local caches affect throughput.
- Aggregate output cardinality is small relative to input size.
- Controlled replication tests processing scale, not additional flight behavior.
