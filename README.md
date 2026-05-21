# Flight Delay Big Data Analysis

Comparative big-data analysis of the **2024 Flight Delay Dataset** using **Spark SQL**, **Spark Core**, and **Hive**, with a focus on data preparation, analytical correctness, execution efficiency, and scalability benchmarking.

Repository: <https://github.com/Forest904/flight-delay-big-data-analysis.git>

This repository is developed for the **Big Data Course - Second Project** at **Roma Tre University**.

---

## Project Overview

The goal of this project is to analyze a large real-world flight dataset using multiple big-data technologies and compare their behavior in terms of:

- Expressiveness
- Ease of implementation
- Execution time
- Scalability
- Shuffle and aggregation cost
- Reproducibility

The project uses the **2024 Flight Delay Dataset**, which contains more than 7 million flight records and includes information about flights, delays, cancellations, diversions, airlines, airports, and operational attributes.

The final output of the project will include:

- Cleaned and prepared datasets
- Analytical jobs implemented with multiple technologies
- Benchmark results for different input sizes
- Tables and charts comparing execution times
- A final PDF report
- Reproducible execution scripts

---

## Technologies Used

The main technologies used in this project are:

| Area | Technology |
|---|---|
| Language | Python 3.11+ |
| Distributed processing | Apache Spark |
| Spark APIs | Spark SQL, Spark Core |
| SQL-on-Hadoop | Apache Hive |
| Hadoop batch processing | Hadoop Streaming MapReduce |
| Storage format | CSV, Parquet |
| Local orchestration | Docker Compose |
| Scripts | Bash |
| Configuration | YAML |
| Benchmark logs | CSV / JSON |
| Charts | Python, matplotlib |
| Documentation | Markdown |
| Version control | Git + GitHub |

MapReduce is implemented as a stretch extension. It is opt-in and validated
against Spark SQL before being used for report claims.

---

## Analyses Implemented

This project focuses on at least two analytical jobs from the assignment specification.

### 1. Delay Report by Airport and Month

For each departure airport, month, and departure-delay range, the job computes:

- Number of flights
- Average departure delay
- Average arrival delay
- Delay range:
  - Low delay: less than 15 minutes
  - Medium delay: between 15 and 60 minutes
  - High delay: more than 60 minutes
- Three most frequent cancellation or delay causes, when available

### 2. Airline-Airport Ranking

For each pair of departure airport and airline, the job computes:

- Number of flights operated by the airline at the airport
- Average departure delay
- Average arrival delay
- Cancellation rate
- Difference between the airline average departure delay and the airport average departure delay
- Airline ranking at the airport based on average departure delay

---

## Repository Structure

```text
flight-delay-big-data-analysis/
|
|-- README.md
|-- Makefile
|-- docker-compose.yml
|-- Dockerfile.mapreduce
|-- requirements.txt
|-- .gitignore
|
|-- config/
|   |-- local.yaml
|   |-- cluster.yaml
|   `-- columns.yaml
|
|-- data/
|   |-- raw/
|   |   `-- .gitkeep
|   |-- prepared/
|   |   `-- .gitkeep
|   |-- samples/
|   |   `-- .gitkeep
|   `-- generated/
|       `-- .gitkeep
|
|-- src/
|   |-- common/
|   |   |-- prepared_data.py
|   |   `-- runtime.py
|   |
|   |-- preparation/
|   |   |-- prepare_spark.py
|   |   `-- generate_input_sizes.py
|   |
|   |-- spark_sql/
|   |   `-- run_spark_sql.py
|   |
|   |-- spark_core/
|   |   `-- run_spark_core.py
|   |
|   |-- hive/
|   |   |-- ddl.sql
|   |   |-- analysis_delay_by_airport_month.sql
|   |   |-- analysis_airline_airport_ranking.sql
|   |   `-- run_hive.py
|   |
|   `-- mapreduce/
|       |-- mapreduce_logic.py
|       |-- mapper_delay.py
|       |-- reducer_delay.py
|       |-- mapper_ranking.py
|       |-- reducer_ranking.py
|       `-- run_mapreduce.py
|
|-- scripts/
|   |-- build_report.py
|   |-- check_env.py
|   |-- clean_generated_artifacts.py
|   |-- download_dataset.md
|   |-- generate_charts.py
|   |-- inspect_raw_dataset.py
|   |-- validate_hive_outputs.py
|   |-- validate_mapreduce_outputs.py
|   |-- validate_spark_core_outputs.py
|   `-- validate_spark_sql_outputs.py
|
|-- experiments/
|   |-- run_benchmarks.py
|   `-- results/
|       |-- local/
|       `-- cluster/
|
|-- outputs/
|   |-- spark_sql/
|   |-- spark_core/
|   |-- hive/
|   `-- mapreduce/
|
|-- notebooks/
|   `-- .gitkeep
|
|-- report/
|   |-- draft_final_report.md
|   |-- figures/
|   |-- tables/
|   `-- draft_final_report.pdf
|
`-- docs/
    |-- cluster_simulation.md
    |-- data_preparation.md
    |-- hive_analyses.md
    |-- mapreduce_analyses.md
    |-- spark_core_analyses.md
    `-- spark_sql_analyses.md
