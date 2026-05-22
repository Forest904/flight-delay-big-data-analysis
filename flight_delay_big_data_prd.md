# Flight Delay Big Data Analysis As-Built Specification

**Project:** Big Data Course - Second Project  
**Dataset:** 2024 Flight Delay Dataset  
**Institution:** Roma Tre University  
**Owner:** Luca Foresti  
**Repository:** <https://github.com/Forest904/flight-delay-big-data-analysis.git>  
**Status:** Submission hardening and benchmark evidence recovery

## Summary

This repository implements a reproducible batch analytics project for more than
7 million 2024 flight records. It prepares the raw Kaggle CSV into a canonical
Parquet dataset, runs two assignment analyses across Spark SQL, Spark Core, and
Hive, validates output equivalence, and produces report-ready benchmark tables,
figures, and first-10 samples.

MapReduce is implemented as an optional stretch lane through Docker-local Hadoop
Streaming. AWS EMR evidence exists for Spark SQL and Spark Core when Learner Lab
budget and credentials allow. Docker evidence is a standalone simulation and is
not claimed as a managed cluster.

## Project Goals

- Produce correct and comparable outputs for the two required assignment
  analyses.
- Use Spark SQL, Spark Core, and Hive as the required technology baseline.
- Keep MapReduce as stretch evidence only when it validates against Spark SQL.
- Benchmark local and Docker simulation runs with explicit input labels and
  repetition counts.
- Preserve AWS EMR Spark evidence without overclaiming budget-limited cells.
- Keep the final report evidence-first, reproducible, and honest about limits.
- Prevent submission drift through `make submission-check`.
- Avoid tracking secrets, raw data, prepared data, runtime outputs, and bulky
  benchmark artifacts.

## Current Analytical Contract

### Assignment Analysis 3.2 - Delay Report By Airport And Time Period

Input: the canonical prepared Parquet dataset.

Grouping keys:

```text
origin_airport
month
delay_range
```

Output columns:

```text
origin_airport
month
delay_range
flight_count
avg_departure_delay
avg_arrival_delay
top_1_cause
top_1_count
top_2_cause
top_2_count
top_3_cause
top_3_count
```

Delay ranges are based on non-null `departure_delay`:

- `low`: less than 15 minutes.
- `medium`: 15 through 60 minutes.
- `high`: greater than 60 minutes.

### Assignment Analysis 3.3 - Ranking Of Airline-Airport Pairs

Input: the canonical prepared Parquet dataset.

Grouping keys:

```text
origin_airport
airline
```

Output columns:

```text
origin_airport
airline
flight_count
avg_departure_delay
avg_arrival_delay
cancellation_rate
airport_avg_departure_delay
difference_from_airport_avg_departure_delay
rank_at_airport
```

Ranking is ascending by average departure delay within each airport, with null
average delays sorted last.

## Data Contract

- Raw CSV location: `data/raw/flight_data_2024.csv`.
- Prepared canonical input: `data/prepared/flights_2024_clean.parquet`.
- Generated benchmark inputs:
  - `100k`: `data/generated/flights_100k.parquet`
  - `500k`: `data/generated/flights_500k.parquet`
  - `1m`: `data/generated/flights_1m.parquet`
  - `3m`: `data/generated/flights_3m.parquet`
  - `full`: `data/prepared/flights_2024_clean.parquet`
  - `14m`: optional controlled replication stress input
  - `28m`: optional controlled replication stress input
- Generated input truth source: `data/generated/input_size_manifest.json`.
- Replicated `14m` and `28m` inputs are scalability stress inputs, not new
  statistical observations about flight behavior.

The prepared schema and cleaning rules are documented in
`docs/data_preparation.md`.

## Technology Contract

| Technology | Status | Runtime contract |
|---|---|---|
| Spark SQL | Required baseline | Local PySpark reference implementation and correctness anchor |
| Spark Core | Required baseline | RDD implementation validated against Spark SQL |
| Hive | Required baseline | Docker-backed HiveServer2/HiveQL implementation validated against Spark SQL |
| MapReduce | Stretch | Docker-local Hadoop Streaming implementation validated against Spark SQL |
| AWS EMR Spark | Evidence extension | Spark SQL/Core managed-cluster evidence when budget allows |
| EMR Hive | Stretch only | Not part of the baseline unless explicitly completed |

