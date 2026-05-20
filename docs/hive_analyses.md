# Hive Analyses

This document records the M6 Hive implementation. Hive is the third required
technology and uses the Spark SQL outputs as the correctness reference.

## Command

Run the Hive analyses from the repository root:

```powershell
make run-hive
```

The command executes `src/hive/run_hive.py`. The runner starts the Docker
Compose Hive stack, waits for HiveServer2 to accept Beeline connections, creates
the external table, runs both HiveQL analyses, and writes generated outputs under
`outputs/hive/`.

Docker Desktop must be running before this command starts.

The Hive services remain running after the analyses finish so repeated runs do
not pay the full startup cost. Stop them when needed with:

```powershell
make stop-hive
```

## Docker Stack

The Docker Compose stack contains:

- `hive-postgres`: Postgres metadata database for the Hive metastore.
- `hive-metastore`: standalone Hive metastore using the Postgres database.
- `hiveserver2`: HiveServer2 with Beeline and access to the repository bind
  mount at `/workspace`.

The Hive services use a local project image built from `apache/hive:4.0.1`. The
PostgreSQL JDBC driver is downloaded during the Docker build with a pinned
SHA-256 checksum and installed under `/opt/hive/lib/postgres.jar`.

## External Table

Hive reads the canonical prepared dataset directly as external Parquet:

```text
flight_delay.flights_2024_clean
file:///workspace/data/prepared/flights_2024_clean.parquet
```

The table schema mirrors the canonical prepared schema documented in
`docs/data_preparation.md`.

## Output Layout

```text
outputs/hive/
  delay_by_airport_month/
    full/
      part-00000.csv
    first_10.csv
  airline_airport_ranking/
    full/
      part-00000.csv
    first_10.csv
  runtime_metrics.json
```

The output schemas and job names match Spark SQL and Spark Core:

- `delay_by_airport_month`
- `airline_airport_ranking`

Runtime metrics capture generation timestamp, input path, Hive table metadata,
top-level status, per-job duration, output rows, output paths, and failure
details when a stage fails.

Internally, Hive writes query results through temporary text tables located under
`outputs/hive/.tmp_exports/` with a control-character delimiter. The Python
runner converts those part files into the stable CSV output layout above.

## Validation

After `make run-spark-sql` and `make run-hive`, validate Hive against the Spark
SQL reference:

```powershell
.\.venv\Scripts\python.exe scripts\validate_hive_outputs.py
```

The validator checks metrics status, output columns, row counts, key sets,
numeric values within `1e-6`, exact top-three cause label and count matches,
ranking order, and the presence of first-10 sample files.
