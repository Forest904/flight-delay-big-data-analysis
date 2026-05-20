# Project Roadmap

## North Star

Build a complete, reproducible, well-benchmarked big-data assignment submission using the 2024 Flight Delay dataset, with two analyses implemented in Spark SQL, Spark Core, and Hive. The final submission should make correctness, scalability, implementation tradeoffs, and reproducibility easy for the evaluator to verify.

## Current State

- [x] Tooling installed and verified: Python 3.12, PySpark 4.1.1, Java 17, Docker Desktop, Docker Compose, and Make.
- [x] Repository foundation scaffolded locally.
- [ ] M1 foundation commit created.
- [x] Kaggle dataset downloaded.
- [x] Raw dataset schema inspected.
- [x] Canonical prepared Parquet dataset created and validated.
- [ ] MapReduce intentionally out of scope.
- [ ] Docker-based cluster simulation planned as grade-enhancing evidence if stable.

## Working Principles

- Treat Spark SQL as the correctness reference, then match Spark Core and Hive outputs against it.
- Preserve reproducibility through Make targets, configs, scripts, and documented commands.
- Generate evidence as the project progresses: row counts, first 10 output rows, benchmark CSVs, charts, and report notes.
- Keep raw data, prepared data, generated data, outputs, and logs out of Git unless they are curated report artifacts.
- Prefer completing the required three technologies well before adding optional extras.

## Milestone Roadmap

### M1 - Repository Foundation

Status: complete.

Goal: make the repository runnable and organized before dataset work begins.

Deliverables:

- [x] Project directory structure.
- [x] `Makefile` with stable public targets.
- [x] `requirements.txt` with direct dependency pins.
- [x] Local, cluster, and column configuration files.
- [x] Environment smoke check script.
- [x] Dataset download instructions.
- [x] Docker Compose placeholder.
- [x] `.gitignore` policy for large artifacts.

Acceptance criteria:

- [x] `make check-env` passes when Docker Desktop is running.
- [x] `make setup` is idempotent.
- [x] Future milestone targets fail clearly while unimplemented.
- [x] Commit foundation changes with a clear message.

Grading evidence:

- Reproducible setup entrypoints exist.
- Repository organization matches the assignment and PRD.

### M2 - Dataset Acquisition and Schema Inspection

Goal: obtain the raw dataset and replace assumptions with measured facts.

Deliverables:

- [x] Kaggle credentials documented locally, not committed. N/A for this run because the dataset was downloaded manually; optional CLI redownload guidance remains in `scripts/download_dataset.md`.
- [x] Dataset downloaded under `data/raw/`.
- [x] Raw filename confirmed against `config/local.yaml`.
- [x] Schema, column names, types, row count, and sample rows inspected.
- [x] Null counts collected for analysis-critical fields.
- [x] `docs/data_preparation.md` started with schema findings.

Acceptance criteria:

- [x] Raw dataset can be located by config.
- [x] Total row count is recorded.
- [x] Required analysis columns are mapped to canonical names or flagged.
- [x] Dataset is confirmed ignored by Git.

Grading evidence:

- Data preparation choices are grounded in actual dataset properties.
- The report can cite initial schema and quality observations.

### M3 - Data Preparation Pipeline

Status: complete.

Goal: create the canonical cleaned Parquet dataset used by every technology.

Deliverables:

- [x] PySpark preparation script under `src/preparation/`.
- [x] Canonical columns produced: date/month, airline, airports, delays, cancellation/diversion, and delay causes.
- [x] Cleaning rules implemented and documented.
- [x] Prepared Parquet written to `data/prepared/flights_2024_clean.parquet`.
- [x] Preparation metrics logged: input rows, output rows, removed rows, null handling summary.
- [x] `make prepare` wired to the preparation script.

Acceptance criteria:

- [x] `make prepare` runs from a clean shell after dataset download.
- [x] Prepared Parquet loads successfully with Spark.
- [x] Cancelled flights are kept for cancellation-rate analysis.
- [x] Null delay values do not distort averages.
- [x] Negative delays are preserved.

Grading evidence:

- Mandatory data preparation is implemented, justified, and repeatable.
- Prepared data becomes a stable input for all analyses.

### M4 - Spark SQL Analyses

Status: complete.

Goal: implement both selected analyses in the most expressive API and use them as reference outputs.

Deliverables:

- [x] Delay report by airport, month, and delay range.
- [x] Airline-airport anomalous delay ranking.
- [x] Output writing under `outputs/spark_sql/`.
- [x] First 10 rows exported for each analysis.
- [x] Runtime metrics captured.
- [x] `make run-spark-sql` wired.

Acceptance criteria:

