# 95+ Grade Rescue Roadmap

## North Star

Turn the current project from a solid but imperfect submission into a strict-evaluator-ready Big Data Course project. The immediate goal is to raise the expected grade from about `76/100` to `95+` by fixing requirement gaps, strengthening experimental evidence, improving report traceability, and only then adding MapReduce as the flagship stretch.

## Current Baseline: functional but not yet 95+

The project already has a strong foundation:

- Spark SQL, Spark Core, and Hive implementations exist for two assignment analyses.
- The raw dataset is prepared into a canonical Parquet dataset.
- Input-size generation exists for `100k`, `500k`, `1m`, `3m`, and `full`.
- Benchmark orchestration, chart generation, validators, Docker services, and report-building scripts exist.
- The draft report is readable and honest about limitations.

The project is not yet a `95+` submission because a strict evaluator can still identify requirement misses and weak evidence.

## Target: strict-evaluator-ready submission

Priority labels:

- `P0 grade blocker`: must be fixed before the final submission can be considered high-grade.
- `P1 evidence upgrade`: needed to make conclusions convincing and defensible.
- `P2 polish`: improves reproducibility, presentation, and evaluator confidence.
- `P3 stretch`: optional expansion after the core path is strong.

Definition of done for the rescue path:

- Every selected assignment analysis exactly satisfies the written requirements.
- Spark SQL, Spark Core, and Hive produce validated, comparable outputs.
- Benchmark tables and charts vary input size enough to support scalability discussion.
- Docker execution is described as a standalone simulation unless a true cluster is used.
- The final PDF contains visible or traceable evidence for every required report item.
- A fresh evaluator can reproduce the main workflow from the README and Make targets.

## Grade Gap Map

| Finding | Priority | Planned milestone | Required outcome |
|---|---|---|---|
| Analysis 1 reports only one cause instead of the three most frequent causes | P0 grade blocker | M1 | Delay-analysis output includes top 1, 2, and 3 cause labels plus counts across Spark SQL, Spark Core, and Hive. |
| Benchmark evidence is too narrow | P0/P1 | M2 | Local and Docker simulation benchmarks cover enough input sizes to support scalability claims. |
| Docker "cluster" wording can overclaim | P1 | M2, M3, M4 | Report, charts, configs, and docs consistently use cautious Docker standalone simulation wording. |
| Local charts have only one x-axis point | P1 | M3 | Chart type matches available evidence; line charts are used only when there are at least three input sizes. |
| Per-technology output samples are hidden | P0/P1 | M4 | Final report shows per-technology samples or an appendix with paths, checksums, and validation status. |
| Hardware and runtime configuration are missing from the report | P1 | M2, M4 | Report includes CPU, RAM, OS, Spark/Hive versions, partitions, Docker limits, and topology. |
| README has encoding and reproducibility polish issues | P2 | M5 | README renders cleanly and documents the correct venv-based test command. |
| MapReduce exists only as an empty placeholder | P3 | M6 | MapReduce is either implemented and validated as a stretch or clearly excluded from core grade claims. |

## Milestone Roadmap


### M1 - Fix Analysis 1 Top-Three Causes

Priority: `P0 grade blocker`  
Status: completed.

Goal: make the delay report fully satisfy the assignment requirement for the three most frequent cancellation or delay causes.

Planned interface change:

- Replace the single `top_delay_or_cancellation_cause` output column with:
  - `top_1_cause`
  - `top_1_count`
  - `top_2_cause`
  - `top_2_count`
  - `top_3_cause`
  - `top_3_count`

Implementation tasks:

- [x] Update Spark SQL delay analysis to rank causes per `origin_airport`, `month`, and `delay_range`, then pivot or aggregate the first three causes into the new schema.
- [x] Update Spark Core delay analysis to compute cause counts and emit the same top-three schema with deterministic tie-breaking.
- [x] Update HiveQL delay analysis to emit the same columns.
- [x] Update output-column constants in all affected runners.
- [x] Update validators so Spark Core and Hive compare against Spark SQL for all top-three cause/count fields.
- [x] Regenerate first-10 output tables for all three technologies.
- [x] Update docs and final report language from "top cause" to "top three causes".

