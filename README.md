# Flight Delay Big Data Analysis

As-built big-data coursework project for the 2024 Flight Delay Dataset. The
repository prepares the raw Kaggle CSV, runs two analytical workflows across
multiple big-data technologies, validates comparable outputs, and produces
benchmark evidence for the final report.

Repository: <https://github.com/Forest904/flight-delay-big-data-analysis.git>

## Current Scope

- Core technologies: Spark SQL, Spark Core, and Hive.
- Stretch technology: Docker-local Hadoop Streaming MapReduce.
- Execution evidence: local runs, Docker standalone simulation, and completed
  AWS EMR Spark evidence.
- Canonical validation input: `data/prepared/flights_2024_clean.parquet`.
- Final guardrail: `make submission-check`.

The original Kaggle dataset is not included in this repository. Download it
manually and place the CSV at `data/raw/flight_data_2024.csv`.

## Quickstart

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

Useful focused commands:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
make validate-spark-sql
make validate-spark-core
make validate-hive
make validate-mapreduce
make benchmark-local
make benchmark-docker-simulation
make clean
```

## Reproducibility

Use the final gate as the canonical reproduction check:

```powershell
make charts
make report
make submission-check
```

`make submission-check` runs the automated tests, validates comparable outputs
for Spark SQL, Spark Core, Hive, and MapReduce, rebuilds report artifacts, and
checks repository hygiene. The full run order is documented in
`docs/reproducibility.md`; AWS EMR reruns and credential cautions are documented
in `docs/aws_emr.md`.

## Documentation Index

| Scope | Document |
|---|---|
| As-built goals and acceptance contract | [flight_delay_big_data_prd.md](flight_delay_big_data_prd.md) |
| Environment setup and canonical run order | [docs/reproducibility.md](docs/reproducibility.md) |
| Benchmark matrix, repetitions, and evidence policy | [docs/benchmarking.md](docs/benchmarking.md) |
| Final gate, validation, and hygiene checks | [docs/submission_gate.md](docs/submission_gate.md) |
| AWS EMR workflow and credential cautions | [docs/aws_emr.md](docs/aws_emr.md) |
| Dataset preparation and schema rules | [docs/data_preparation.md](docs/data_preparation.md) |
| Spark SQL implementation | [docs/spark_sql_analyses.md](docs/spark_sql_analyses.md) |
| Spark Core implementation | [docs/spark_core_analyses.md](docs/spark_core_analyses.md) |
| Hive implementation | [docs/hive_analyses.md](docs/hive_analyses.md) |
| MapReduce stretch implementation | [docs/mapreduce_analyses.md](docs/mapreduce_analyses.md) |
| Docker standalone simulation | [docs/docker_simulation.md](docs/docker_simulation.md) |
| Dataset download notes | [scripts/download_dataset.md](scripts/download_dataset.md) |

## Report Artifacts

The report source is `report/draft_final_report.md`; the generated PDF is
`report/draft_final_report.pdf`. Curated figures and tables under
`report/figures/` and `report/tables/` are intentionally tracked as submission
evidence.

Raw data, prepared Parquet data, generated inputs, runtime outputs, benchmark
logs, `.env`, and bulky AWS downloads are ignored. Before sharing the repository
or screenshots, rotate any Kaggle or AWS Learner Lab credentials that were used
locally.

## Author

Luca Foresti, Roma Tre University Big Data Course.
