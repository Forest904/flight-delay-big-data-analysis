# Product Requirements Document
## Flight Delay Big Data Analysis Platform

**Project:** Big Data Course — Second Project  
**Dataset:** 2024 Flight Delay Dataset  
**Institution:** Roma Tre University  
**Submission Deadline:** 4 June 2026  
**Document Version:** 1.0  
**Owner:** Luca Foresti  
**Repository:** To be added after GitHub setup

---

## 1. Executive Summary

This project aims to design and implement a reproducible big-data analytics pipeline for analyzing the 2024 Flight Delay Dataset, a large CSV dataset containing more than 7 million flight records and approximately 35 columns related to flights, delays, cancellations, diversions, airports, airlines, and operational attributes.

The system will ingest the raw flight dataset, clean and normalize it, generate scalable input datasets of different sizes, execute selected analytical jobs using at least three big-data technologies, and produce benchmark results, output samples, charts, and a final PDF report.

The recommended technologies are:

- Apache Spark SQL
- Apache Spark Core
- Apache Hive
- Optional extension: Hadoop MapReduce

The final deliverables will include a GitHub repository containing the complete source code, execution scripts, documentation, and reproducibility instructions, plus a final PDF report.

---

## 2. Project Objectives

The primary objective is to build a complete big-data analysis project that compares the use of different technologies on a real dataset of significant size.

The project must address the following goals:

1. Prepare and clean the 2024 Flight Delay Dataset.
2. Implement at least two required analytical tasks.
3. Execute the analyses using at least three technologies among MapReduce, Hive, Spark Core, and Spark SQL.
4. Compare execution performance across technologies.
5. Evaluate scalability by varying input size and, where possible, execution setting.
6. Produce result samples, benchmark tables, and charts.
7. Discuss the strengths and weaknesses of each technology.
8. Provide a reproducible GitHub repository and final PDF report.

---

## 3. Scope

### 3.1 In Scope

The project includes:

- Dataset ingestion from Kaggle.
- Local storage of the raw CSV dataset.
- Data preparation and normalization.
- Conversion of prepared data into Parquet format.
- Generation of smaller and larger test datasets.
- Implementation of selected analytical jobs using:
  - Spark SQL
  - Spark Core
  - Hive
- Optional implementation using MapReduce.
- Execution-time benchmarking.
- Comparison of technologies.
- Local execution.
- Docker standalone simulation evidence.
- Future managed-service execution is reserved for a later extension.
- Generation of tables and charts for the final report.
- Final PDF report.
- GitHub repository with code, scripts, and documentation.

### 3.2 Out of Scope

The project will not include:

- Real-time streaming analytics.
- Interactive dashboard development.
- Production deployment to cloud infrastructure.
- Machine learning prediction models.
- Automated Kaggle authentication unless time permits.
- Storing the full dataset inside the GitHub repository.

---

## 4. Success Criteria

The project will be considered successful if it satisfies the following conditions:

| Area | Success Criterion |
|---|---|
| Correctness | At least two required analyses are correctly implemented. |
| Technology coverage | At least three required technologies are used. |
| Reproducibility | The repository includes clear setup and execution instructions. |
| Data preparation | Cleaning and transformation decisions are documented and justified. |
| Benchmarking | Execution times are collected for different input sizes. |
| Scalability | The project evaluates behavior as data size increases. |
| Reporting | The final PDF includes result samples, benchmark tables, charts, and critical discussion. |
| Code quality | The repository is organized, modular, and readable. |

---

## 5. Users and Stakeholders

### 5.1 Primary User

The primary user is the student developing and submitting the project.

### 5.2 Academic Evaluator

The evaluator will review:

- Correctness of implementation.
- Completeness of required analyses.
- Quality of technology comparison.
- Experimental accuracy.
- Scalability discussion.
- Reproducibility of the solution.
- Quality of the final report.

### 5.3 Future Developer

The repository should be understandable by another developer who wants to reproduce, extend, or verify the experiments.

---

## 6. Dataset Requirements

### 6.1 Source Dataset

The project uses the **2024 Flight Delay Dataset** available on Kaggle. The dataset contains more than 7 million flight records in CSV format and includes information about delays, cancellations, diversions, airlines, airports, and operational attributes.

### 6.2 Raw Data Location

The raw dataset must be placed locally under:

```text
data/raw/
```

The full raw dataset must not be committed to GitHub.

### 6.3 Prepared Data Location