Acceptance criteria:

- [x] Spark SQL, Spark Core, and Hive produce the same delay-output keys.
- [x] Top-three cause labels and counts match across technologies.
- [x] Ties are deterministic, using cause count descending and cause label ascending.
- [x] Groups with fewer than three available causes use a documented empty value, such as null cause and zero count.
- [x] Existing ranking analysis remains unchanged except for shared validation/report tooling if needed.

Grading evidence:

- This directly removes the largest requirement-compliance penalty.
- Implemented delay-output schema now emits `top_1_cause`, `top_1_count`, `top_2_cause`, `top_2_count`, `top_3_cause`, and `top_3_count` across Spark SQL, Spark Core, and Hive.
- Verification completed: `pytest` passed with 38 tests, all three technology outputs regenerated successfully, Spark SQL validation passed, Spark Core validation passed against Spark SQL, Hive validation passed against Spark SQL, and `make charts` regenerated first-10 report tables.

### M2 - Strengthen Benchmark Evidence

Priority: `P0 grade blocker` and `P1 evidence upgrade`  
Status: completed.

Goal: make the experimental analysis broad enough to support efficiency and scalability claims.

Benchmark target:

- Local benchmark matrix:
  - [x] `100k`, `500k`, `1m`, and `3m` for Spark SQL, Spark Core, and Hive.
  - [x] `full` for Spark SQL and Spark Core if runtime and hardware allow.
  - [x] Hive full-size run only if it is practical; otherwise document the limit.
- Docker standalone simulation matrix:
  - [x] `100k`, `500k`, and `1m` for Spark SQL, Spark Core, and Hive.
  - [x] Document optional worker-count variation as skipped because the fixed two-worker Docker Compose topology is the reliable M2 setup.

Runtime configuration evidence:

- [x] Record CPU model, core count, RAM, OS, disk type if known, and timestamp of benchmark campaign.
- [x] Record Python, Java, Spark, Hive, Docker, and Docker Compose versions.
- [x] Record Spark master, shuffle partitions, executor/worker topology, worker memory, worker cores, and Docker Desktop CPU/RAM limits.
- [x] Store this as a report-ready artifact, for example `report/tables/environment_summary.*`.

Acceptance criteria:

- [x] Benchmark summary tables no longer rely on only local `100k` and Docker `100k`/`1m`.
- [x] Failed or skipped benchmark cells are explicitly marked with a reason.
- [x] The report can discuss input-size trends without overgeneralizing.
- [x] Docker results are labeled as Docker standalone simulation, not as real distributed-cluster performance.

Grading evidence:

- The project visibly addresses the assignment request to compare execution times while varying input size and, where possible, execution setting.
- Implemented Docker benchmark label standardization from `docker-cluster` to `docker-simulation`, while keeping legacy benchmark CSV rows readable through report-generation normalization.
- Local benchmark campaign completed successfully for `100k`, `500k`, `1m`, `3m`, and `full` across Spark SQL, Spark Core, and Hive: 30/30 expected local job cells succeeded.
- Docker standalone simulation benchmark campaign completed successfully for `100k`, `500k`, and `1m` across Spark SQL, Spark Core, and Hive: 18/18 expected Docker simulation job cells succeeded.
- Generated report-ready benchmark artifacts: `report/tables/benchmark_summary.*`, `report/tables/benchmark_pivot.*`, and `report/tables/benchmark_status.*`.
- Generated runtime configuration artifacts: `report/tables/environment_summary.csv`, `report/tables/environment_summary.md`, and `report/tables/environment_summary.json`.
- Worker-count variation was intentionally not added because the current Docker Compose topology uses two named Spark workers; M2 focuses on input-size variation and documents this limit in the environment summary.
- Verification completed: `.\.venv\Scripts\python.exe -m pytest -q` passed with 44 tests, `make benchmark-local` passed, `make benchmark-cluster` passed, `make charts` regenerated report tables and figures, and `make report` rebuilt `report/draft_final_report.pdf`.

