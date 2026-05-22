# 95+ Grade Upgrade Roadmap: AWS EMR Cluster Evidence

This roadmap focuses on the two highest-impact improvements for the final
submission:

1. Fix the report weaknesses found during professor-style grading.
2. Add real AWS EMR cluster evidence using the AWS Academy Learner Lab budget.

Target outcome: a stronger final report with reproducible local, Docker
standalone simulation, and real AWS EMR cluster experiments.

## Grade Target

- Target grade: 95+.
- Main current weakness: experimental/scalability evidence.
- Main upgrade path: replace "cluster-like" claims with real EMR cluster
  evidence, repeated measurements, larger replicated input, and clearer
  report structure.

## Milestone Checklist

### M0 - AWS Feasibility And Budget Guardrails

**Goal:** confirm that the AWS Learner Lab can safely support the EMR
experiment before running any expensive workloads.

- [x] Verify AWS Academy Learner Lab access.
      Result: STS identity succeeded for account `380623119505`.
- [x] Confirm remaining budget is close to the expected 50 USD allowance.
      Result: Learner Lab budget recorded as `50.00 USD`.
- [x] Confirm the active AWS region; use `us-east-1` unless the lab restricts
      otherwise.
      Result: active region is `us-east-1`.
- [x] Verify service availability for:
  - [x] S3
        Result: `ListBuckets` succeeded.
  - [x] EMR
        Result: `ListClusters` succeeded.
  - [x] EC2
        Result: `m5.large` and `m5.xlarge` are offered in-region.
  - [x] IAM roles
        Result: `EMR_DefaultRole` and `EMR_EC2_DefaultRole` are readable.
  - [x] CloudWatch logs or EMR/S3 logs
        Result: S3 logs are reachable and CloudWatch Logs `DescribeLogGroups`
        succeeded.
- [x] Confirm which EMR-supported EC2 instance types are available in the lab.
      Result: EMR `emr-7.13.0` returned 200 supported instance types.
- [x] Use this fallback instance order:
  1. `m5.xlarge`
  2. `m5.large`
  3. largest EMR-supported instance type allowed by Learner Lab
      Result: selected default instance type is `m5.xlarge`.
- [x] Define the default EMR cluster profile:
  - [x] 1 primary node
  - [x] 2 core nodes
  - [x] Spark installed
        Result: target EMR release is `emr-7.13.0` with Spark.
  - [x] logs written to S3
- [x] Add a hard stop rule: every EMR cluster must be terminated immediately
      after benchmark steps finish.
- [x] Create a budget/cost log table for the report with:
  - [x] cluster profile
  - [x] start time
  - [x] end time
  - [x] estimated AWS cost
  - [x] tested inputs
  - [x] notes and failures
      Result: M0 scaffolding writes `report/tables/aws_feasibility.{json,csv,md}`;
      per-run cost logging remains part of the M4/M6 benchmark workflow.
- [x] Create or select the project S3 bucket for later EMR logs/results.
      Result: `AWS_FLIGHT_DELAY_BUCKET=fd-bda-380623119505-us-east-1` was used
      for the completed M4 EMR runs.

**Acceptance criteria:**

- AWS service availability is known.
- A safe default cluster profile is selected.
- A cleanup rule exists before the first EMR run.
- Project S3 bucket and `AWS_FLIGHT_DELAY_BUCKET` are configured for M4.

### M1 - Report Fixes From Professor-Style Review

**Goal:** address the known report-quality deductions before adding new AWS
material.

- [x] Fix appendix structure so required samples are clearly separated:
  - [x] Spark SQL samples
  - [x] Spark Core samples
  - [x] Hive samples
  - [x] MapReduce stretch samples
- [x] Add a compact requirement-to-output mapping table for both analyses.
- [x] Expand implementation descriptions with short execution plans for:
  - [x] Spark SQL
  - [x] Spark Core
  - [x] Hive
  - [x] MapReduce stretch
- [x] Add a paragraph explaining flat or non-monotonic benchmark timings:
  - [x] startup overhead
  - [x] JVM/container setup
  - [x] cached/prepared Parquet reads
  - [x] small output cardinality
  - [x] single-run measurement limitations
- [x] Reword Docker evidence consistently as "Docker standalone simulation,"
      not a true cluster.

**Acceptance criteria:**

- The report no longer has confusing appendix hierarchy.
- The reader can trace every assignment requirement to a concrete output
  column.
- Docker evidence is clearly scoped and not overclaimed.

### M2 - Stronger Benchmark Methodology