The cleaned and normalized dataset must be written to:

```text
data/prepared/flights_2024_clean.parquet
```

### 6.4 Generated Benchmark Datasets

The project should generate datasets of increasing size for scalability testing:

```text
data/generated/flights_100k.parquet
data/generated/flights_500k.parquet
data/generated/flights_1m.parquet
data/generated/flights_3m.parquet
data/generated/flights_7m.parquet
data/generated/flights_14m.parquet
data/generated/flights_28m.parquet
```

Smaller datasets should be created by sampling or selecting portions of the original dataset. Larger datasets should be created through controlled replication, with the procedure documented in the final report.

---

## 7. Data Preparation Requirements

Data preparation is a mandatory part of the project and must be clearly described and justified in the final report.

### 7.1 Required Preparation Steps

The preparation pipeline must:

1. Load the raw CSV dataset.
2. Validate the schema.
3. Select columns relevant to the selected analyses.
4. Normalize column names.
5. Cast numeric fields to appropriate numeric types.
6. Cast date/month fields to appropriate temporal types.
7. Normalize cancellation and diversion indicators.
8. Handle missing delay values.
9. Handle missing cancellation or delay-cause values.
10. Remove records that are unusable for the selected analyses.
11. Write the cleaned dataset in Parquet format.

### 7.2 Recommended Cleaning Rules

| Data Issue | Required Handling |
|---|---|
| Missing airline identifier | Drop record |
| Missing departure airport | Drop record |
| Missing month/date | Drop record or derive month from flight date |
| Missing arrival delay | Exclude from arrival-delay averages |
| Missing departure delay | Exclude from departure-delay averages where appropriate |
| Cancelled flight with missing delay | Keep for cancellation-rate computation |
| Negative delay values | Keep, because they represent early departures or arrivals |
| Missing cancellation code | Replace with `UNKNOWN` |
| Missing delay-cause fields | Treat as null or zero depending on source schema |
| Duplicate rows | Remove only if exact duplicates are detected |

### 7.3 Required Prepared Columns

The prepared dataset should include, where available:

```text
flight_date
month
airline_code
airline_name
origin_airport
destination_airport
departure_delay
arrival_delay
cancelled
diverted
cancellation_code
carrier_delay
weather_delay
nas_delay
security_delay
late_aircraft_delay
```

If some source columns use different names, the preparation layer must normalize them into these canonical names.

---

## 8. Functional Requirements

### 8.1 Data Ingestion

#### Requirement FR-001 — Load Raw Dataset

The system must load the raw CSV dataset from `data/raw/`.

**Acceptance Criteria:**

- The system reads the CSV with header support.
- The schema is printed or logged.
- The number of loaded records is logged.
- Invalid file paths produce clear errors.

---

### 8.2 Data Preparation

#### Requirement FR-002 — Clean and Normalize Dataset

The system must create a cleaned dataset from the raw CSV.

**Acceptance Criteria:**

- Relevant columns are selected.
- Column names are normalized.
- Numeric values are cast correctly.
- Required null-handling rules are applied.
- The prepared dataset is written as Parquet.
- The preparation script logs input rows, output rows, and removed rows.

---

#### Requirement FR-003 — Generate Input Sizes

The system must generate multiple input datasets for benchmarking.

**Acceptance Criteria:**

- Datasets of increasing size are generated.
- The generation method is documented.
- Larger-than-original datasets are generated using controlled replication.
- Each generated dataset includes a record count validation.

---

### 8.3 Analytical Job 1 — Delay Report by Airport and Month

#### Requirement FR-004 — Implement Delay Report

The system must generate a report for each departure airport and month.

For each departure airport, month, and delay range, the output must include:

- Number of flights.
- Average departure delay.
- Average arrival delay.
- Delay range:
  - Low delay: less than 15 minutes.
  - Medium delay: between 15 and 60 minutes.
  - High delay: more than 60 minutes.
- Most frequent causes of cancellation or delay, where available.

**Acceptance Criteria:**

- Output is grouped by departure airport, month, and delay range.
- Delay ranges are calculated consistently across all technologies.
- Flight counts are correct.
- Average delays exclude null delay values where appropriate.
- Outputs from different technologies are comparable.
- The first 10 result rows can be exported for the final report.

---

### 8.4 Analytical Job 2 — Airline-Airport Ranking

#### Requirement FR-005 — Implement Airline-Airport Ranking

The system must generate a performance report for each pair of departure airport and airline.

