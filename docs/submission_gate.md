# Submission Gate

`make submission-check` is the final guardrail before sharing or submitting the
repository. It prevents the artifact drift that can happen when different
technologies are regenerated from different inputs.

## Command

```powershell
make submission-check
```

The target runs:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
make validate-spark-sql
make validate-spark-core
make validate-hive
make validate-mapreduce
make charts
make report
```

Then it audits report artifacts, benchmark evidence, tracked artifacts, and
credential-like values.

For documentation-only checks, use:

```powershell
.\.venv\Scripts\python.exe scripts\submission_check.py --audit-only
```

## Canonical Input Validation

Report-ready outputs must use:

```text
data/prepared/flights_2024_clean.parquet
```

The validators normalize Windows paths, repository-relative paths, and
`/workspace` container paths before comparing `input_path` values in
`runtime_metrics.json`.

The gate fails if Spark SQL, Spark Core, Hive, or MapReduce runtime metrics point
at another input such as `100k`, `1m`, `14m`, or `28m`.

## Required Report Artifacts

The gate expects:

- Benchmark summary, phase summary, pivot, status, speedup, scalability,
  rows-per-second, and environment summary tables.
- Local first-10 tables for Spark SQL, Spark Core, Hive, and MapReduce for both
  analyses.
- Local and Docker simulation execution-time figures.
- `report/tables/benchmark_notes.csv`.
- A rebuilt `report/draft_final_report.pdf`.

## Single-Run Benchmark Notes

Every `runs=1` row in `report/tables/benchmark_summary.csv` must match a note in
`report/tables/benchmark_notes.csv`.

Allowed classifications:

- `smoke`
- `budget_limited`
- `resource_limited`

This makes one-off evidence visible instead of silently presenting it as equal
to repeated benchmark campaigns.

## Tracked Artifact Hygiene

The gate uses `git ls-files` and fails if tracked files include:

- `.env`
- `derby.log`
- raw data
- prepared data
- generated Parquet data
- runtime outputs under `outputs/`
- benchmark logs or downloaded results under `experiments/results/`
- bulky AWS downloads

Intentional `.gitkeep` placeholders and `.env.example` are allowed.

## Credential Scan

Only tracked files are scanned. The scan is value-sensitive so placeholder
variable names and examples such as `AWS_SECRET_ACCESS_KEY=...` do not fail the
gate, but realistic AWS and Kaggle credential values do.

Before sharing the repository, screenshots, logs, or videos, rotate any Kaggle
or AWS Learner Lab credentials that appeared in local `.env`, terminals, logs,
or screen recordings.
