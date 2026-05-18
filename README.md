# Flight Delay Big Data Analysis

Comparative big-data analysis of the **2024 Flight Delay Dataset** using **Spark SQL**, **Spark Core**, and **Hive**, with a focus on data preparation, analytical correctness, execution efficiency, and scalability benchmarking.

This repository is developed for the **Big Data Course — Second Project** at **Roma Tre University**.

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
| Storage format | CSV, Parquet |
| Local orchestration | Docker Compose |
| Scripts | Bash |
| Configuration | YAML |
| Benchmark logs | CSV / JSON |
| Charts | Python, matplotlib |
| Documentation | Markdown |
| Version control | Git + GitHub |

Optional extension:

- Hadoop MapReduce

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
- Most frequent cancellation or delay causes, when available

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
│
├── README.md
├── Makefile
├── docker-compose.yml
├── requirements.txt
├── .gitignore
│
├── config/
│   ├── local.yaml
│   ├── cluster.yaml
│   └── columns.yaml
│
├── data/
│   ├── raw/
│   │   └── .gitkeep
│   ├── prepared/
│   │   └── .gitkeep
│   ├── samples/
│   │   └── .gitkeep
│   └── generated/
│       └── .gitkeep
│
├── src/
│   ├── common/
│   │   ├── schema.py
│   │   ├── paths.py
│   │   ├── metrics.py
│   │   └── utils.py
│   │
│   ├── preparation/
│   │   ├── prepare_spark.py
│   │   └── generate_input_sizes.py
│   │
│   ├── spark_sql/
│   │   ├── analysis_delay_by_airport_month.py
│   │   └── analysis_airline_airport_ranking.py
│   │
│   ├── spark_core/
│   │   ├── analysis_delay_by_airport_month.py
│   │   └── analysis_airline_airport_ranking.py
│   │
│   ├── hive/
│   │   ├── ddl.sql
│   │   ├── load_data.sql
│   │   ├── analysis_delay_by_airport_month.sql
│   │   └── analysis_airline_airport_ranking.sql
│   │
│   └── mapreduce/
│       └── optional/
│
├── scripts/
│   ├── download_dataset.md
│   ├── run_prepare_local.sh
│   ├── run_spark_sql.sh
│   ├── run_spark_core.sh
│   ├── run_hive.sh
│   ├── run_all_local.sh
│   ├── run_all_cluster.sh
│   └── collect_results.sh
│
├── experiments/
│   ├── benchmark_plan.md
│   ├── input_sizes.yaml
│   ├── run_benchmarks.py
│   └── results/
│       ├── local/
│       └── cluster/
│
├── outputs/
│   ├── spark_sql/
│   ├── spark_core/
│   ├── hive/
│   └── mapreduce/
│
├── notebooks/
│   └── exploratory_analysis.ipynb
│
├── report/
│   ├── final_report.md
│   ├── figures/
│   ├── tables/
│   └── final_report.pdf
│
└── docs/
    ├── architecture.md
    ├── data_preparation.md
    ├── reproducibility.md
    └── technology_comparison.md
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
└── raw/
    └── flight_data_2024.csv
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

Or directly:

```bash
bash scripts/run_prepare_local.sh
```

---

## Generated Input Sizes

For benchmarking and scalability analysis, the project generates datasets of different sizes.

Example generated datasets:

```text
data/generated/flights_100k.parquet
data/generated/flights_500k.parquet
data/generated/flights_1m.parquet
data/generated/flights_3m.parquet
data/generated/flights_7m.parquet
data/generated/flights_14m.parquet
data/generated/flights_28m.parquet
```

Smaller datasets are created from portions of the original data. Larger datasets are created through controlled replication and are used only for scalability experiments.

Run:

```bash
make generate-sizes
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/flight-delay-big-data-analysis.git
cd flight-delay-big-data-analysis
```

### 2. Create a Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate
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

### Run Spark Core jobs

```bash
make run-spark-core
```

Or:

```bash
bash scripts/run_spark_core.sh
```

### Run Hive jobs

```bash
make run-hive
```

Or:

```bash
bash scripts/run_hive.sh
```

### Run all local jobs

```bash
make run-all-local
```

---

## Benchmarking

The benchmark runner executes analytical jobs across multiple input sizes and records execution metrics.

Metrics collected include:

```text
technology
job_name
input_size_label
input_records
environment
cluster_size
execution_time_seconds
output_rows
status
timestamp
```

Run local benchmarks:

```bash
make benchmark-local
```

Run cluster benchmarks, if a cluster environment is available:

```bash
make benchmark-cluster
```

Benchmark results are stored in:

```text
experiments/results/local/
experiments/results/cluster/
```

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

---

## Report

The final report is developed in Markdown and exported as PDF.

Report files are stored in:

```text
report/
```

Expected report outputs:

```text
report/final_report.md
report/final_report.pdf
report/figures/
report/tables/
```

Generate charts:

```bash
make charts
```

Generate final report:

```bash
make report
```

---

## Reproducibility

A complete reproduction should follow this sequence:

```bash
make setup
make inspect-raw
make prepare
make generate-sizes
make benchmark-local
make charts
make report
```

If Hive or cluster execution requires additional setup, see:

```text
docs/reproducibility.md
```

---

## Expected Makefile Commands

The project is expected to expose the following commands:

```text
setup
inspect-raw
prepare
generate-sizes
run-spark-sql
run-spark-core
run-hive
run-all-local
benchmark-local
benchmark-cluster
charts
report
clean
```

---

## Experimental Plan

The project compares execution times across:

- Different technologies
- Different analytical jobs
- Different input sizes
- Local and cluster environments, where available

Suggested local benchmark matrix:

| Input Size | Spark SQL | Spark Core | Hive |
|---:|---|---|---|
| 100k | Yes | Yes | Yes |
| 500k | Yes | Yes | Yes |
| 1M | Yes | Yes | Yes |
| 3M | Yes | Yes | Yes |
| 7M+ | Yes | Yes | Yes |

Suggested cluster benchmark matrix:

| Input Size | Spark SQL | Spark Core | Hive |
|---:|---|---|---|
| 1M | Yes | Yes | Yes |
| 3M | Yes | Yes | Yes |
| 7M+ | Yes | Yes | Yes |
| 14M | Yes | Yes | Yes |
| 28M | Yes | Yes | Yes |

---

## Documentation

Additional documentation is stored under:

```text
docs/
```

Recommended documents:

| File | Purpose |
|---|---|
| `architecture.md` | System architecture and data flow |
| `data_preparation.md` | Cleaning rules and schema decisions |
| `reproducibility.md` | Full setup and execution instructions |
| `technology_comparison.md` | Notes comparing Spark SQL, Spark Core, Hive, and optional MapReduce |

---

## Git Ignore Policy

The repository should not track large generated artifacts.

Recommended ignored paths:

```text
data/raw/*
data/prepared/*
data/generated/*
outputs/*
experiments/results/*
report/figures/*
report/tables/*
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
- Larger-than-original datasets are generated through controlled replication, so they are intended for scalability testing rather than new statistical insight.
- Hive execution may require additional local or Docker-based configuration.
- MapReduce is treated as an optional extension unless explicitly implemented.

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