```

---

## Dataset

The project uses the **2024 Flight Delay Dataset** from Kaggle.

The original dataset is not included in this repository because of its size.

Download the dataset manually from Kaggle and place the CSV file under:

```text
data/raw/
```

Expected local structure:

```text
data/
`-- raw/
    `-- flight_data_2024.csv
```

The exact filename can be configured in:

```text
config/local.yaml
```

---

## Data Preparation

Before running the analytical jobs, the raw dataset must be cleaned and normalized.

The preparation step is responsible for:

- Loading the raw CSV file
- Validating the schema
- Selecting relevant columns
- Normalizing column names
- Casting numeric and date fields
- Handling missing values
- Keeping cancelled flights for cancellation-rate analysis
- Writing the cleaned dataset in Parquet format

Prepared data output:

```text
data/prepared/flights_2024_clean.parquet
```

Run locally:

```bash
make prepare
```

## Generated Input Sizes

For benchmarking and scalability analysis, the project generates reproducible
datasets of different sizes from the canonical prepared Parquet input.

Default generated datasets:

```text
data/generated/flights_100k.parquet
data/generated/flights_500k.parquet
data/generated/flights_1m.parquet
data/generated/flights_3m.parquet
```

The full-size local input is referenced directly from
`data/prepared/flights_2024_clean.parquet` instead of being copied. The optional
large replicated datasets are:

```text
data/generated/flights_14m.parquet
data/generated/flights_28m.parquet
```

Smaller datasets are created with a seeded deterministic hash-limit method and
exact row limits. Larger datasets are created through controlled replication:
full repetitions of the prepared dataset plus a deterministic hash-limited
remainder. Forced generation may print Spark `WindowExec` warnings because exact
deterministic selection uses a global ordering step; validated manifest counts
are the success signal.

Run:

```bash
make generate-sizes
```

Replace existing generated inputs or opt into the larger replicated datasets:

```bash
make generate-sizes FORCE=1
make generate-sizes GENERATE_LARGE=1 FORCE=1
```

Generation writes `data/generated/input_size_manifest.json` with the validated
row count, generation method, seed, source path, and reuse status for every
benchmark input. Benchmark runners should use this manifest as the source of
truth and skip optional entries such as `14m` and `28m` unless they are present
with successful validation.

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Forest904/flight-delay-big-data-analysis.git
cd flight-delay-big-data-analysis
```

### 2. Create a Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell, the equivalent setup path is:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Place the dataset

Download the dataset from Kaggle and place it under:

```text
data/raw/
```

### 5. Prepare the dataset

```bash
make prepare
```

---

## Running the Jobs

### Run Spark SQL jobs

```bash
make run-spark-sql
```

Or on Windows:

```powershell
.\.venv\Scripts\python.exe src\spark_sql\run_spark_sql.py
```

On Windows, Spark SQL output writing requires Hadoop `winutils.exe` configured
through `HADOOP_HOME` or `hadoop.home.dir`.

Validate Spark SQL outputs with:

```powershell
make validate-spark-sql
```

### Run Spark Core jobs

```bash
make run-spark-core
```

