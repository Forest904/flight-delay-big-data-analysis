# MapReduce Analyses

This document records the M6 Hadoop Streaming stretch implementation. It is an
optional extension after the required Spark SQL, Spark Core, and Hive path.
MapReduce is included in report claims only when its outputs validate against
the Spark SQL reference generated from the same input dataset.

## Command

Run the MapReduce analyses from the repository root:

```powershell
make run-mapreduce
```

The command executes `src/mapreduce/run_mapreduce.py`. Docker Desktop must be
running because Hadoop Streaming is executed inside the `mapreduce-runner`
Compose service built from `Dockerfile.mapreduce`.

Validate MapReduce against Spark SQL:

```powershell
make validate-mapreduce
```

The Spark SQL reference and MapReduce outputs must use the same prepared
Parquet input. The validator checks the `input_path` recorded in both runtime
metrics files before comparing CSV outputs.

## Docker Hadoop Streaming Runtime

The `mapreduce-runner` service uses the `apache/hive:4.0.1` image family because
it already includes Hadoop. The Dockerfile installs Python 3, creates a stable
`/opt/hadoop-streaming.jar` symlink, resets the Hive entrypoint, and runs Hadoop
Streaming in local MapReduce mode against the repository bind mount at
`/workspace`.

This is a reproducible Docker-local Hadoop Streaming runtime, not YARN, HDFS,
or a remote Hadoop deployment. It is useful for implementation comparison and
stretch evidence, while the main grade-critical technology set remains Spark
SQL, Spark Core, and Hive.

## Canonical CSV Export

MapReduce does not reparse the raw Kaggle CSV. The runner exports the selected
prepared Parquet input to:

```text
data/generated/mapreduce_csv/<input_slug>/part-00000.csv
data/generated/mapreduce_csv/<input_slug>/manifest.json
```

The manifest records the source Parquet path, Parquet part-file signatures,
canonical column order, row count, CSV byte size, CSV SHA-256, export duration,
and whether the export was reused. Cached CSV exports are reused only when the
manifest and file metadata still match. Runtime metrics report CSV export
duration separately from Hadoop Streaming job durations, so benchmark rows
represent the MapReduce job time.

## Output Layout

```text
outputs/mapreduce/
  delay_by_airport_month/
    full/
      part-00000.csv
    first_10.csv
  airline_airport_ranking/
    full/
      part-00000.csv
    first_10.csv
  runtime_metrics.json
```

The output schemas and job names match Spark SQL, Spark Core, and Hive:

- `delay_by_airport_month`
- `airline_airport_ranking`

## Implementation Notes

The delay mapper skips rows with null `departure_delay`, derives the same delay
range and per-flight cause label as Spark SQL, and emits grouped values keyed by
`origin_airport`, `month`, and `delay_range`. The reducer aggregates counts and
averages, then sorts cause counts by count descending and cause label ascending
to emit the top-three cause schema.

The ranking mapper emits one record per flight keyed by `origin_airport`. The
reducer aggregates airline-level and airport-level departure statistics, applies
Spark SQL `RANK()` semantics with null average delays last, and emits rows
ordered by airport, rank, average delay, and airline.

Reducers emit JSON rows internally. The runner then sorts, validates row shape,
and writes the stable CSV output files used by validators, report tables, and
benchmark metadata.

## Benchmarking

Run the opt-in MapReduce stretch benchmark with three repetitions on the local
input ladder:

```powershell
make benchmark-mapreduce-local BENCHMARK_FLAGS="--input-label 100k --input-label 500k --input-label 1m --input-label 3m --input-label full --repetitions 3"
```

The default `make benchmark-local` matrix intentionally remains limited to
Spark SQL, Spark Core, and Hive. MapReduce benchmark rows are included in chart
and table generation when present, without adding missing MapReduce cells to
the core benchmark-status matrix.

MapReduce benchmark runs write isolated outputs under:

```text
outputs/mapreduce/.benchmark_runs/<run_id>/<input_label>/
```

The main `outputs/mapreduce/` directory is reserved for validated report-ready
outputs from `make run-mapreduce`.
