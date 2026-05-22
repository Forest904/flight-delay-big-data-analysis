import csv
from pathlib import Path

from scripts import submission_check


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def required_benchmark_rows(*, runs: int = 3) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for environment, inputs in (
        ("local", submission_check.LOCAL_INPUTS),
        ("docker-simulation", submission_check.DOCKER_INPUTS),
    ):
        for input_label in inputs:
            for job_name in submission_check.JOBS:
                for technology in submission_check.CORE_TECHNOLOGIES:
                    rows.append(
                        {
                            "environment": environment,
                            "input_label": input_label,
                            "records": 100000,
                            "job_name": job_name,
                            "technology": technology,
                            "runs": runs,
                            "median_duration_seconds": 1.0,
                            "mean_duration_seconds": 1.0,
                            "min_duration_seconds": 1.0,
                            "max_duration_seconds": 1.0,
                            "stddev_duration_seconds": "",
                            "output_rows": 12,
                            "run_id": "run",
                            "timestamp_utc": "2026-05-22T00:00:00+00:00",
                        }
                    )
    return rows


def write_notes(path: Path, rows: list[dict[str, object]]) -> None:
    write_csv(path, list(submission_check.NOTE_COLUMNS), rows)


def test_audit_benchmark_summary_accepts_required_cells_and_wildcard_notes(tmp_path):
    tables_dir = tmp_path / "report" / "tables"
    summary_rows = required_benchmark_rows(runs=3)
    summary_rows[0]["runs"] = 1
    summary_rows[0]["run_id"] = "smoke-run"
    write_csv(tables_dir / "benchmark_summary.csv", list(summary_rows[0]), summary_rows)
    write_notes(
        tables_dir / "benchmark_notes.csv",
        [
            {
                "environment": "local",
                "input_label": "*",
                "job_name": "*",
                "technology": "Spark SQL",
                "run_id": "smoke-run",
                "classification": "smoke",
                "note": "explicit smoke evidence",
            }
        ],
    )

    assert submission_check.audit_benchmark_summary(tables_dir) == []


def test_audit_benchmark_summary_fails_missing_required_cell(tmp_path):
    tables_dir = tmp_path / "report" / "tables"
    summary_rows = required_benchmark_rows(runs=3)[1:]
    write_csv(tables_dir / "benchmark_summary.csv", list(summary_rows[0]), summary_rows)
    write_notes(tables_dir / "benchmark_notes.csv", [])

    failures = submission_check.audit_benchmark_summary(tables_dir)

    assert any("Missing benchmark summary cell" in failure for failure in failures)


def test_audit_benchmark_summary_fails_unnoted_single_run(tmp_path):
    tables_dir = tmp_path / "report" / "tables"
    summary_rows = required_benchmark_rows(runs=1)
    write_csv(tables_dir / "benchmark_summary.csv", list(summary_rows[0]), summary_rows)
    write_notes(tables_dir / "benchmark_notes.csv", [])

    failures = submission_check.audit_benchmark_summary(tables_dir)

    assert any("runs=1 benchmark row lacks explicit note" in failure for failure in failures)


def test_audit_report_artifacts_requires_tables_figures_and_first_10(tmp_path):
    tables_dir = tmp_path / "report" / "tables"
    figures_dir = tmp_path / "report" / "figures"
    for name in (*submission_check.REQUIRED_TABLES, *submission_check.required_first_10_table_names()):
        path = tables_dir / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("x\n", encoding="utf-8")
    for name in submission_check.REQUIRED_FIGURES:
        path = figures_dir / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("x\n", encoding="utf-8")

    assert submission_check.audit_report_artifacts(tables_dir, figures_dir) == []


def test_audit_tracked_artifacts_blocks_private_and_runtime_files():
    failures = submission_check.audit_tracked_artifacts(
        [
            ".env",
            ".env.example",
            "data/prepared/.gitkeep",
            "data/prepared/flights_2024_clean.parquet",
            "outputs/spark_sql/runtime_metrics.json",
            "experiments/results/local/.gitkeep",
            "experiments/results/local/logs/run/stdout.log",
        ]
    )

    assert any(".env:" in failure for failure in failures)
    assert any("flights_2024_clean.parquet" in failure for failure in failures)
    assert any("runtime_metrics.json" in failure for failure in failures)
    assert any("stdout.log" in failure for failure in failures)
    assert not any(".env.example" in failure for failure in failures)


def test_secret_scan_allows_placeholders_and_flags_realistic_values(tmp_path):
    placeholder = tmp_path / "README.md"
    placeholder.write_text(
        "AWS_SECRET_ACCESS_KEY=...\nAWS_SESSION_TOKEN=...\nKAGGLE_KEY=your_kaggle_api_key\n",
        encoding="utf-8",
    )
    secret = tmp_path / "leak.txt"
    aws_access_key_id = "ASIA" + "1234567890ABCDEF"
    aws_secret_access_key = "abcdefghijklmnopqrstuvwxyz" + "ABCDE1234567890/+="
    kaggle_key = "KGAT" + "abcdefghijklmnop123456"
    secret.write_text(
        f"AWS_ACCESS_KEY_ID={aws_access_key_id}\n"
        f"AWS_SECRET_ACCESS_KEY={aws_secret_access_key}\n"
        f"KAGGLE_KEY={kaggle_key}\n",
        encoding="utf-8",
    )

    assert submission_check.scan_text_for_secrets(placeholder) == []
    findings = submission_check.scan_text_for_secrets(secret)
    assert len(findings) == 3