### M3 - Upgrade Charts And Derived Metrics

Priority: `P1 evidence upgrade`  
Status: completed.

Goal: make the final visualizations convincing, readable, and aligned with the amount of data available.

Chart changes:

- [x] Use grouped bar charts when a job/environment has only one or two input sizes.
- [x] Use line charts only when a job/environment has at least three input sizes.
- [x] Keep separate charts for local and Docker standalone simulation unless combining them improves readability.
- [x] Rename chart titles and filenames away from overclaiming "cluster" language where needed.

Derived metrics:

- [x] Add rows-per-second tables per technology, job, environment, and input size.
- [x] Add speedup tables:
  - Spark SQL duration divided by Spark Core duration.
  - Hive duration divided by Spark SQL duration.
  - Hive duration divided by Spark Core duration.
- [x] Add normalized scalability ratios from the `100k` baseline where at least three input sizes exist.
- [x] Include notes explaining startup overhead and why tiny inputs may not show monotonic scaling.

Acceptance criteria:

- [x] No local chart shows a one-point line as if it were a trend.
- [x] Every chart has clear units, input sizes, technology labels, and environment labels.
- [x] Visual claims in the report are directly supported by the plotted data.

Grading evidence:

- The final report becomes stronger on efficiency, scalability, and technology comparison.
- Implemented adaptive execution-time charts: grouped bars for one or two input sizes and line charts only for three or more input sizes.
- Generated report-ready derived metric artifacts: `report/tables/rows_per_second.*`, `report/tables/speedup.*`, and `report/tables/scalability_ratios.*`.
- Kept local and Docker standalone simulation charts separate and preserved normalized `docker-simulation` figure filenames.
- Updated the draft final report with derived-metric references and notes about startup overhead and non-monotonic tiny-input behavior.
- Verification completed: `.\.venv\Scripts\python.exe -m pytest -q` passed with 50 tests, `make charts` regenerated report tables and figures, and `make report` rebuilt `report/draft_final_report.pdf`.

### M4 - Report Rewrite And Evidence Appendix

Priority: `P0 grade blocker` and `P1 evidence upgrade`  
Status: draft report exists, rewrite needed after M1-M3.

Goal: make the PDF read like a complete final submission rather than a compact draft.

Required report updates:

- [ ] Update Analysis 1 explanation and samples for top-three causes.
- [ ] Show first 10 rows for each job and technology, or provide a compact appendix with paths, checksums, and validation status.
- [ ] Add hardware and runtime-configuration table from M2.
- [ ] Add benchmark summary, benchmark pivot, rows/sec, speedup, and normalized scalability tables.
- [ ] Add upgraded charts from M3.
- [ ] Add a short "What is Docker standalone simulation?" paragraph and avoid real-cluster overclaims.
- [ ] Expand critical discussion of:
  - Spark SQL expressiveness and window functions.
  - Spark Core RDD verbosity and accumulator design.
  - Hive overhead and SQL-on-Hadoop tradeoffs.
  - Shuffle and aggregation costs for both selected analyses.
  - Data preparation effects on correctness and benchmark fairness.
  - Startup overhead and why small datasets can distort runtime comparisons.

Acceptance criteria:

- [ ] Every item in the assignment final-report section is explicitly answered.
- [ ] Claims are traceable to committed tables, figures, outputs, or documented commands.
- [ ] Limitations are honest but do not substitute for missing required evidence.
- [ ] The PDF renders cleanly and uses table layouts that fit the page.

Grading evidence:

- The report becomes the evaluator-facing proof that the project is complete, correct, and critically analyzed.

### M5 - Repository Polish And Reproducibility Hardening

Priority: `P1 evidence upgrade` and `P2 polish`  
Status: not started.

Goal: remove friction that could cost easy reproducibility and presentation points.

Tasks:

- [ ] Fix README encoding corruption in tree diagrams and punctuation.
- [ ] Document the reliable test command:
  - `.\.venv\Scripts\python.exe -m pytest -q`
