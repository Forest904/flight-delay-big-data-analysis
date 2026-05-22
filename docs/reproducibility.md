# Reproducibility

This document records the canonical local reproduction path for the as-built
project. The short README links here instead of carrying the full manual.

## Prerequisites

- Python 3.12 through the project virtual environment.
- Java 17 for Spark.
- Docker Desktop for Windows Spark Core, Hive, MapReduce, and Docker simulation.
- Pandoc plus a PDF engine such as `xelatex` for report generation.
- The Kaggle CSV placed at `data/raw/flight_data_2024.csv`.

The raw dataset is not tracked in Git. Local credentials belong in `.env`, which
is ignored.

## Setup

```powershell
make setup
make check-env
```

On Windows, the project uses:

```powershell
.\.venv\Scripts\python.exe
```

On Linux, WSL, or macOS, use:

```bash
.venv/bin/python
```

## Canonical Local Run Order

Run this sequence from the repository root after placing the raw Kaggle CSV:

```powershell
make inspect-raw
make prepare
make generate-sizes
make run-all-local
make run-mapreduce
make charts
make report
make submission-check
```

`make run-all-local` runs Spark SQL, Spark Core, and Hive, then validates those
three required lanes. `make run-mapreduce` is separate because MapReduce is
stretch evidence and takes longer.

## Canonical Validation Input

Report-ready local outputs must use:

```text
data/prepared/flights_2024_clean.parquet
```

The validators fail if Spark SQL, Spark Core, Hive, or MapReduce runtime metrics
point at a different input for report-ready outputs.

## Common Targets

| Target | Purpose |
|---|---|
| `make prepare` | Build the cleaned canonical Parquet dataset |
| `make generate-sizes` | Generate validated benchmark inputs and manifest |
| `make run-all-local` | Run and validate Spark SQL, Spark Core, and Hive |
| `make run-mapreduce` | Run stretch MapReduce outputs |
| `make benchmark-local` | Run local Spark SQL/Core/Hive benchmark matrix |
| `make benchmark-docker-simulation` | Run Docker standalone simulation matrix |
| `make charts` | Regenerate report tables and figures |
| `make report` | Rebuild `report/draft_final_report.pdf` |
| `make submission-check` | Run final submission gate |
| `make clean` | Remove generated runtime artifacts while preserving evidence |

## Verification

Use the full test suite before committing code or documentation changes:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Use the audit-only path when checking documentation or tracked-file hygiene
without rebuilding the PDF:

```powershell
.\.venv\Scripts\python.exe scripts\submission_check.py --audit-only
```