- [x] Delay ranges are implemented consistently: low `< 15`, medium `15 <= delay <= 60`, high `> 60`.
- [x] Ranking uses airport-level partitioning and average departure delay ascending.
- [x] Cancellation rates are computed from all relevant flights.
- [x] Output schemas are stable and documented.

Grading evidence:

- Correct reference implementation for both required jobs.
- Strong expressiveness discussion point for SQL/window functions.

### M5 - Spark Core Analyses

Status: complete.

Goal: reimplement both analyses with RDD transformations and compare against Spark SQL.

Deliverables:

- [x] RDD version of delay report.
- [x] RDD version of airline-airport ranking.
- [x] Output writing under `outputs/spark_core/`.
- [x] First 10 rows exported for each analysis.
- [x] Runtime metrics captured.
- [x] `make run-spark-core` wired.

Acceptance criteria:

- [x] Spark Core outputs match Spark SQL on grouping keys and numeric fields within documented tolerance.
- [x] Ranking order matches Spark SQL for comparable records.
- [x] Implementation avoids unnecessary `groupByKey` where a safer aggregation pattern is practical.

Grading evidence:

- Clear comparison between declarative Spark SQL and lower-level RDD implementation effort.
- Shuffle and aggregation costs can be discussed with concrete examples.

### M6 - Hive Environment and HiveQL Analyses

Status: complete.

Goal: complete the third required technology using Docker-based Hive/Hadoop services.

Deliverables:

- [x] Docker Compose Hive stack.
- [x] Hive DDL for prepared dataset.
- [x] Hive load or external table setup.
- [x] HiveQL version of both analyses.
- [x] Output writing under `outputs/hive/`.
- [x] First 10 rows exported for each analysis.
- [x] `make run-hive` wired.

Acceptance criteria:

- [x] Hive starts from Docker Compose.
- [x] Hive can read the prepared dataset or a Hive-compatible export of it.
- [x] Hive outputs are comparable to Spark SQL outputs.
- [x] Hive run times are logged.

Grading evidence:

- Three required technologies are complete.
- SQL-on-Hadoop tradeoffs can be compared against Spark SQL.

### M7 - Input Size Generation

Status: complete for default local sizes; optional 14M/28M generation is available behind an explicit flag.

Goal: create controlled datasets for scalability experiments.

Deliverables:

- [x] Generator script under `src/preparation/`.
- [x] Datasets for 100k, 500k, 1M, 3M, and full-size local runs where hardware allows.
- [ ] Replicated 14M and 28M datasets if local storage and time allow.
- [x] Record-count validation for every generated dataset.
- [x] `make generate-sizes` wired.

Acceptance criteria:

- [x] Smaller datasets are sampled or selected from original data.
- [x] Larger datasets are generated through documented controlled replication.
- [x] Generated datasets are ignored by Git.

Grading evidence:

- Scalability experiments vary input size as requested.
- Replication method is explainable in the final report.

### M8 - Benchmark Runner

Status: complete for local benchmark orchestration.

Goal: automate local timing collection across jobs, technologies, and input sizes.

Deliverables:

- [x] `experiments/run_benchmarks.py`.
- [x] Benchmark result schema implemented.
- [x] Local benchmark CSV under `experiments/results/local/`.
- [x] Failure logging for unsuccessful runs.
- [x] `make benchmark-local` wired.

Acceptance criteria:

- [x] Benchmark rows include technology, job name, input label, records, environment, cluster size, duration, output rows, status, and timestamp.
- [x] Repeated benchmark runs append or write clearly versioned results.
- [x] Failed jobs do not corrupt completed metrics.

Grading evidence:

- Execution-time comparison is systematic, not manually assembled.
- Benchmark data can feed report tables and charts directly.

### M9 - Docker Cluster Simulation

Goal: add cluster-style evidence if the Docker setup is stable enough.

Deliverables:

- [ ] Docker Compose services for Spark master/workers or equivalent simulation.
- [ ] Cluster config updated with real service addresses.
- [ ] Cluster benchmark results under `experiments/results/cluster/`.
- [ ] Clear documentation of simulated cluster limits.
- [ ] `make benchmark-cluster` wired if the setup is reliable.

Acceptance criteria:

- [ ] Cluster simulation runs at least one input size for each required technology, or limitations are documented.
- [ ] Results distinguish local mode from Docker cluster simulation.
- [ ] The report does not overclaim simulation results as a real production cluster.

Grading evidence:

- Addresses the assignment encouragement to vary execution setting and cluster size where possible.
- Gives useful scalability discussion even without a university cluster.

### M10 - Charts and Tables

Goal: turn benchmark outputs and sample results into report-ready artifacts.