On Windows, `make run-spark-core` uses the Docker Compose Spark Core service so
PySpark RDD worker execution runs in Linux. On Linux, WSL, or macOS, it runs the
native Spark Core runner directly.

Run the native path directly for diagnostics with:

```powershell
make run-spark-core-native
```

Validate Spark Core outputs against the Spark SQL reference with:

```powershell
make validate-spark-core
```

Run only the Spark Core RDD worker smoke check with:

```powershell
.\.venv\Scripts\python.exe src\spark_core\run_spark_core.py --smoke-rdd
```

Spark Core writes its small aggregate CSV outputs locally, so it does not require
Hadoop `winutils.exe` for output writing. If the native Windows RDD smoke check
fails with `Python worker exited unexpectedly`, use the stable command:

```powershell
make run-spark-core
```

That command mounts this repository, runs the same Spark Core runner with Python
3.12 and Java 17 in Docker, and writes the same `outputs/spark_core/` files. The
explicit Docker target remains available as `make run-spark-core-docker`.

### Run Hive jobs

```bash
make run-hive
```

This starts the Docker Compose Hive stack with HiveServer2, a standalone
metastore, and Postgres metadata storage. Hive reads the prepared Parquet dataset
through an external table and writes outputs under `outputs/hive/`.

Docker Desktop must be running before starting Hive. The Hive services remain
running after the command finishes; stop them with:

```powershell
make stop-hive
```

Validate the Hive outputs against the Spark SQL reference with:

```powershell
make validate-hive
```

### Run MapReduce stretch jobs

```bash
make run-mapreduce
```

MapReduce is the optional M6 stretch implementation. It uses Docker-based
Hadoop Streaming with Python mappers and reducers. The runner first exports the
selected prepared Parquet input to a canonical CSV under
`data/generated/mapreduce_csv/`, then runs both analyses and writes outputs
under `outputs/mapreduce/`.

`outputs/mapreduce/` is reserved for validated report-ready outputs. The
runner supports `--output-root` for isolated runs, and benchmark smoke runs use
that option automatically so they do not overwrite the validated MapReduce
artifacts.

Validate MapReduce against the current Spark SQL reference outputs with:

```powershell
make validate-mapreduce
```

The validator fails if Spark SQL and MapReduce runtime metrics do not record
the same input path. Benchmarking MapReduce is opt-in through the separate
target documented below; `make run-all-local` intentionally remains limited to
the three required technologies.

### Run all local jobs

```bash
make run-all-local
```

`make run-all-local` runs Spark SQL, Spark Core, and Hive, then validates all
outputs. It expects the prepared Parquet dataset to already exist. Run
`make prepare` first after placing the raw Kaggle CSV under `data/raw/`.

---

## Benchmarking

The local benchmark runner executes Spark SQL, Spark Core, and Hive jobs across
validated generated input sizes from `data/generated/input_size_manifest.json`.
Run `make generate-sizes` before benchmarking.

Metrics collected include:

```text
technology
job_name
input_label
records
environment
cluster_size
duration_seconds
output_rows
status
timestamp_utc
```

Run local benchmarks:

```bash
make benchmark-local
```

Run a smaller smoke benchmark:

```bash
make benchmark-local BENCHMARK_FLAGS="--input-label 100k"
```

Run the opt-in MapReduce benchmark smoke:

```bash
make benchmark-mapreduce-local BENCHMARK_FLAGS="--input-label 100k"
```

This writes regular benchmark rows with `technology=mapreduce`. The default
`make benchmark-local` matrix remains Spark SQL, Spark Core, and Hive so the
required submission path is not slowed down by the stretch runtime. MapReduce
benchmark outputs are written under
`outputs/mapreduce/.benchmark_runs/<run_id>/<input_label>/`; the main
`outputs/mapreduce/` validation artifacts are left untouched.

Run Docker standalone simulation benchmarks:

```bash
make benchmark-cluster
```

In this repository, `make benchmark-cluster` starts a Docker Compose Spark
standalone simulation with one master, two workers, and a driver container. It
uses `config/cluster.yaml`, writes results under `experiments/results/cluster/`,
and labels rows with `environment=docker-simulation`. The default M2 matrix runs
`100k`, `500k`, and `1m` for Spark SQL, Spark Core, and Hive.