For each pair, the output must include:

- Departure airport.
- Airline.
- Number of flights operated by the airline at that airport.
- Average departure delay.
- Average arrival delay.
- Cancellation rate.
- Difference between the airline’s average departure delay and the overall average departure delay for that airport.
- Airline ranking at the airport based on average departure delay, from best to worst.

**Acceptance Criteria:**

- Output is grouped by departure airport and airline.
- Airport-level average departure delay is computed.
- Airline-specific average departure delay is computed.
- Difference from airport average is computed.
- Ranking is generated within each airport.
- Outputs from different technologies are comparable.
- The first 10 result rows can be exported for the final report.

---

### 8.5 Technology Implementations

#### Requirement FR-006 — Spark SQL Implementation

The system must implement the selected analytical jobs using Spark SQL.

**Acceptance Criteria:**

- Spark reads the prepared Parquet dataset.
- Jobs are expressed using DataFrame operations and/or SQL queries.
- Outputs are written to `outputs/spark_sql/`.
- Execution time is logged.

---

#### Requirement FR-007 — Spark Core Implementation

The system must implement the selected analytical jobs using Spark Core RDD transformations.

**Acceptance Criteria:**

- Spark reads the prepared dataset.
- Jobs are expressed using RDD operations such as `map`, `filter`, `reduceByKey`, `groupByKey`, and joins.
- Outputs are written to `outputs/spark_core/`.
- Execution time is logged.
- Implementation choices are documented for comparison against Spark SQL.

---

#### Requirement FR-008 — Hive Implementation

The system must implement the selected analytical jobs using HiveQL.

**Acceptance Criteria:**

- Hive tables are created for the prepared dataset.
- Data can be loaded into Hive external or managed tables.
- HiveQL scripts produce the required outputs.
- Outputs are written to `outputs/hive/`.
- Execution time is logged.

---

#### Requirement FR-009 — Optional MapReduce Implementation

The system may implement one or more jobs using Hadoop MapReduce.

**Acceptance Criteria:**

- Mapper and reducer logic are documented.
- Output matches the expected analytical result.
- Execution time is logged.
- Implementation complexity is discussed in the final report.

---

### 8.6 Benchmarking

#### Requirement FR-010 — Collect Execution Metrics

The system must collect execution-time metrics for each technology, job, input size, and environment.

**Benchmark fields:**

```text
technology
job_name
input_size
environment
execution_setting
execution_time_seconds
records_processed
output_rows
timestamp
```

**Acceptance Criteria:**

- Metrics are saved in CSV or JSON format.
- Local execution results are stored under `experiments/results/local/`.
- Docker standalone simulation results, if available, are stored under `experiments/results/docker-simulation/`.
- Failed runs are logged with error information.

---

#### Requirement FR-011 — Generate Benchmark Charts

The system must generate tables and charts comparing execution times.

**Acceptance Criteria:**

- Charts compare execution time by technology.
- Charts compare execution time by input size.
- Charts distinguish local and Docker standalone simulation execution where available.
- Generated figures are saved under `report/figures/`.

---

### 8.7 Reporting

#### Requirement FR-012 — Produce Final Report

The system must support production of a final PDF report.

The report must include:

- Data preparation description.
- Implementation choices for each selected technology.
- Pseudocode or textual explanation of each job.
- First 10 rows of produced results.
- Execution-time tables.
- Execution-time charts.
- Critical comparison of technologies.
- Discussion of scalability.
- Discussion of shuffle, aggregation, and preparation costs.
- GitHub repository link.

**Acceptance Criteria:**

- Final report is exported as PDF.
- All required sections are present.
- Figures and tables are included.
- GitHub link is included.
- The report clearly explains how experiments can be reproduced.

---

## 9. Non-Functional Requirements

### 9.1 Scalability

The system must support processing the full dataset and generated larger datasets.

**Requirements:**

- Jobs must run on datasets from 100k records to at least the full 7M+ dataset.
- Larger replicated datasets should be supported where hardware allows.
- The architecture must support local execution and Docker standalone simulation,
  while leaving room for a future managed execution service.

---

### 9.2 Reproducibility

The project must be reproducible from the GitHub repository.

**Requirements:**

- All execution commands must be documented.
- Scripts must use relative paths where possible.
- Configuration should be stored under `config/`.
- The raw dataset should not be committed.
- The README must explain how to obtain and place the dataset.
- Environment setup must be documented.