Deliverables:

- [ ] Chart generation script.
- [ ] Execution-time charts by technology and input size.
- [ ] Tables with benchmark summaries.
- [ ] First 10 result rows for each job and technology.
- [ ] `make charts` wired.

Acceptance criteria:

- [ ] Figures are saved under `report/figures/`.
- [ ] Tables are saved under `report/tables/`.
- [ ] Artifacts are small enough to commit.
- [ ] Chart labels and units are clear.

Grading evidence:

- Final report has concrete visual and tabular support.
- Comparisons are easy for the evaluator to inspect.

### M11 - Final Report

Goal: write and export the PDF submission report.

Deliverables:

- [ ] `report/final_report.md`.
- [ ] `report/final_report.pdf`.
- [ ] Data preparation section.
- [ ] Implementation choices and pseudocode or textual explanation for each technology.
- [ ] First 10 rows of produced results.
- [ ] Benchmark tables and charts.
- [ ] Critical comparison and scalability discussion.
- [ ] GitHub repository link.
- [ ] `make report` wired.

Acceptance criteria:

- [ ] Report directly addresses every required item from the assignment.
- [ ] Claims are supported by produced outputs or benchmark files.
- [ ] Limitations are honest and specific.
- [ ] PDF renders cleanly.

Grading evidence:

- The report is the main evaluator-facing proof of correctness, experimentation, and reflection.

### M12 - Submission Hardening

Goal: make the repository and report safe to submit.

Deliverables:

- [ ] Final README reproduction pass.
- [ ] Final `make check-env` pass.
- [ ] Final local smoke run for preparation and all implemented analyses.
- [ ] Git status check for accidental data/output files.
- [ ] GitHub link added to README and report.
- [ ] Final PDF reviewed.
- [ ] Tagged or clearly identified submission commit.

Acceptance criteria:

- [ ] A fresh clone can follow the documented setup path.
- [ ] Raw data is not committed.
- [ ] Essential scripts, configs, SQL, docs, benchmark summaries, tables, and figures are committed.
- [ ] The repository and PDF are ready before submission.

Grading evidence:

- Reproducibility and polish are visible, not assumed.

## Perfect Grade Checklist

- [ ] Correctness: both selected analyses produce consistent outputs across Spark SQL, Spark Core, and Hive.
- [ ] Completeness: Spark SQL, Spark Core, and Hive are all implemented for both jobs.
- [x] Data preparation: cleaning, normalization, and column mapping are justified and documented.
- [ ] Reproducibility: setup, preparation, execution, benchmarking, charts, and report generation have stable commands.
- [ ] Experimental quality: benchmarks vary technology, job, input size, and execution setting where feasible.
- [ ] Scalability: input-size generation is controlled and explained.
- [ ] Critical discussion: report covers expressiveness, ease of implementation, efficiency, scalability, shuffle, aggregation, and preparation costs.
- [ ] Deliverables: final PDF, GitHub repository, source code, scripts, SQL files, docs, benchmark results, charts, and tables are present.
- [ ] Repository hygiene: raw data and bulky generated artifacts are ignored.

## Risk Register

| Risk | Mitigation |
|---|---|
| Dataset schema differs from expectations | Inspect schema in M2 and use `config/columns.yaml` aliases before implementing preparation. |
| Hive setup becomes time-consuming | Finish Spark SQL and Spark Core first, then isolate Hive in the Docker milestone. |
| Local hardware cannot handle full or replicated datasets | Use smaller sizes, document limits, and include controlled replication only where feasible. |
| Outputs differ across technologies | Treat Spark SQL as the reference and add comparison checks before benchmarking. |
| Windows local preparation without Hadoop `winutils.exe` uses a PyArrow writer that streams prepared rows through the driver | Treat this as a compatibility fallback only; do not use it as scalability evidence for M7/M8 benchmark claims. |
| Prepared Parquet directory reads can differ on Windows without Hadoop native tools | Use the shared prepared-data resolver in `src/common/prepared_data.py` for Spark jobs so all technologies agree on the canonical directory shape. |
| Docker cluster simulation is unstable | Keep local benchmarks as the required baseline and document simulation limits honestly. |
| Large files are accidentally committed | Use `.gitignore`, `git status --ignored`, and final submission checks. |
| Report falls behind implementation | Capture metrics, sample rows, and notes at each milestone instead of reconstructing everything at the end. |

## Stable Commands

```powershell
make setup
make check-env
make prepare
make generate-sizes
make run-spark-sql
make run-spark-core
make run-spark-core-native
make run-spark-core-docker
make run-hive
make benchmark-local
make charts
make report
```