**Goal:** make the benchmark evidence more statistically credible.

- [x] Add repeated-run support to the benchmark workflow.
- [x] Default benchmark repetitions to `3`.
- [x] Keep raw per-run benchmark CSVs as evidence.
- [x] Generate aggregate benchmark tables with:
  - [x] median
  - [x] mean
  - [x] min
  - [x] max
  - [x] standard deviation
- [x] Update charts to use median duration.
- [x] Add variability indicators where feasible.
- [x] Update the report text so it no longer relies on a single timing per
      configuration.

**Acceptance criteria:**

- `make benchmark-local` can run repeated measurements.
- Report tables include aggregate timing statistics.
- Raw benchmark rows remain available for auditability.

### M3 - Larger Input Sizes

**Goal:** improve scalability evidence beyond the original 7M-row dataset.

- [x] Generate and validate `14m` with the existing controlled replication
      support.
- [x] Attempt `28m` only if local storage, runtime, and AWS budget remain
      reasonable.
- [x] Document the replication method:
  - no synthetic schema changes
  - controlled full-dataset repetition
  - deterministic sampled remainder
  - same prepared schema as the canonical input
- [x] Include at least `14m` in the local benchmark matrix if feasible.
- [x] Use `28m` only as optional stretch evidence.

**Acceptance criteria:**

- `14m` is generated, validated, and documented.
- The final report explains why replicated larger inputs are valid for
  scalability testing.

### M4 - AWS EMR Experiment Lane

**Goal:** add real cluster execution evidence with Amazon EMR.

**Status:** complete. The canonical full-matrix EMR benchmark is
`m4-emr-final-2`; the hardened instrumentation proof run is
`m4-hardened-smoke-3`.

- [x] Add an AWS benchmark environment named `aws-emr`.
- [x] Use this S3 layout:
  - `s3://<bucket>/flight-delay/data/`
  - `s3://<bucket>/flight-delay/code/`
  - `s3://<bucket>/flight-delay/results/`
  - `s3://<bucket>/flight-delay/logs/`
- [x] Upload prepared Parquet inputs to S3.
- [x] Upload generated inputs to S3.
- [x] Upload the source bundle and config files to S3.
- [x] Run Spark SQL on EMR with Spark steps / `spark-submit`.
- [x] Run Spark Core on EMR with Spark steps / `spark-submit`.
- [x] Keep Hive local/containerized unless EMR Hive is explicitly added later.
- [x] Target max-grade EMR input matrix:
  - [x] `100k`
  - [x] `500k`
  - [x] `1m`
  - [x] `3m`
  - [x] `full`
  - [x] `14m`
- [x] Target EMR repetition policy:
  - [x] 3 repetitions for `100k`
  - [x] 3 repetitions for `1m`
  - [x] 3 repetitions for `full`
  - [x] 1 to 3 repetitions for `14m`, depending on budget
- [x] Add audit and safety hardening:
  - [x] run manifest with canonical-run marker
  - [x] step-level EMR timing evidence
  - [x] expanded cost log
  - [x] pinned EMR dependency install
  - [x] cluster startup, step, and total-run timeouts
  - [x] EMR idle auto-termination policy
  - [x] tagged-cluster cleanup discovery
  - [x] S3 input-prefix validation before cluster creation

Result: real EMR run `m4-emr-final-2` completed successfully on cluster
`j-VS6OEAAXUMGP` in `us-east-1` using the baseline 1 primary + 2 core node
profile. The run produced 48 successful Spark SQL/Core benchmark rows covering
`100k`, `500k`, `1m`, `3m`, `full`, and `14m`; S3 outputs and logs were fetched
under `experiments/results/aws-emr/downloaded/m4-emr-final-2/`.

Hardening result: `m4-hardened-smoke-3` completed a low-cost instrumented
`100k` Spark SQL/Core smoke run on EMR cluster `j-3P841S0DMZQP1`. It proves the
new run manifest, step timing CSV, expanded cost log, S3 result fetch, and
tagged-cluster cleanup path while keeping `m4-emr-final-2` as the canonical
full-matrix evidence. Earlier failed hardening attempts remain manifest-labeled
as failed dependency-pin attempts.

Report artifacts now include `report/tables/aws_run_manifest.*`,
`report/tables/aws_step_timing.*`, `report/tables/aws_cost_log.*`, AWS EMR
execution-time figures, and downloaded AWS first-10 sample tables.

**Acceptance criteria:**

- EMR benchmark results are stored separately from local and Docker results.
      Result: `experiments/results/aws-emr/benchmark_m4-emr-final-2.csv`.
