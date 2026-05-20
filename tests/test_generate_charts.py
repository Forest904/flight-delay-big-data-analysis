import csv
from datetime import datetime, timezone
from pathlib import Path

from scripts import generate_charts


BENCHMARK_COLUMNS = [
    "run_id",
    "technology",
    "job_name",
    "input_label",
    "records",
    "environment",
    "cluster_size",
    "duration_seconds",
    "output_rows",
    "status",
    "timestamp_utc",
    "input_path",
    "metrics_path",
    "error",
    "stage",
]


def write_benchmark_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=BENCHMARK_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def benchmark_row(
    *,
    run_id: str,
    timestamp_utc: str,
    duration_seconds: float,
    status: str = "success",
    technology: str = "spark_sql",
    job_name: str = "delay_by_airport_month",
    input_label: str = "100k",
    records: int = 100000,
    environment: str = "local",
) -> dict[str, object]:
    return {
        "run_id": run_id,
        "technology": technology,
        "job_name": job_name,
        "input_label": input_label,
        "records": records,
        "environment": environment,
        "cluster_size": environment,
        "duration_seconds": duration_seconds,
        "output_rows": 12,
        "status": status,
        "timestamp_utc": timestamp_utc,
        "input_path": f"data/generated/flights_{input_label}.parquet",
        "metrics_path": f"outputs/{technology}/runtime_metrics.json",
        "error": "",
        "stage": "complete",
    }


def test_discover_benchmark_csvs_ignores_latest_copy(tmp_path):
    results_dir = tmp_path / "results"
    timestamped = results_dir / "benchmark_20260520T120000123456Z.csv"
    latest = results_dir / "benchmark_latest.csv"
    unrelated = results_dir / "benchmark_notes.csv"
    write_benchmark_csv(timestamped, [])
    write_benchmark_csv(latest, [])
    unrelated.write_text("not a benchmark\n", encoding="utf-8")

    discovered = generate_charts.discover_benchmark_csvs([results_dir])

    assert discovered == [timestamped]


def test_latest_successful_rows_keeps_newest_success_and_excludes_failed(tmp_path):
    older = tmp_path / "benchmark_20260520T120000000000Z.csv"
    newer = tmp_path / "benchmark_20260520T130000000000Z.csv"
    failed = tmp_path / "benchmark_20260520T140000000000Z.csv"
    write_benchmark_csv(
        older,
        [
            benchmark_row(
                run_id="older",
                timestamp_utc="2026-05-20T12:00:00+00:00",
                duration_seconds=8.5,
            )
        ],
    )
    write_benchmark_csv(
        newer,
        [
            benchmark_row(
                run_id="newer",
                timestamp_utc="2026-05-20T13:00:00+00:00",
                duration_seconds=7.5,
            )
        ],
    )
    write_benchmark_csv(
        failed,
        [
            benchmark_row(
                run_id="failed",
                timestamp_utc="2026-05-20T14:00:00+00:00",
                duration_seconds=1.0,
                status="failed",
            )
        ],
    )

    rows = generate_charts.read_successful_benchmark_rows([older, newer, failed])
    latest = generate_charts.latest_successful_rows(rows)

    assert len(latest) == 1
    assert latest[0]["run_id"] == "newer"
    assert latest[0]["duration_seconds"] == "7.5"


def test_benchmark_pivot_contains_available_technology_duration_columns():
    rows = [
        benchmark_row(
            run_id="run",
            timestamp_utc=datetime(2026, 5, 20, tzinfo=timezone.utc).isoformat(),
            duration_seconds=8.5,
            technology="spark_sql",
        ),
        benchmark_row(
            run_id="run",
            timestamp_utc=datetime(2026, 5, 20, tzinfo=timezone.utc).isoformat(),
            duration_seconds=2.25,
            technology="spark_core",
        ),
    ]
    for row in rows:
        row["_timestamp"] = generate_charts.parse_timestamp(row["timestamp_utc"])

    summary = generate_charts.benchmark_summary_records(rows)
    pivot = generate_charts.benchmark_pivot_records(summary)

    assert len(pivot) == 1
    assert pivot[0]["Spark SQL duration_seconds"] == 8.5
    assert pivot[0]["Spark Core duration_seconds"] == 2.25


def test_first_10_csv_inputs_are_written_as_report_tables(tmp_path):
    outputs_dir = tmp_path / "outputs"
    sample_path = outputs_dir / "spark_sql" / "delay_by_airport_month" / "first_10.csv"
    sample_path.parent.mkdir(parents=True)
    outputs_dir.joinpath("spark_core").mkdir()
    outputs_dir.joinpath("hive").mkdir()
    sample_path.write_text("origin_airport,month,flight_count\nABE,1,42\nABQ,2,10\n", encoding="utf-8")
    tables_dir = tmp_path / "report" / "tables"

    tables, warnings = generate_charts.copy_first_10_tables(outputs_dir, tables_dir)

    assert warnings == []
    assert tables_dir.joinpath("first_10_spark_sql_delay_by_airport_month.csv").read_text(
        encoding="utf-8"
    ).startswith("origin_airport,month,flight_count")
    assert "| origin_airport | month | flight_count |" in tables_dir.joinpath(
        "first_10_spark_sql_delay_by_airport_month.md"
    ).read_text(encoding="utf-8")
    assert len(tables) == 2