- [ ] Add or update instructions for regenerating:
  - prepared data;
  - input-size datasets;
  - all technology outputs;
  - benchmarks;
  - charts and report tables;
  - final PDF.
- [ ] Replace placeholder `run-all-local` roadmap expectations with either an implemented target or a documented non-goal.
- [ ] Replace placeholder `clean` roadmap expectations with either an implemented safe cleanup target or a documented non-goal.
- [ ] Verify `.gitignore` still keeps raw, prepared, generated, and bulky output files out of Git.
- [ ] Add a final submission checklist to README or report docs.

Acceptance criteria:

- [ ] A fresh clone plus downloaded raw dataset can follow the documented workflow.
- [ ] The README renders without mojibake or broken tree characters.
- [ ] The documented test command passes in the project virtual environment.
- [ ] Git status is clean except for intentionally edited source/report artifacts.

Grading evidence:

- Reproducibility is visible, not assumed.

### M6 - MapReduce Flagship Stretch

Priority: `P3 stretch`  
Status: planned stretch after M1-M5.

Goal: add MapReduce as the flagship expansion only after the required submission path is strong.

Scope:

- [ ] Use Hadoop Streaming with Python mappers and reducers.
- [ ] Use a canonical CSV export derived from prepared Parquet instead of reparsing raw CSV.
- [ ] Reuse existing job names where practical:
  - `delay_by_airport_month`
  - `airline_airport_ranking`
- [ ] Minimum credible stretch: Analysis 1 with the top-three cause schema and benchmark integration.
- [ ] Preferred stretch: both selected analyses implemented and validated.

Artifacts:

- [ ] Source files under `src/mapreduce/`.
- [ ] Outputs under `outputs/mapreduce/`.
- [ ] Runtime metrics following the existing benchmark metadata conventions.
- [ ] Validator comparing MapReduce outputs against Spark SQL.
- [ ] Optional Docker service or documented local Hadoop/Hadoop Streaming setup.
- [ ] Report appendix section if MapReduce is complete enough to discuss.

Acceptance criteria:

- [ ] MapReduce outputs match Spark SQL on keys, numeric fields, ranks if implemented, and top-three causes.
- [ ] Benchmark rows can be included without breaking existing chart/table generation.
- [ ] If incomplete, MapReduce is clearly marked as future work and is not used for grade-critical claims.

Grading evidence:

- A complete MapReduce stretch can raise the project beyond the minimum three-technology requirement and show deeper understanding of distributed-processing tradeoffs.

### M7 - Final Submission Gate

Priority: `P0 grade blocker`  
Status: final checkpoint.

Goal: verify that code, artifacts, report, and repository story are consistent before submission.

Final checks:

- [ ] Run Spark SQL outputs after M1 schema changes.
- [ ] Run Spark Core outputs after M1 schema changes.
- [ ] Run Hive outputs after M1 schema changes.
- [ ] Run Spark Core and Hive validators against Spark SQL.
- [ ] Run MapReduce validator if M6 is implemented.
- [ ] Run the venv test command:
  - `.\.venv\Scripts\python.exe -m pytest -q`
- [ ] Generate report tables and figures.
- [ ] Build the final PDF.
- [ ] Inspect PDF pages manually for broken tables, tiny charts, missing captions, and stale wording.
- [ ] Check Git status for accidental large files.
- [ ] Confirm GitHub repository link appears in README and PDF.

Acceptance criteria:

- [ ] Final PDF and repository agree on outputs, commands, limitations, and terminology.
- [ ] No chart or paragraph describes Docker as a true distributed cluster.
- [ ] Every requirement from the assignment PDF is either satisfied or explicitly scoped as a documented limitation only where optional.
- [ ] The final submission can be defended under a harsh grading review.

Grading evidence:

- This gate protects against regressions introduced while upgrading the project.

## Public Interfaces And Artifact Expectations

Delay-analysis schema:

- Replaced schema:
  - `top_delay_or_cancellation_cause`
- Current schema:
  - `top_1_cause`
  - `top_1_count`
  - `top_2_cause`
  - `top_2_count`
  - `top_3_cause`
  - `top_3_count`