Each technology writes report-ready outputs under `outputs/<technology>/` with:

```text
<job_name>/full/part*.csv
<job_name>/first_10.csv
runtime_metrics.json
```

Runtime metrics must include `technology`, `status`, `input_path`, job durations,
output row counts, and output paths.

## Validation And Submission Gate

Spark SQL is the correctness reference, but all required technologies must use
the same canonical validation input for report-ready outputs:

```text
data/prepared/flights_2024_clean.parquet
```

Validators fail if:

- Runtime metrics are missing or not successful.
- Output schemas differ from the expected contract.
- Output row counts disagree with runtime metrics.
- Spark Core, Hive, or MapReduce outputs differ from Spark SQL beyond the
  numeric tolerance.
- Any report-ready runtime metrics use a non-canonical input.

The final submission gate is:

```powershell
make submission-check
```

It runs tests, validators, chart generation, report generation, artifact checks,
single-run benchmark note checks, tracked-artifact hygiene, and credential-like
value scanning. Details are in `docs/submission_gate.md`.

## Benchmark Evidence Policy

Benchmark rows must identify:

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
```

Required local baseline:

- Inputs: `100k`, `500k`, `1m`, `3m`, `full`.
- Technologies: Spark SQL, Spark Core, Hive.
- Target repetitions: 3 for report-critical claims.

Required Docker simulation baseline:

- Inputs: `100k`, `500k`, `1m`.
- Technologies: Spark SQL, Spark Core, Hive.
- Target repetitions: 3 for report-critical claims.

Any report-critical `runs=1` benchmark summary row must have an explicit
machine-readable note in `report/tables/benchmark_notes.csv` marked as `smoke`,
`budget_limited`, or `resource_limited`.

AWS EMR rows are useful evidence but may remain budget-limited. MapReduce
benchmarking is optional stretch evidence and should not slow the required
three-technology baseline.

## Reproducibility Contract

The canonical local run order is:

```powershell
make setup
make check-env
make inspect-raw
make prepare
make generate-sizes
make run-all-local
make run-mapreduce
make charts
make report
make submission-check
```

Focused docs:

- `docs/reproducibility.md`: setup and run order.
- `docs/benchmarking.md`: benchmark policy and matrix.
- `docs/aws_emr.md`: AWS workflow and cautions.
- `docs/submission_gate.md`: final gate and hygiene checks.

## Hygiene Requirements

The repository must not track:

- `.env`
- raw Kaggle data
- prepared Parquet data
- generated Parquet data
- runtime outputs
- benchmark logs and bulky result downloads
- `derby.log`
- real credential-like values

Only placeholder files such as `.env.example` and `.gitkeep` files may be
tracked in ignored runtime directories. Kaggle tokens and AWS Learner Lab
credentials used locally must be rotated before sharing the repository,
screenshots, logs, or videos.

## Known Limits

- Docker standalone simulation is single-host evidence, not a production
  cluster.
- Hive local/Docker evidence is required; EMR Hive is a stretch item.
- AWS EMR evidence is constrained by Learner Lab budget, credentials, and
  cluster availability.
- MapReduce is intentionally slower and optional; it exists for implementation
  comparison and stretch validation.
- Replicated large inputs test processing scale, not new statistical behavior.
- Warm filesystem cache, Spark/JVM startup, small aggregate outputs, and shuffle
  behavior must be discussed when interpreting timings.

## Definition Of Done

The project is submission-ready when:

- Spark SQL, Spark Core, Hive, and claimed MapReduce outputs validate against
  the same canonical prepared input.
- Required report tables, figures, and first-10 samples exist.
- Benchmark evidence has explicit input labels, environment labels, repetition
  counts, and notes for all report-critical single-run cells.
- The final PDF is rebuilt from the final Markdown source.
- `make submission-check` passes.
- `git status --short` contains only intentional source, documentation, test,
  and committed report-evidence changes.
- No private credentials or bulky generated artifacts are tracked.