---

### 9.3 Maintainability

The codebase must be modular and understandable.

**Requirements:**

- Common logic should be placed in `src/common/`.
- Each technology must have its own directory.
- Analytical jobs must be separated by task.
- Scripts must have descriptive names.
- Output paths must be consistent.

---

### 9.4 Performance Observability

Each job must log:

- Start time.
- End time.
- Execution duration.
- Input path.
- Output path.
- Number of records processed, where possible.
- Technology used.
- Job name.

---

### 9.5 Portability

The project should run in at least one local environment and should be adaptable
to a future managed execution service.

**Requirements:**

- Local execution should be supported through scripts and/or Docker Compose.
- Docker standalone simulation should be supported through a separate configuration
  file; future managed-service execution should use its own configuration.
- Configuration must avoid hard-coded absolute paths.

---

## 10. Recommended Technology Stack

| Layer | Technology |
|---|---|
| Programming language | Python 3.11+ |
| Main processing engine | Apache Spark |
| Spark APIs | PySpark, Spark SQL, Spark Core |
| SQL-on-Hadoop | Apache Hive |
| Storage format | CSV raw, Parquet prepared |
| Local orchestration | Docker Compose |
| Scripts | Bash |
| Configuration | YAML |
| Benchmark logs | CSV/JSON |
| Charts | Python, matplotlib |
| Documentation | Markdown |
| Final report | PDF |
| Version control | Git + GitHub |

---

## 11. Repository Structure

The GitHub repository should use the following structure:

```text
big-data-flight-delay-analysis/
│
├── README.md
├── Makefile
├── docker-compose.yml
├── requirements.txt
├── .gitignore
│
├── config/
│   ├── local.yaml
│   ├── docker_simulation.yaml
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
│   ├── run_docker_simulation.sh
│   └── collect_results.sh
│
├── experiments/
│   ├── benchmark_plan.md
│   ├── input_sizes.yaml
│   ├── run_benchmarks.py
│   └── results/
│       ├── local/
│       └── docker-simulation/
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

## 12. System Architecture

The system will follow a layered batch-processing architecture:

```text
Raw Kaggle CSV
      ↓
Data Preparation Layer
      ↓
Cleaned Parquet Dataset
      ↓
Generated Input Sizes
      ↓
Technology-Specific Analytical Jobs
      ↓
Output Results
      ↓
Benchmark Logs
      ↓