- The report can honestly claim real cluster execution.
      Result: real cluster `j-VS6OEAAXUMGP` ran from
      `2026-05-21T22:51:56Z` to `2026-05-21T23:40:53Z`.
- EMR outputs and timing evidence are reproducible from documented commands.
      Result: `make aws-upload`, `make benchmark-aws-emr`, and
      `make aws-fetch-results` document the run path.
      Spark job `duration_seconds` records internal application timing, while
      `step_timing_<run_id>.csv` records EMR queue/start/end wall-clock timing.

### M5 - Cluster Size Variation

**Goal:** add limited but real cluster-size scalability evidence.

- [x] Run the baseline EMR profile:
  - [x] 1 primary node
  - [x] 2 core nodes
      Result: baseline evidence is the completed `m4-emr-final-2` run on
      cluster `j-VS6OEAAXUMGP`.
- [x] If budget allows, run a larger EMR profile:
  - [x] 1 primary node
  - [x] 3 or 4 core nodes
      Result: `m5-emr-3core-1m-full` completed on cluster `j-LTX1FIHYB4X9`
      using `config/aws_emr_m5_larger.yaml` with 1 primary + 3 core nodes.
- [x] Use the same input subset for cluster-size comparison:
  - [x] `1m`
  - [x] `full`
  - [ ] `14m`, if budget allows
      Result: `14m` remains in the baseline EMR evidence, but the larger
      profile intentionally used `1m` and `full` only to control Learner Lab
      cost.
- [x] Add a comparison table:
  - [x] local
  - [x] Docker standalone simulation
  - [x] EMR baseline cluster
  - [x] EMR larger cluster
      Result: `report/tables/cluster_size_comparison.*` is generated. Missing
      Docker `full` cells are shown as `N/A` with notes.

**Acceptance criteria:**

- The report includes at least one real EMR cluster configuration.
- If budget allows, the report includes limited cluster-size variation.
- Any missing larger-cluster run is explained as a budget or Learner Lab
  limitation.

### M6 - Tooling And Interfaces To Add

**Goal:** make the AWS experiment reproducible instead of manual-only.

- [x] Add Make targets:
  - [x] `make aws-upload`
  - [x] `make benchmark-aws-emr`
  - [x] `make aws-fetch-results`
  - [x] `make aws-cleanup`
- [x] Add an AWS config file for:
  - [x] S3 bucket and prefix
  - [x] AWS region
  - [x] EMR release label
  - [x] cluster profile
  - [x] benchmark matrix
  - [x] repetition policy
- [x] Add an AWS helper script with:
  - [x] dry-run mode
  - [x] S3 upload support
  - [x] EMR cluster creation
  - [x] Spark step submission
  - [x] step polling
  - [x] result download
  - [x] forced cluster termination
  - [x] smoke-only execution
  - [x] run manifest generation
  - [x] step timing CSV generation
  - [x] cost log generation
  - [x] tagged-cluster cleanup discovery
- [x] Extend chart/table generation to include `aws-emr`.
- [x] Add tests for:
  - [x] AWS command construction
  - [x] benchmark repetition aggregation
  - [x] chart environment handling
  - [x] config parsing
  - [x] pinned dependency command construction
  - [x] S3 input validation
  - [x] missing metrics failure behavior
  - [x] run manifest fields and hash generation
  - [x] tagged cleanup selection
  - [x] AWS audit table generation
- [x] Confirm `.gitignore` excludes:
  - [x] AWS credentials
  - [x] raw data
  - [x] generated Parquet datasets
  - [x] bulky EMR logs
  - [x] downloaded AWS runtime artifacts

**Acceptance criteria:**

- AWS tooling can be dry-run tested before spending budget.
      Result: `make aws-upload AWS_DRY_RUN=1` and
      `make benchmark-aws-emr AWS_DRY_RUN=1` both construct the expected
      commands without creating AWS resources.
- EMR clusters are always terminated by the helper workflow.
      Result: the benchmark helper terminates the tracked cluster in a
      `finally` block and exposes `make aws-cleanup` as a manual safety valve.
- AWS results can be merged into the existing report artifact pipeline.
      Result: chart/table discovery includes `experiments/results/aws-emr`.

### M7 - Final Report Upgrade

**Goal:** convert the new work into evaluator-facing evidence.

