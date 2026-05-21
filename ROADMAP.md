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
- [ ] Create or select the project S3 bucket for later EMR logs/results.
      Current status: `AWS_FLIGHT_DELAY_BUCKET` is not set yet.

**Acceptance criteria:**

- AWS service availability is known.
- A safe default cluster profile is selected.
- A cleanup rule exists before the first EMR run.
- Remaining setup before first EMR run: create/select the project S3 bucket and
  set `AWS_FLIGHT_DELAY_BUCKET`.

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

- [ ] Add an AWS benchmark environment named `aws-emr`.
- [ ] Use this S3 layout:
  - `s3://<bucket>/flight-delay/data/`
  - `s3://<bucket>/flight-delay/code/`
  - `s3://<bucket>/flight-delay/results/`
  - `s3://<bucket>/flight-delay/logs/`
- [ ] Upload prepared Parquet inputs to S3.
- [ ] Upload generated inputs to S3.
- [ ] Upload the source bundle and config files to S3.
- [ ] Run Spark SQL on EMR with Spark steps / `spark-submit`.
- [ ] Run Spark Core on EMR with Spark steps / `spark-submit`.
- [ ] Keep Hive local/containerized unless EMR Hive is explicitly added later.
- [ ] Target max-grade EMR input matrix:
  - [ ] `100k`
  - [ ] `500k`
  - [ ] `1m`
  - [ ] `3m`
  - [ ] `full`
  - [ ] `14m`
- [ ] Target EMR repetition policy:
  - [ ] 3 repetitions for `100k`
  - [ ] 3 repetitions for `1m`
  - [ ] 3 repetitions for `full`
  - [ ] 1 to 3 repetitions for `14m`, depending on budget

**Acceptance criteria:**

- EMR benchmark results are stored separately from local and Docker results.
- The report can honestly claim real cluster execution.
- EMR outputs and timing evidence are reproducible from documented commands.

### M5 - Cluster Size Variation

**Goal:** add limited but real cluster-size scalability evidence.

- [ ] Run the baseline EMR profile:
  - [ ] 1 primary node
  - [ ] 2 core nodes
- [ ] If budget allows, run a larger EMR profile:
  - [ ] 1 primary node
  - [ ] 3 or 4 core nodes
- [ ] Use the same input subset for cluster-size comparison:
  - [ ] `1m`
  - [ ] `full`
  - [ ] `14m`, if budget allows
- [ ] Add a comparison table:
  - local
  - Docker standalone simulation
  - EMR baseline cluster
  - EMR larger cluster

**Acceptance criteria:**

- The report includes at least one real EMR cluster configuration.
- If budget allows, the report includes limited cluster-size variation.
- Any missing larger-cluster run is explained as a budget or Learner Lab
  limitation.

### M6 - Tooling And Interfaces To Add

**Goal:** make the AWS experiment reproducible instead of manual-only.

- [ ] Add Make targets:
  - [ ] `make aws-upload`
  - [ ] `make benchmark-aws-emr`
  - [ ] `make aws-fetch-results`
  - [ ] `make aws-cleanup`
- [ ] Add an AWS config file for:
  - [ ] S3 bucket and prefix
  - [ ] AWS region
  - [ ] EMR release label
  - [ ] cluster profile
  - [ ] benchmark matrix
  - [ ] repetition policy
- [ ] Add an AWS helper script with:
  - [ ] dry-run mode
  - [ ] S3 upload support
  - [ ] EMR cluster creation
  - [ ] Spark step submission
  - [ ] step polling
  - [ ] result download
  - [ ] forced cluster termination
- [ ] Extend chart/table generation to include `aws-emr`.
- [ ] Add tests for:
  - [ ] AWS command construction
  - [ ] benchmark repetition aggregation
  - [ ] chart environment handling
  - [ ] config parsing
- [ ] Confirm `.gitignore` excludes:
  - [ ] AWS credentials
  - [ ] raw data
  - [ ] generated Parquet datasets
  - [ ] bulky EMR logs
  - [ ] downloaded AWS runtime artifacts

**Acceptance criteria:**

- AWS tooling can be dry-run tested before spending budget.
- EMR clusters are always terminated by the helper workflow.
- AWS results can be merged into the existing report artifact pipeline.

### M7 - Final Report Upgrade

**Goal:** convert the new work into evaluator-facing evidence.

- [ ] Add a new report section: "AWS EMR Cluster Experiment."
- [ ] Include:
  - [ ] region
  - [ ] EMR release
  - [ ] Spark version
  - [ ] instance types
  - [ ] node counts
  - [ ] S3 layout
  - [ ] cluster lifetime
  - [ ] budget controls
- [ ] Add AWS benchmark tables and charts.
- [ ] Add cost-awareness discussion.
- [ ] Compare local, Docker simulation, and EMR cluster behavior.
- [ ] Update limitations with:
  - [ ] Learner Lab restrictions
  - [ ] short-lived clusters
  - [ ] S3 I/O effects
  - [ ] small budget
  - [ ] limited repetitions for largest inputs
- [ ] Update the conclusion to state that the project includes real cluster
      evidence.

**Acceptance criteria:**

- The final report directly addresses correctness, reproducibility, real
  cluster execution, scalability, cost, and technology comparison.
- The previous grading weakness is explicitly resolved or honestly bounded.

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

- [ ] Run unit tests:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

- [ ] Run report artifact generation:

```powershell
make charts
make report
```

- [ ] Run AWS tooling in dry-run mode before any real EMR cluster is created.
- [ ] Run one EMR smoke benchmark on `100k` before the full AWS matrix.
- [ ] Validate EMR Spark SQL and Spark Core outputs against local Spark SQL
      samples where feasible.
- [ ] Confirm every EMR cluster is terminated.
- [ ] Confirm no unexpected AWS resources remain after cleanup.

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