Benchmark artifacts:

- Keep existing benchmark metadata fields: technology, job name, input label, records, environment, cluster-size label, duration, output rows, status, timestamp, input path, and metrics path.
- Add report-ready derived tables for rows/sec, speedup, and normalized scalability.
- Preserve timestamped benchmark CSVs as immutable run evidence.

Report artifacts:

- Benchmark summary and pivot tables.
- First-10 result samples per technology and job, or evidence appendix with paths/checksums.
- Hardware and runtime configuration table.
- Upgraded execution-time charts.
- Speedup and scalability-ratio charts or tables.
- Validation summary table.

Terminology:

- Use "Docker standalone simulation" for the current Docker Compose Spark setup.
- Use "cluster" only for a true multi-node or managed distributed environment.
- Describe Hive as containerized local Hive unless a distributed Hive/Hadoop/YARN setup is actually added.

MapReduce conventions:

- Reuse existing job names and benchmark conventions.
- Validate against Spark SQL before presenting MapReduce as complete.
- Keep MapReduce out of grade-critical claims unless it passes the same acceptance bar as the other technologies.

## Implementation Order

1. M1: fix the actual requirement miss first.
2. M2: collect enough benchmark evidence to support the report.
3. M3: make charts and derived metrics match the evidence.
4. M4: rewrite the final report around the new evidence.
5. M5: harden README and reproducibility.
6. M6: add MapReduce if time remains.
7. M7: run final submission gate.

Cut line if time becomes tight:

- Must ship: M1, M2 core benchmark matrix, M3 chart fixes, M4 report rewrite, M5 README/test-command polish, M7 final gate.
- Nice to ship: full-size local benchmarks, repeated benchmark runs, worker-count variation.
- Stretch only: M6 MapReduce.

## Test And Acceptance Plan

Roadmap rewrite acceptance:

- [ ] `ROADMAP.md` contains no stale "perfect checklist complete" claims.
- [ ] Every grading finding is mapped to a milestone.
- [ ] Required fixes appear before optional expansion.
- [ ] MapReduce is planned as stretch, not as a blocker for the 95+ core path.

Later implementation acceptance captured by this roadmap:

- [ ] The venv pytest command passes.
- [ ] Spark Core and Hive validators match Spark SQL after the schema change.
- [ ] Benchmark charts have enough x-axis evidence to support written claims.
- [ ] Final report avoids calling Docker a real cluster.
- [ ] Report artifacts are regenerated after all schema and benchmark changes.

## Risk Register

| Risk | Impact | Mitigation |
|---|---|---|
| Top-three cause schema change breaks validators and report generation | High | Update outputs, validators, first-10 tables, and docs in the same milestone. |
| Benchmark runs take too long on local hardware | Medium | Prioritize 100k, 500k, 1m, and 3m; treat full-size and Hive full-size as conditional evidence. |
| Docker simulation is mistaken for a real cluster | Medium | Rename charts/report language and explicitly document topology limits. |
| Tiny-input startup overhead creates non-monotonic results | Medium | Explain startup overhead and include rows/sec plus normalized ratios. |
| MapReduce consumes time before required fixes are complete | High | Keep M6 after M1-M5 and do not make it part of the core grade path. |
| README polish is skipped as "minor" | Low | Include README encoding and test command in M5 acceptance. |
| Report falls behind implementation changes | High | Regenerate report artifacts after each output-schema or benchmark change. |
| Large files are accidentally committed | Medium | Keep data/output/log hygiene in M7 final gate. |

## Stable Commands To Preserve Or Improve

```powershell
make setup
make check-env
make prepare
make generate-sizes
make run-spark-sql
make run-spark-core
make run-hive
make benchmark-local
make benchmark-cluster
make charts
make report
.\.venv\Scripts\python.exe -m pytest -q
```

Future command improvements to consider:

- [ ] Implement `make run-all-local` only if it can run the full local workflow reliably.
- [ ] Implement `make clean` only if it safely removes generated artifacts without touching raw data or user work.
- [ ] Add MapReduce commands only after M6 has a validated implementation.