- [x] Add a new report section: "AWS EMR Cluster Experiment."
- [x] Include:
  - [x] region
  - [x] EMR release
  - [x] Spark version
  - [x] instance types
  - [x] node counts
  - [x] S3 layout
  - [x] cluster lifetime
  - [x] budget controls
      Result: `report/draft_final_report.md` now summarizes the baseline
      `m4-emr-final-2` cluster and the larger `m5-emr-3core-1m-full` cluster,
      including `us-east-1`, EMR `emr-7.13.0`, Spark `3.5.6-amzn-2`,
      `m5.xlarge` nodes, S3 prefixes, lifetimes, and termination/time-budget
      controls.
- [x] Add AWS benchmark tables and charts.
      Result: the report references `aws_run_manifest`, `aws_step_timing`,
      `aws_cost_log`, `benchmark_summary`, and `cluster_size_comparison`, and
      embeds the AWS EMR baseline and larger-cluster charts.
- [x] Add cost-awareness discussion.
      Result: M7 explains Learner Lab budget controls, short-lived clusters,
      forced termination, idle timeout, per-step/run timeouts, cost logs, and
      why the larger cluster matrix was intentionally limited.
- [x] Compare local, Docker simulation, and EMR cluster behavior.
      Result: the critical discussion now distinguishes local execution,
      single-host Docker standalone simulation, baseline EMR, and larger EMR
      behavior.
- [x] Update limitations with:
  - [x] Learner Lab restrictions
  - [x] short-lived clusters
  - [x] S3 I/O effects
  - [x] small budget
  - [x] limited repetitions for largest inputs
- [x] Update the conclusion to state that the project includes real cluster
      evidence.

**Acceptance criteria:**

- The final report directly addresses correctness, reproducibility, real
  cluster execution, scalability, cost, and technology comparison.
      Result: the M7 report section, benchmark summary, limitations, and
      conclusion explicitly cover these topics.
- The previous grading weakness is explicitly resolved or honestly bounded.
      Result: the conclusion states that real EMR evidence resolves the prior
      cluster-evidence weakness, while Learner Lab budget and repetition limits
      bound broad scalability claims.

## Suggested Execution Order

1. M1: fix report structure and wording first.
2. M2: add repeated-run benchmark support.
3. M3: generate and validate `14m`.
4. M0: verify AWS lab availability and budget.
5. M6: add dry-run AWS tooling.
6. M4: run EMR smoke test on `100k`.
7. M4/M5: run final EMR benchmark matrix within budget.
8. M7: regenerate charts, tables, and PDF report.

## Test Plan

- [x] Run unit tests:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Result: `106 passed`.

- [x] Run report artifact generation:

```powershell
make charts
make report
```

Result: charts/tables regenerated and `report/draft_final_report.pdf` rebuilt.

M7 result: `make charts` regenerated 8 figures and 108 report tables; the
`make report` target rebuilt `report/draft_final_report.pdf`.

- [x] Run focused M7 regression tests:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_generate_charts.py tests/test_repository_polish.py tests/test_aws_emr_benchmark.py
```

Result: `40 passed`.

- [x] Run AWS tooling in dry-run mode before any real EMR cluster is created.
- [x] Run one EMR smoke benchmark on `100k` before the full AWS matrix.
- [ ] Validate EMR Spark SQL and Spark Core outputs against local Spark SQL
      samples where feasible.
- [x] Confirm every EMR cluster is terminated.
- [x] Confirm no unexpected AWS resources remain after cleanup.

## AWS Cost And Safety Rules

- Never leave EMR clusters idle.
- Prefer short-lived clusters created for a specific benchmark run.
- Always write EMR logs to S3 for post-run debugging.
- Record start and end timestamps for every cluster.
- Check remaining Learner Lab budget after each cluster run.
- Stop after the baseline EMR matrix if estimated remaining budget is too low
  for cluster-size variation.

## Out Of Scope For This Upgrade

- AWS Glue.
- Amazon Athena.
- EMR Hive, unless added explicitly after Spark EMR evidence is complete.
- Production-grade AWS infrastructure-as-code.
- Long-running clusters or interactive notebooks.

## Assumptions

- AWS Academy Learner Lab allows EMR, S3, IAM roles, and at least one
  EMR-supported EC2 instance type.
- EMR is grade-critical; Glue and Athena are optional future work.
- `14m` is the target large replicated dataset.
- `28m` is optional stretch evidence.
- Docker standalone simulation remains useful, but EMR becomes the main cluster
  result.

## Official AWS References

- [Amazon EMR pricing](https://aws.amazon.com/emr/pricing/)
- [Add a Spark step on Amazon EMR](https://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-spark-submit-step.html)
- [Create an EMR cluster with Apache Spark](https://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-spark-launch.html)