Charts, Tables, Final Report
```

### 12.1 Data Layer

Responsible for storing:

- Raw CSV data.
- Cleaned Parquet data.
- Generated benchmark datasets.
- Analytical outputs.

### 12.2 Processing Layer

Responsible for executing:

- Spark SQL jobs.
- Spark Core jobs.
- HiveQL jobs.
- Optional MapReduce jobs.

### 12.3 Experiment Layer

Responsible for:

- Running jobs across input sizes.
- Measuring execution times.
- Collecting benchmark metrics.
- Producing comparison-ready results.

### 12.4 Reporting Layer

Responsible for:

- Exporting first 10 rows of outputs.
- Generating benchmark charts.
- Producing the final report.

---

## 13. Analytical Specifications

### 13.1 Analysis 1: Delay Report by Airport and Month

#### Input

Prepared flight dataset.

#### Grouping Keys

```text
origin_airport
month
delay_range
```

#### Delay Range Definition

```text
low_delay: departure_delay < 15
medium_delay: 15 <= departure_delay <= 60
high_delay: departure_delay > 60
```

#### Output Fields

```text
origin_airport
month
delay_range
flight_count
avg_departure_delay
avg_arrival_delay
top_delay_or_cancellation_causes
```

#### Notes

Cancelled flights should contribute to total flight counts and cancellation-related analysis, but they may have null delay values. Null delay values should not distort average delay calculations.

---

### 13.2 Analysis 2: Airline-Airport Ranking

#### Input

Prepared flight dataset.

#### Grouping Keys

```text
origin_airport
airline_code or airline_name
```

#### Output Fields

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

#### Ranking Rule

Airlines should be ranked within each departure airport by average departure delay in ascending order.

```text
rank 1 = best average departure delay
higher rank = worse average departure delay
```

#### Notes

This analysis is expected to highlight differences in expressiveness between technologies. Spark SQL can use window functions, while Spark Core requires more manual grouping and sorting logic.

---

## 14. Benchmarking Requirements

### 14.1 Benchmark Dimensions

Benchmarks must vary:

- Technology.
- Analytical job.
- Input size.
- Execution environment.
- Execution setting, where possible.

### 14.2 Required Benchmark Matrix

| Environment | Input Sizes | Technologies |
|---|---:|---|
| Local | 100k, 500k, 1M, 3M, 7M | Spark SQL, Spark Core, Hive |
| Docker standalone simulation, if available | 100k, 500k, 1M | Spark SQL, Spark Core, Hive |

### 14.3 Metrics Schema

Benchmark results should be stored with this schema:

```text
technology
job_name
input_size_label
input_records
environment
execution_setting
execution_time_seconds
output_rows
status
timestamp
```

### 14.4 Benchmark Output Files

```text
experiments/results/local/benchmark_results.csv
experiments/results/docker-simulation/benchmark_results.csv
```

---

## 15. Deliverables

The final submission must include:

1. Final PDF report.
2. GitHub repository containing:
   - Source code.
   - Execution scripts.
   - SQL scripts.
   - Documentation.
   - Benchmark results.
   - Instructions for reproduction.
3. Sample output rows.
4. Benchmark tables.
5. Benchmark charts.

---

## 16. Milestones

| Milestone | Description | Output |
|---|---|---|
| M1 | Repository setup | GitHub repo, folder structure, README |
| M2 | Dataset inspection | Schema notes, initial row counts |
| M3 | Data preparation | Cleaned Parquet dataset |
| M4 | Spark SQL Analysis 1 | First working analytical job |
| M5 | Spark SQL Analysis 2 | Second working analytical job |
| M6 | Spark Core implementations | RDD-based versions |
| M7 | Hive implementations | HiveQL versions |
| M8 | Benchmarking scripts | Automated experiment runner |
| M9 | Benchmark execution | CSV benchmark results |
| M10 | Charts and tables | Report-ready visualizations |
| M11 | Final report | PDF report |
| M12 | Final repository cleanup | Reproducible GitHub submission |

---

## 17. Implementation Plan

### Phase 1 — Foundation

Tasks:

- Create GitHub repository.
- Add project structure.
- Add `.gitignore`.
- Add README skeleton.
- Add `requirements.txt`.
- Add configuration files.
- Add empty scripts.

Deliverables:

```text
README.md
Makefile
config/
src/
scripts/
docs/
```

---

### Phase 2 — Data Exploration and Preparation

Tasks:

- Load raw CSV using PySpark.
- Print schema.
- Count records.
- Inspect null values.
- Select relevant columns.
- Normalize column names.
- Cast data types.
- Write cleaned Parquet output.

Deliverables:

```text
src/preparation/prepare_spark.py
data/prepared/flights_2024_clean.parquet
docs/data_preparation.md
```

---

### Phase 3 — Spark SQL Jobs

Tasks:

- Implement delay report by airport and month.
- Implement airline-airport ranking.
- Write outputs.
- Export first 10 rows.
- Log execution times.

Deliverables:

```text
src/spark_sql/analysis_delay_by_airport_month.py
src/spark_sql/analysis_airline_airport_ranking.py
outputs/spark_sql/
```

---

### Phase 4 — Spark Core Jobs

Tasks:

- Reimplement both analyses using RDD transformations.
- Ensure outputs are equivalent to Spark SQL outputs.
- Log execution times.
- Document implementation differences.

Deliverables:

```text
src/spark_core/analysis_delay_by_airport_month.py
src/spark_core/analysis_airline_airport_ranking.py
outputs/spark_core/
```

---

### Phase 5 — Hive Jobs

Tasks:

- Define Hive schema.
- Load prepared data.
- Implement both analyses in HiveQL.
- Export outputs.
- Log execution times.

Deliverables:

```text
src/hive/ddl.sql
src/hive/load_data.sql
src/hive/analysis_delay_by_airport_month.sql
src/hive/analysis_airline_airport_ranking.sql
outputs/hive/
```

---

### Phase 6 — Benchmarking

Tasks:

- Generate input datasets.
- Run each job for each input size.
- Store metrics.
- Validate output rows.
- Generate benchmark tables.

Deliverables:

```text
src/preparation/generate_input_sizes.py
experiments/run_benchmarks.py
experiments/results/
```

---

### Phase 7 — Reporting

Tasks:

- Generate charts.
- Add first 10 rows of each job output.
- Write final discussion.
- Export report to PDF.

Deliverables:

```text
report/final_report.md
report/figures/
report/tables/
report/final_report.pdf
```

---

## 18. Makefile Requirements

The project should expose the following commands:

```makefile
setup
prepare
generate-sizes
run-spark-sql
run-spark-core
run-hive
benchmark-local
benchmark-docker-simulation
charts
report
clean
```

Expected usage:

```bash
make setup
make prepare
make generate-sizes
make benchmark-local
make charts
make report
```

---

## 19. README Requirements

The README must include:

```text
Project objective
Dataset description
Technologies used
Analyses implemented
Repository structure
Setup instructions
Dataset download instructions
Data preparation instructions
How to run Spark SQL jobs
How to run Spark Core jobs
How to run Hive jobs
How to run benchmarks
How to reproduce the report
Known limitations
```

The README must explicitly state:

```text
The original Kaggle dataset is not included in this repository.
Download it manually from Kaggle and place it under data/raw/.
```

---

## 20. Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Dataset column names differ from expectations | Jobs may fail | Build a schema-normalization layer |
| Local machine cannot process larger datasets | Benchmarking may be limited | Use smaller local sizes and document hardware limits |
| Hive setup takes too long | Delays implementation | Start with Spark SQL and Spark Core first |
| Future managed execution service unavailable | Scalability section weaker | Use controlled local scaling and Docker standalone simulation while clearly explaining the limitation |
| MapReduce too verbose | Time loss | Treat MapReduce as optional |
| Outputs differ across technologies | Comparison becomes unreliable | Use Spark SQL as correctness reference |
| Large files accidentally committed | GitHub repository becomes unusable | Use `.gitignore` for `data/`, `outputs/`, and benchmark artifacts |

---

## 21. Key Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Main language | Python | Faster development and easier reporting |
| Prepared format | Parquet | Better analytical performance than CSV |
| Primary correctness reference | Spark SQL | Most expressive and concise |
| Additional Spark implementation | Spark Core | Useful comparison against lower-level API |
| SQL baseline | Hive | Required big-data technology and good SQL comparison |
| Larger input generation | Controlled replication | Supports scalability testing |
| Raw data in GitHub | No | Dataset is too large and externally hosted |
| Benchmark format | CSV | Easy to inspect and plot |
| Report format | Markdown to PDF | Easy to version and export |

---

## 22. Open Questions

These decisions should be finalized during implementation:

1. What are the exact column names in the Kaggle CSV?
2. Should a real managed execution service be added in a future project phase?
3. Will MapReduce be implemented as an optional fourth technology?
4. Should outputs be written as CSV, Parquet, or both?
5. Should cancellation causes and delay causes be combined into one “cause” field or reported separately?
6. What local hardware will be used for benchmarks?
7. What docker simulation configuration, if any, will be used?

---

## 23. Final Acceptance Checklist

Before submission, the project must satisfy this checklist:

```text
[ ] GitHub repository created
[ ] Raw dataset download instructions documented
[ ] Dataset not committed to GitHub
[ ] Data preparation script implemented
[ ] Data preparation choices documented
[ ] Cleaned Parquet dataset generated
[ ] Input-size generation implemented
[ ] Analysis 1 implemented in Spark SQL
[ ] Analysis 1 implemented in Spark Core
[ ] Analysis 1 implemented in Hive
[ ] Analysis 2 implemented in Spark SQL
[ ] Analysis 2 implemented in Spark Core
[ ] Analysis 2 implemented in Hive
[ ] Benchmark scripts implemented
[ ] Local benchmark results collected
[ ] Docker standalone simulation benchmark results collected or limitation documented
[ ] First 10 rows of results exported
[ ] Benchmark tables generated
[ ] Benchmark charts generated
[ ] Technology comparison written
[ ] Scalability discussion written
[ ] Shuffle and aggregation discussion written
[ ] Final PDF report generated
[ ] GitHub link added to report
[ ] README includes reproduction instructions
```

---

## 24. Definition of Done

The project is complete when:

1. The repository contains all source code, scripts, SQL files, documentation, and reproduction instructions.
2. The selected analyses run successfully using at least three required technologies.
3. The project produces comparable outputs across technologies.
4. Execution-time metrics are collected for multiple input sizes.
5. Benchmark tables and charts are included in the final report.
6. The final report critically discusses expressiveness, ease of implementation, efficiency, scalability, shuffle, aggregation, and data-preparation costs.
7. The final PDF report and GitHub repository are ready for submission.