Run a narrower simulation slice with benchmark flags:

```bash
make benchmark-cluster BENCHMARK_FLAGS="--input-label 1m --technology spark_sql"
```

Hive is included in the Docker simulation benchmark CSV, but it remains the existing
single-node containerized HiveServer2/metastore/Postgres setup. Treat it as
controlled Docker execution evidence, not a distributed Hive/Hadoop cluster.
See `docs/cluster_simulation.md` for the topology and limitations.

Benchmark results are stored in:

```text
experiments/results/local/
experiments/results/cluster/
```

Each local benchmark run writes:

```text
experiments/results/local/benchmark_<YYYYMMDDTHHMMSSffffffZ>.csv
experiments/results/local/benchmark_latest.csv
experiments/results/local/logs/<run_id>/
```

The timestamped CSV is immutable run evidence. `benchmark_latest.csv` is a
convenience copy for report tables and charts.

---

## Outputs

Analytical outputs are stored by technology:

```text
outputs/spark_sql/
outputs/spark_core/
outputs/hive/
outputs/mapreduce/
```

Each technology should produce comparable outputs for the same analytical job.
MapReduce follows the same output contract:

```text
outputs/mapreduce/
|-- delay_by_airport_month/
|   |-- full/
|   |   `-- part-00000.csv
|   `-- first_10.csv
|-- airline_airport_ranking/
|   |-- full/
|   |   `-- part-00000.csv
|   `-- first_10.csv
`-- runtime_metrics.json
```

MapReduce benchmark smoke outputs are intentionally excluded from that
report-ready layout and are written below `outputs/mapreduce/.benchmark_runs/`.

---

## Report

The final report is developed in Markdown and exported as PDF.

Report files are stored in:

```text
report/
```

Expected report outputs:

```text
report/draft_final_report.md
report/draft_final_report.pdf
report/figures/
report/tables/
```

Generate charts:

```bash
make charts
```

This also regenerates `report/tables/environment_summary.*` with hardware,
runtime, Spark, Hive, Docker, and Docker Compose configuration evidence.

Generate final report:

```bash
make report
```

This rebuilds `report/draft_final_report.pdf` from
`report/draft_final_report.md`.

---

## Reproducibility

A complete fresh-clone reproduction should follow this sequence after the raw
Kaggle CSV has been downloaded into `data/raw/`:

```bash
make setup
make check-env
make inspect-raw
make prepare
make generate-sizes
make run-all-local
make benchmark-local
make benchmark-cluster
make charts
make report
```

Regeneration map:

| Artifact | Command |
|---|---|
| Prepared Parquet data | `make prepare` |
| Input-size datasets | `make generate-sizes` |
| Spark SQL, Spark Core, and Hive outputs | `make run-all-local` |
| MapReduce stretch outputs | `make run-mapreduce` |
| Local benchmark CSVs and logs | `make benchmark-local` |
| MapReduce local benchmark CSVs and logs | `make benchmark-mapreduce-local` |
| Docker standalone simulation benchmark CSVs and logs | `make benchmark-cluster` |
| Charts and report tables | `make charts` |
| Final PDF | `make report` |

The reliable Windows test command is:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

On Linux, WSL, or macOS, use:

```bash
.venv/bin/python -m pytest -q
```

If Hive or cluster execution requires additional setup, see:

```text
docs/hive_analyses.md
docs/cluster_simulation.md
docs/mapreduce_analyses.md
```

---

## Expected Makefile Commands

The project exposes the following supported commands:

```text
setup
check-env
inspect-raw
prepare
generate-sizes
run-spark-sql
run-spark-core
run-hive
run-mapreduce
stop-hive
validate-spark-sql
validate-spark-core
validate-hive
validate-mapreduce
run-all-local
benchmark-local
benchmark-cluster
benchmark-mapreduce-local
charts
report
clean
```

`make clean` is intentionally conservative. It removes generated data,
technology outputs, and benchmark runtime results while preserving raw Kaggle
data, `.gitkeep` files, committed report figures/tables/PDFs, source code,
configuration, and documentation.

Dry-run the cleanup helper directly with:

```powershell
.\.venv\Scripts\python.exe scripts\clean_generated_artifacts.py --dry-run
```

---

## Final Submission Checklist

- [ ] Raw Kaggle CSV is present under `data/raw/` and matches `config/local.yaml`.
- [ ] Environment checks pass with `make check-env`.
- [ ] Prepared Parquet data has been regenerated with `make prepare`.
- [ ] Input-size datasets and manifest have been regenerated with `make generate-sizes`.
- [ ] Spark SQL, Spark Core, and Hive outputs plus validations pass with `make run-all-local`.
- [ ] MapReduce stretch outputs pass with `make run-mapreduce` and `make validate-mapreduce`, if claiming M6.
- [ ] Local benchmarks have been regenerated with `make benchmark-local`.
- [ ] MapReduce benchmark smoke has been regenerated with `make benchmark-mapreduce-local BENCHMARK_FLAGS="--input-label 100k"`, if claiming M6.
- [ ] Docker standalone simulation benchmarks have been regenerated with `make benchmark-cluster`, if Docker is available.
- [ ] Report charts and tables have been regenerated with `make charts`.
- [ ] Final PDF has been rebuilt with `make report`.
- [ ] Tests pass with `.\.venv\Scripts\python.exe -m pytest -q`.
- [ ] `git status --short` shows only intentional source, documentation, test, and report-evidence changes.
- [ ] No raw, prepared, generated, runtime output, benchmark log, virtual environment, or bulky local artifact is staged for Git.

---

## Experimental Plan

The project compares execution times across:

- Different technologies
- Different analytical jobs
- Different input sizes
- Local mode and Docker standalone simulation, where available

Suggested local benchmark matrix:

| Input Size | Spark SQL | Spark Core | Hive |
|---:|---|---|---|
| 100k | Yes | Yes | Yes |
| 500k | Yes | Yes | Yes |
| 1M | Yes | Yes | Yes |
| 3M | Yes | Yes | Yes |
| 7M+ | Yes | Yes | Yes |

M2 Docker standalone simulation benchmark matrix:

| Input Size | Spark SQL | Spark Core | Hive |
|---:|---|---|---|
| 100k | Yes | Yes | Yes |
| 500k | Yes | Yes | Yes |
| 1M | Yes | Yes | Yes |

---

## Documentation

Additional documentation is stored under:

```text
docs/
```

Recommended documents:

| File | Purpose |
|---|---|
| `cluster_simulation.md` | Docker Spark standalone simulation and limits |
| `data_preparation.md` | Cleaning rules and schema decisions |
| `hive_analyses.md` | Hive setup, queries, execution, and validation |
| `spark_core_analyses.md` | Spark Core implementation and validation notes |
| `spark_sql_analyses.md` | Spark SQL implementation and validation notes |

---

## Git Ignore Policy

The repository should not track large generated artifacts. Raw data, prepared
Parquet data, generated benchmark inputs, runtime outputs, raw benchmark logs,
local virtual environments, caches, and local environment files remain ignored.
Curated report artifacts under `report/figures/` and `report/tables/` are small
submission evidence and are intentionally committed.

Ignored runtime artifact paths:

```text
data/raw/*
data/prepared/*
data/generated/*
outputs/*
experiments/results/*
*.parquet
*.csv
*.log
```

Keep `.gitkeep` files where empty directories need to be preserved.

---

## Known Limitations

Current expected limitations:

- The full raw dataset is not stored in the repository.
- Cluster experiments depend on the availability of a suitable execution environment.
- The Docker standalone simulation runs all services on one host and must not
  be described as production-cluster performance.
- Larger-than-original datasets are generated through controlled replication, so they are intended for scalability testing rather than new statistical insight.
- Hive execution may require additional local or Docker-based configuration.
- MapReduce is implemented as an optional stretch and depends on Docker-based
  Hadoop Streaming. It is not part of `make run-all-local` or the default local
  benchmark matrix.

---

## Final Deliverables

The final submission will include:

- Final PDF report
- GitHub repository link
- Source code
- SQL scripts
- Execution scripts
- Benchmark results
- Output samples
- Tables and charts
- Reproducibility documentation

---

## License

This project is intended for academic use.

A license can be added later if the repository is made public.

---

## Author

**Luca Foresti**

Roma Tre University  
Big Data Course
