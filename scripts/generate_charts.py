"""Generate report-ready benchmark charts and tables."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.run_benchmarks import BENCHMARK_COLUMNS
DEFAULT_RESULTS_DIRS = (
    PROJECT_ROOT / "experiments" / "results" / "local",
    PROJECT_ROOT / "experiments" / "results" / "docker-simulation",
    PROJECT_ROOT / "experiments" / "results" / "aws-emr",
    PROJECT_ROOT / "experiments" / "results" / "aws-emr-larger",
)
DEFAULT_OUTPUTS_DIR = PROJECT_ROOT / "outputs"
DEFAULT_FIGURES_DIR = PROJECT_ROOT / "report" / "figures"
DEFAULT_TABLES_DIR = PROJECT_ROOT / "report" / "tables"
TECHNOLOGY_LABELS = {
    "spark_sql": "Spark SQL",
    "spark_core": "Spark Core",
    "hive": "Hive",
    "mapreduce": "MapReduce",
}
TECHNOLOGY_ORDER = tuple(TECHNOLOGY_LABELS)
CORE_TECHNOLOGY_ORDER = ("spark_sql", "spark_core", "hive")
OPTIONAL_OUTPUT_TECHNOLOGIES = {"mapreduce"}
JOB_LABELS = {
    "delay_by_airport_month": "Delay by airport, month, and delay range",
    "airline_airport_ranking": "Airline-airport delay ranking",
}
ENVIRONMENT_LABELS = {
    "local": "Local",
    "docker-simulation": "Docker standalone simulation",
    "aws-emr": "AWS EMR",
    "aws-emr-larger": "AWS EMR larger cluster",
}
BENCHMARK_FILE_RE = re.compile(r"^benchmark_(?!latest\.csv$)(?!notes\.csv$)[A-Za-z0-9][A-Za-z0-9_.-]*\.csv$")
EXPECTED_INPUTS_BY_ENVIRONMENT = {
    "local": (
        ("100k", 100_000),
        ("500k", 500_000),
        ("1m", 1_000_000),
        ("3m", 3_000_000),
        ("full", 7_079_081),
    ),
    "docker-simulation": (
        ("100k", 100_000),
        ("500k", 500_000),
        ("1m", 1_000_000),
        ("3m", 3_000_000),
        ("full", 7_079_081),
        ("14m", 14_000_000),
        ("28m", 28_000_000),
    ),
    "aws-emr": (
        ("100k", 100_000),
        ("500k", 500_000),
        ("1m", 1_000_000),
        ("3m", 3_000_000),
        ("full", 7_079_081),
        ("14m", 14_000_000),
    ),
    "aws-emr-larger": (
        ("1m", 1_000_000),
        ("full", 7_079_081),
    ),
}
EXPECTED_TECHNOLOGIES_BY_ENVIRONMENT = {
    "aws-emr": ("spark_sql", "spark_core"),
    "aws-emr-larger": ("spark_sql", "spark_core"),
}
CLUSTER_COMPARISON_INPUTS = (
    ("1m", 1_000_000),
    ("full", 7_079_081),
)
CLUSTER_COMPARISON_TECHNOLOGIES = ("Spark SQL", "Spark Core")
AWS_AUDIT_MANIFEST_COLUMNS = [
    "run_id",
    "run_kind",
    "status",
    "is_canonical_full_run",
    "canonical_run_id",
    "git_commit",
    "git_dirty",
    "bucket",
    "region",
    "emr_release",
    "cluster_id",
    "instance_type",
    "node_count",
    "source_bundle_sha256",
    "runtime_config_sha256",
    "config_sha256",
    "dependencies",
]
@dataclass(frozen=True)
class GeneratedArtifacts:
    figures: list[Path]
    tables: list[Path]
    warnings: list[str]


def resolve_project_path(path: Path | str) -> Path:
    value = Path(path)
    if not value.is_absolute():
        return PROJECT_ROOT / value
    return value


def display_path(path: Path) -> str:
    try:
        return path.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def canonical_environment(value: object) -> str:
    return str(value or "")


def discover_benchmark_csvs(results_dirs: Iterable[Path]) -> list[Path]:
    csvs: list[Path] = []
    for results_dir in results_dirs:
        if not results_dir.exists():
            continue
        csvs.extend(
            path
            for path in results_dir.glob("benchmark_*.csv")
            if BENCHMARK_FILE_RE.fullmatch(path.name)
            and benchmark_csv_schema_errors(path) == []
        )
    return sorted(csvs)


def benchmark_csv_schema_errors(path: Path) -> list[str]:
    try:
        with path.open(newline="", encoding="utf-8-sig") as file:
            fieldnames = csv.DictReader(file).fieldnames or []
    except OSError as exc:
        return [str(exc)]
    required = [column for column in BENCHMARK_COLUMNS if column != "repetition"]
    missing = [column for column in required if column not in fieldnames]
    unknown = [column for column in fieldnames if column not in BENCHMARK_COLUMNS]
    errors: list[str] = []
    if missing:
        errors.append(f"missing columns: {', '.join(missing)}")
    if unknown:
        errors.append(f"unexpected columns: {', '.join(unknown)}")
    return errors


def parse_timestamp(value: object) -> datetime:
    text = str(value or "").strip()
    if not text:
        return datetime.min.replace(tzinfo=timezone.utc)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return datetime.min.replace(tzinfo=timezone.utc)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def read_benchmark_rows(csv_paths: Iterable[Path]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for csv_path in csv_paths:
        errors = benchmark_csv_schema_errors(csv_path)
        if errors:
            continue
        with csv_path.open(newline="", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if not row.get("repetition"):
                    row["repetition"] = "1"
                row["environment"] = canonical_environment(row.get("environment", ""))
                row["_source_file"] = csv_path.name
                row["_timestamp"] = parse_timestamp(row.get("timestamp_utc"))
                rows.append(row)
    return rows


def read_successful_benchmark_rows(csv_paths: Iterable[Path]) -> list[dict[str, object]]:
    return [
        row
        for row in read_benchmark_rows(csv_paths)
        if str(row.get("status", "")).lower() == "success"
    ]


def latest_successful_rows(rows: Iterable[dict[str, object]]) -> list[dict[str, object]]:
    latest_timestamp_by_key: dict[tuple[str, str, str, str], datetime] = {}
    for row in rows:
        key = (
            str(row.get("environment", "")),
            str(row.get("input_label", "")),
            str(row.get("job_name", "")),
            str(row.get("technology", "")),
        )
        current = latest_timestamp_by_key.get(key)
        timestamp = row["_timestamp"]
        if current is None or timestamp > current:
            latest_timestamp_by_key[key] = timestamp
    latest_rows = [
        row
        for row in rows
        if latest_timestamp_by_key.get(
            (
                str(row.get("environment", "")),
                str(row.get("input_label", "")),
                str(row.get("job_name", "")),
                str(row.get("technology", "")),
            )
        )
        == row["_timestamp"]
    ]
    return sorted(
        latest_rows,
        key=lambda row: (
            str(row.get("environment", "")),
            int(float(row.get("records") or 0)),
            str(row.get("input_label", "")),
            str(row.get("job_name", "")),
            TECHNOLOGY_ORDER.index(str(row.get("technology")))
            if str(row.get("technology")) in TECHNOLOGY_ORDER
            else len(TECHNOLOGY_ORDER),
            int(float(row.get("repetition") or 1)),
        ),
    )


def latest_benchmark_rows(rows: Iterable[dict[str, object]]) -> list[dict[str, object]]:
    latest_by_key: dict[tuple[str, str, str, str], dict[str, object]] = {}
    for row in rows:
        key = (
            str(row.get("environment", "")),
            str(row.get("input_label", "")),
            str(row.get("job_name", "")),
            str(row.get("technology", "")),
        )
        current = latest_by_key.get(key)
        if current is None or (
            row["_timestamp"],
            int(float(row.get("repetition") or 1)),
        ) > (
            current["_timestamp"],
            int(float(current.get("repetition") or 1)),
        ):
            latest_by_key[key] = row
    return sorted(
        latest_by_key.values(),
        key=lambda row: (
            str(row.get("environment", "")),
            int(float(row.get("records") or 0)),
            str(row.get("input_label", "")),
            str(row.get("job_name", "")),
            TECHNOLOGY_ORDER.index(str(row.get("technology")))
            if str(row.get("technology")) in TECHNOLOGY_ORDER
            else len(TECHNOLOGY_ORDER),
        ),
    )


def formatted_number(value: object, digits: int = 3) -> str:
    if value is None or value == "":
        return ""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if number.is_integer():
        return str(int(number))
    return f"{number:.{digits}f}".rstrip("0").rstrip(".")


def positive_float(value: object) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if number <= 0:
        return None
    return number


def divide_or_blank(numerator: object, denominator: object) -> float | str:
    numerator_value = positive_float(numerator)
    denominator_value = positive_float(denominator)
    if numerator_value is None or denominator_value is None:
        return ""
    return numerator_value / denominator_value


def benchmark_summary_records(rows: Iterable[dict[str, object]]) -> list[dict[str, object]]:
    normalized_rows: list[dict[str, object]] = []
    for row in rows:
        duration = positive_float(row.get("duration_seconds"))
        if duration is None:
            continue
        normalized_rows.append(
            {
                "environment": row.get("environment", ""),
                "input_label": row.get("input_label", ""),
                "records": int(float(row.get("records") or 0)),
                "job_name": row.get("job_name", ""),
                "technology": str(row.get("technology", "")),
                "duration_seconds": duration,
                "output_rows": int(float(row.get("output_rows") or 0)),
                "run_id": row.get("run_id", ""),
                "timestamp_utc": row.get("timestamp_utc", ""),
            }
        )
    if not normalized_rows:
        return []

    frame = pd.DataFrame(normalized_rows)
    records: list[dict[str, object]] = []
    group_columns = ["environment", "input_label", "records", "job_name", "technology"]
    for key, group in frame.groupby(group_columns, sort=True):
        environment, input_label, records_value, job_name, technology = key
        durations = group["duration_seconds"]
        stddev = durations.std(ddof=1) if len(durations) > 1 else None
        records.append(
            {
                "environment": environment,
                "input_label": input_label,
                "records": int(records_value),
                "job_name": job_name,
                "technology": TECHNOLOGY_LABELS.get(str(technology), str(technology)),
                "runs": int(len(durations)),
                "median_duration_seconds": float(durations.median()),
                "mean_duration_seconds": float(durations.mean()),
                "min_duration_seconds": float(durations.min()),
                "max_duration_seconds": float(durations.max()),
                "stddev_duration_seconds": "" if stddev is None or pd.isna(stddev) else float(stddev),
                "output_rows": int(group["output_rows"].iloc[0]),
                "run_id": group["run_id"].iloc[0],
                "timestamp_utc": group["timestamp_utc"].iloc[0],
            }
        )
    return sorted(
        records,
        key=lambda row: (
            str(row.get("environment", "")),
            int(float(row.get("records") or 0)),
            str(row.get("input_label", "")),
            str(row.get("job_name", "")),
            str(row.get("technology", "")),
        ),
    )


def benchmark_pivot_records(summary: list[dict[str, object]]) -> list[dict[str, object]]:
    if not summary:
        return []

    frame = pd.DataFrame(summary)
    pivot = (
        frame.pivot_table(
            index=["environment", "input_label", "records", "job_name"],
            columns="technology",
            values="median_duration_seconds",
            aggfunc="first",
        )
        .reset_index()
        .sort_values(["environment", "records", "input_label", "job_name"])
    )

    ordered_columns = ["environment", "input_label", "records", "job_name"]
    ordered_columns.extend(label for label in TECHNOLOGY_LABELS.values() if label in pivot.columns)
    ordered_columns.extend(column for column in pivot.columns if column not in ordered_columns)
    pivot = pivot[ordered_columns]
    pivot = pivot.rename(columns={label: f"{label} median_duration_seconds" for label in TECHNOLOGY_LABELS.values()})
    return pivot.where(pd.notna(pivot), "").to_dict(orient="records")


def cluster_size_comparison_records(summary: list[dict[str, object]]) -> list[dict[str, object]]:
    summary_by_key = {
        (
            str(row.get("environment", "")),
            str(row.get("input_label", "")),
            str(row.get("job_name", "")),
            str(row.get("technology", "")),
        ): row
        for row in summary
    }

    def duration(environment: str, input_label: str, job_name: str, technology: str) -> object:
        row = summary_by_key.get((environment, input_label, job_name, technology))
        if row is None:
            return "N/A"
        return row.get("median_duration_seconds", "N/A")

    def run_id(environment: str, input_label: str, job_name: str, technology: str) -> object:
        row = summary_by_key.get((environment, input_label, job_name, technology))
        if row is None:
            return "N/A"
        return row.get("run_id", "N/A") or "N/A"

    records: list[dict[str, object]] = []
    for input_label, records_value in CLUSTER_COMPARISON_INPUTS:
        for job_name in JOB_LABELS:
            for technology in CLUSTER_COMPARISON_TECHNOLOGIES:
                local_duration = duration("local", input_label, job_name, technology)
                docker_duration = duration("docker-simulation", input_label, job_name, technology)
                baseline_duration = duration("aws-emr", input_label, job_name, technology)
                larger_duration = duration("aws-emr-larger", input_label, job_name, technology)
                speedup = divide_or_blank(baseline_duration, larger_duration)
                notes: list[str] = []
                if docker_duration == "N/A" and input_label == "full":
                    notes.append("Docker standalone simulation full input was not run.")
                if larger_duration == "N/A":
                    notes.append("Larger EMR profile not run or not fetched yet.")
                records.append(
                    {
                        "input_label": input_label,
                        "records": records_value,
                        "job_name": job_name,
                        "technology": technology,
                        "local_median_duration_seconds": local_duration,
                        "docker_simulation_median_duration_seconds": docker_duration,
                        "emr_baseline_median_duration_seconds": baseline_duration,
                        "emr_larger_median_duration_seconds": larger_duration,
                        "emr_larger_vs_baseline_speedup": speedup if speedup != "" else "N/A",
                        "local_run_id": run_id("local", input_label, job_name, technology),
                        "docker_simulation_run_id": run_id("docker-simulation", input_label, job_name, technology),
                        "emr_baseline_run_id": run_id("aws-emr", input_label, job_name, technology),
                        "emr_larger_run_id": run_id("aws-emr-larger", input_label, job_name, technology),
                        "notes": " ".join(notes),
                    }
                )
    return records


def rows_per_second_records(summary: list[dict[str, object]]) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for row in summary:
        duration_seconds = positive_float(row.get("median_duration_seconds"))
        rows_per_second = ""
        if duration_seconds is not None:
            rows_per_second = int(float(row.get("records") or 0)) / duration_seconds
        records.append(
            {
                "environment": row.get("environment", ""),
                "input_label": row.get("input_label", ""),
                "records": row.get("records", ""),
                "job_name": row.get("job_name", ""),
                "technology": row.get("technology", ""),
                "median_duration_seconds": row.get("median_duration_seconds", ""),
                "rows_per_second": rows_per_second,
            }
        )
    return records


def speedup_records(pivot: list[dict[str, object]]) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for row in pivot:
        spark_sql = row.get("Spark SQL median_duration_seconds", "")
        spark_core = row.get("Spark Core median_duration_seconds", "")
        hive = row.get("Hive median_duration_seconds", "")
        records.append(
            {
                "environment": row.get("environment", ""),
                "input_label": row.get("input_label", ""),
                "records": row.get("records", ""),
                "job_name": row.get("job_name", ""),
                "spark_sql_div_spark_core": divide_or_blank(spark_sql, spark_core),
                "hive_div_spark_sql": divide_or_blank(hive, spark_sql),
                "hive_div_spark_core": divide_or_blank(hive, spark_core),
            }
        )
    return records


def scalability_ratio_records(summary: list[dict[str, object]]) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    if not summary:
        return records

    frame = pd.DataFrame(summary).sort_values(["environment", "job_name", "technology", "records", "input_label"])
    for (environment, job_name, technology), group in frame.groupby(["environment", "job_name", "technology"], sort=True):
        group = group.drop_duplicates(subset=["input_label"], keep="first")
        if len(group) < 3:
            continue

        baseline_group = group[group["input_label"] == "100k"]
        if baseline_group.empty:
            continue
        baseline = baseline_group.iloc[0]
        baseline_duration = positive_float(baseline.get("median_duration_seconds"))
        baseline_records = positive_float(baseline.get("records"))
        if baseline_duration is None or baseline_records is None:
            continue
        baseline_throughput = baseline_records / baseline_duration

        for _, row in group.iterrows():
            records_value = positive_float(row.get("records"))
            duration_value = positive_float(row.get("median_duration_seconds"))
            throughput = ""
            if records_value is not None and duration_value is not None:
                throughput = records_value / duration_value
            records.append(
                {
                    "environment": environment,
                    "input_label": row.get("input_label", ""),
                    "records": int(row.get("records", 0)),
                    "job_name": job_name,
                    "technology": technology,
                    "median_duration_vs_100k": divide_or_blank(duration_value, baseline_duration),
                    "records_vs_100k": divide_or_blank(records_value, baseline_records),
                    "throughput_vs_100k": divide_or_blank(throughput, baseline_throughput),
                }
            )
    return records


def row_reason(row: dict[str, object]) -> str:
    error = str(row.get("error", "") or "").strip()
    stage = str(row.get("stage", "") or "").strip()
    if error and stage:
        return f"{stage}: {error}"
    if error:
        return error
    if stage:
        return stage
    status = str(row.get("status", "") or "").strip()
    return status


def benchmark_status_record(row: dict[str, object], *, records: int | None = None) -> dict[str, object]:
    technology = str(row.get("technology", ""))
    return {
        "environment": row.get("environment", ""),
        "input_label": row.get("input_label", ""),
        "records": records if records is not None else int(float(row.get("records") or 0)),
        "job_name": row.get("job_name", ""),
        "technology": TECHNOLOGY_LABELS.get(technology, technology),
        "status": row.get("status", ""),
        "duration_seconds": row.get("duration_seconds", ""),
        "output_rows": row.get("output_rows", ""),
        "reason": "" if str(row.get("status", "")).lower() == "success" else row_reason(row),
        "run_id": row.get("run_id", ""),
        "timestamp_utc": row.get("timestamp_utc", ""),
        "source_file": row.get("_source_file", ""),
    }


def benchmark_status_records(rows: Iterable[dict[str, object]]) -> list[dict[str, object]]:
    latest_rows = latest_benchmark_rows(rows)
    latest_by_key = {
        (
            str(row.get("environment", "")),
            str(row.get("input_label", "")),
            str(row.get("job_name", "")),
            str(row.get("technology", "")),
        ): row
        for row in latest_rows
    }
    latest_run_failures = {
        (
            str(row.get("environment", "")),
            str(row.get("input_label", "")),
            str(row.get("technology", "")),
        ): row
        for row in latest_rows
        if str(row.get("job_name", "")) == "__run__"
        and str(row.get("status", "")).lower() != "success"
    }

    expected_keys: set[tuple[str, str, str, str]] = set()
    status_rows: list[dict[str, object]] = []
    for environment, inputs in EXPECTED_INPUTS_BY_ENVIRONMENT.items():
        expected_technologies = EXPECTED_TECHNOLOGIES_BY_ENVIRONMENT.get(environment, CORE_TECHNOLOGY_ORDER)
        for input_label, records in inputs:
            for job_name in JOB_LABELS:
                for technology in expected_technologies:
                    key = (environment, input_label, job_name, technology)
                    expected_keys.add(key)
                    row = latest_by_key.get(key)
                    if row is not None:
                        status_rows.append(benchmark_status_record(row, records=records))
                        continue

                    run_failure = latest_run_failures.get((environment, input_label, technology))
                    if run_failure is not None:
                        failed_row = dict(run_failure)
                        failed_row["job_name"] = job_name
                        status_rows.append(benchmark_status_record(failed_row, records=records))
                        continue

                    status_rows.append(
                        {
                            "environment": environment,
                            "input_label": input_label,
                            "records": records,
                            "job_name": job_name,
                            "technology": TECHNOLOGY_LABELS[technology],
                            "status": "not_run",
                            "duration_seconds": "",
                            "output_rows": "",
                            "reason": "No benchmark row found for this expected cell.",
                            "run_id": "",
                            "timestamp_utc": "",
                            "source_file": "",
                        }
                    )

    extras = [
        row
        for row in latest_rows
        if (
            str(row.get("environment", "")),
            str(row.get("input_label", "")),
            str(row.get("job_name", "")),
            str(row.get("technology", "")),
        )
        not in expected_keys
        and str(row.get("job_name", "")) != "__run__"
    ]
    status_rows.extend(benchmark_status_record(row) for row in extras)
    return sorted(
        status_rows,
        key=lambda row: (
            str(row.get("environment", "")),
            int(float(row.get("records") or 0)),
            str(row.get("input_label", "")),
            str(row.get("job_name", "")),
            str(row.get("technology", "")),
        ),
    )


def write_csv(path: Path, records: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames: list[str] = []
    for record in records:
        for key in record:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", newline="", encoding="utf-8") as file:
        if not fieldnames:
            file.write("")
            return
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def markdown_escape(value: object) -> str:
    text = formatted_number(value) if isinstance(value, float) else str(value)
    return text.replace("|", "\\|").replace("\n", " ")


def write_markdown(path: Path, records: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not records:
        path.write_text("_No data available._\n", encoding="utf-8")
        return

    columns: list[str] = []
    for record in records:
        for key in record:
            if key not in columns:
                columns.append(key)
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for record in records:
        lines.append("| " + " | ".join(markdown_escape(record.get(column, "")) for column in columns) + " |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_table_pair(tables_dir: Path, stem: str, records: list[dict[str, object]]) -> list[Path]:
    csv_path = tables_dir / f"{stem}.csv"
    md_path = tables_dir / f"{stem}.md"
    write_csv(csv_path, records)
    write_markdown(md_path, records)
    return [csv_path, md_path]


def input_tick_label(label: object, records: object) -> str:
    return f"{label}\n({formatted_number(records, digits=0)} rows)"


def execution_time_chart_kind(input_count: int) -> str:
    return "line" if input_count >= 3 else "bar"


def generate_execution_time_charts(rows: list[dict[str, object]], figures_dir: Path) -> list[Path]:
    if not rows:
        return []

    figures_dir.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame(benchmark_summary_records(rows))
    figures: list[Path] = []

    for (environment, job_name), group in frame.groupby(["environment", "job_name"], sort=True):
        group = group.sort_values(["records", "input_label", "technology"])
        input_order = (
            group[["input_label", "records"]]
            .drop_duplicates()
            .sort_values(["records", "input_label"])
            .to_dict(orient="records")
        )
        x_positions = list(range(len(input_order)))
        x_lookup = {item["input_label"]: index for index, item in enumerate(input_order)}
        chart_kind = execution_time_chart_kind(len(input_order))

        plt.figure(figsize=(7.0, 4.2), dpi=140)
        technology_labels = [
            label
            for label in TECHNOLOGY_LABELS.values()
            if not group[group["technology"] == label].empty
        ]
        bar_width = 0.8 / max(len(technology_labels), 1)

        for technology_index, technology_label in enumerate(technology_labels):
            tech_group = group[group["technology"] == technology_label].sort_values(["records", "input_label"])
            if tech_group.empty:
                continue
            positions = [x_lookup[label] for label in tech_group["input_label"]]
            medians = list(tech_group["median_duration_seconds"])
            lower_errors = [
                max(0.0, float(row["median_duration_seconds"]) - float(row["min_duration_seconds"]))
                for _, row in tech_group.iterrows()
            ]
            upper_errors = [
                max(0.0, float(row["max_duration_seconds"]) - float(row["median_duration_seconds"]))
                for _, row in tech_group.iterrows()
            ]
            yerr = [lower_errors, upper_errors]
            if chart_kind == "line":
                plt.errorbar(
                    positions,
                    medians,
                    yerr=yerr,
                    marker="o",
                    linewidth=1.8 if len(tech_group) >= 2 else 0,
                    linestyle="-" if len(tech_group) >= 2 else "",
                    capsize=3,
                    label=technology_label,
                )
            else:
                offset = (technology_index - (len(technology_labels) - 1) / 2) * bar_width
                plt.bar(
                    [position + offset for position in positions],
                    medians,
                    yerr=yerr,
                    capsize=3,
                    width=bar_width,
                    label=technology_label,
                )

        environment_label = ENVIRONMENT_LABELS.get(str(environment), str(environment))
        plt.title(f"{JOB_LABELS.get(str(job_name), job_name)} - {environment_label}")
        plt.xlabel("Input size (record count)")
        plt.ylabel("Median execution time (seconds)")
        plt.xticks(
            x_positions,
            [input_tick_label(item["input_label"], item["records"]) for item in input_order],
        )
        plt.grid(axis="y", alpha=0.25)
        plt.legend(title="Technology")
        plt.tight_layout()

        safe_environment = str(environment).replace(" ", "_")
        safe_job_name = str(job_name).replace(" ", "_")
        figure_path = figures_dir / f"execution_time_{safe_environment}_{safe_job_name}.png"
        plt.savefig(figure_path, bbox_inches="tight")
        plt.close()
        figures.append(figure_path)

    return figures


def read_first_10_records(path: Path) -> list[dict[str, object]]:
    frame = pd.read_csv(path)
    return frame.head(10).where(pd.notna(frame), "").to_dict(orient="records")


def copy_first_10_tables(outputs_dir: Path, tables_dir: Path) -> tuple[list[Path], list[str]]:
    tables: list[Path] = []
    warnings: list[str] = []

    for technology in TECHNOLOGY_ORDER:
        technology_dir = outputs_dir / technology
        if not technology_dir.exists():
            if technology in OPTIONAL_OUTPUT_TECHNOLOGIES:
                continue
            warnings.append(f"Missing output directory: {display_path(technology_dir)}")
            continue
        for job_dir in sorted(path for path in technology_dir.iterdir() if path.is_dir() and not path.name.startswith(".")):
            source_path = job_dir / "first_10.csv"
            if not source_path.exists():
                warnings.append(f"Missing first-10 sample: {display_path(source_path)}")
                continue
            records = read_first_10_records(source_path)
            tables.extend(write_table_pair(tables_dir, f"first_10_{technology}_{job_dir.name}", records))

    return tables, warnings


def audit_results_dirs(benchmark_csvs: Iterable[Path]) -> list[Path]:
    return sorted(
        {
            path.parent
            for path in benchmark_csvs
            if path.parent.name in {"aws-emr", "aws-emr-larger"}
            or path.parent.as_posix().endswith(("aws-emr", "aws-emr-larger"))
        }
    )


def read_aws_run_manifest_records(results_dirs: Iterable[Path]) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for results_dir in results_dirs:
        for path in sorted(results_dir.glob("run_manifest_*.json")):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            aws = data.get("aws", {}) if isinstance(data.get("aws"), dict) else {}
            git = data.get("git", {}) if isinstance(data.get("git"), dict) else {}
            artifacts = data.get("artifacts", {}) if isinstance(data.get("artifacts"), dict) else {}
            records.append(
                {
                    "run_id": data.get("run_id", ""),
                    "run_kind": data.get("run_kind", ""),
                    "status": data.get("status", ""),
                    "is_canonical_full_run": data.get("is_canonical_full_run", ""),
                    "canonical_run_id": data.get("canonical_run_id", ""),
                    "git_commit": git.get("commit", ""),
                    "git_dirty": git.get("dirty", ""),
                    "bucket": aws.get("bucket", ""),
                    "region": aws.get("region", ""),
                    "emr_release": aws.get("emr_release", ""),
                    "cluster_id": aws.get("cluster_id", ""),
                    "instance_type": aws.get("instance_type", ""),
                    "node_count": aws.get("node_count", ""),
                    "source_bundle_sha256": artifacts.get("source_bundle_sha256", ""),
                    "runtime_config_sha256": artifacts.get("runtime_config_sha256", ""),
                    "config_sha256": artifacts.get("config_sha256", ""),
                    "dependencies": "; ".join(str(item) for item in data.get("python_dependencies", [])),
                }
            )
    return records


def read_csv_records(paths: Iterable[Path]) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for path in paths:
        try:
            with path.open(newline="", encoding="utf-8-sig") as file:
                records.extend(dict(row) for row in csv.DictReader(file))
        except OSError:
            continue
    return records


def copy_aws_first_10_tables(results_dirs: Iterable[Path], tables_dir: Path, run_ids: set[str]) -> tuple[list[Path], list[str]]:
    tables: list[Path] = []
    warnings: list[str] = []
    if not run_ids:
        return tables, warnings

    for results_dir in results_dirs:
        downloaded = results_dir / "downloaded"
        if not downloaded.exists():
            continue
        for run_id in sorted(run_ids):
            run_dir = downloaded / run_id
            if not run_dir.exists():
                continue
            outputs = run_dir / "outputs"
            if not outputs.exists():
                warnings.append(f"Missing downloaded AWS outputs: {display_path(outputs)}")
                continue
            for source_path in sorted(outputs.glob("*/*/rep1/*/*/first_10.csv")):
                parts = source_path.relative_to(outputs).parts
                if len(parts) < 6:
                    continue
                input_label, technology, repetition, _, job_name, _ = parts[:6]
                records = read_first_10_records(source_path)
                stem = f"first_10_{results_dir.name}_{run_id}_{input_label}_{technology}_{repetition}_{job_name}"
                tables.extend(write_table_pair(tables_dir, stem, records))
    return tables, warnings


def generate_artifacts(
    *,
    benchmark_csvs: list[Path],
    outputs_dir: Path,
    figures_dir: Path,
    tables_dir: Path,
) -> GeneratedArtifacts:
    warnings: list[str] = []
    if not benchmark_csvs:
        warnings.append("No timestamped benchmark CSV files found.")

    invalid_csvs = [(path, benchmark_csv_schema_errors(path)) for path in benchmark_csvs]
    invalid_csvs = [(path, errors) for path, errors in invalid_csvs if errors]
    for path, errors in invalid_csvs:
        warnings.append(f"Skipping invalid benchmark CSV {display_path(path)}: {'; '.join(errors)}")

    all_rows = read_benchmark_rows(benchmark_csvs)
    successful_rows = [
        row
        for row in all_rows
        if str(row.get("status", "")).lower() == "success"
    ]
    latest_rows = latest_successful_rows(successful_rows)
    summary = benchmark_summary_records(latest_rows)
    pivot = benchmark_pivot_records(summary)
    status = benchmark_status_records(all_rows)
    rows_per_second = rows_per_second_records(summary)
    speedups = speedup_records(pivot)
    scalability = scalability_ratio_records(summary)
    cluster_comparison = cluster_size_comparison_records(summary)

    tables: list[Path] = []
    tables.extend(write_table_pair(tables_dir, "benchmark_summary", summary))
    tables.extend(write_table_pair(tables_dir, "benchmark_pivot", pivot))
    tables.extend(write_table_pair(tables_dir, "benchmark_status", status))
    tables.extend(write_table_pair(tables_dir, "rows_per_second", rows_per_second))
    tables.extend(write_table_pair(tables_dir, "speedup", speedups))
    tables.extend(write_table_pair(tables_dir, "scalability_ratios", scalability))
    tables.extend(write_table_pair(tables_dir, "cluster_size_comparison", cluster_comparison))

    first_10_tables, first_10_warnings = copy_first_10_tables(outputs_dir, tables_dir)
    tables.extend(first_10_tables)
    warnings.extend(first_10_warnings)

    aws_results_dirs = audit_results_dirs(benchmark_csvs)
    aws_run_ids = {
        str(row.get("run_id", ""))
        for row in latest_rows
        if str(row.get("environment", "")).startswith("aws-emr") and row.get("run_id")
    }
    manifest_records = read_aws_run_manifest_records(aws_results_dirs)
    step_timing_records = read_csv_records(path for results_dir in aws_results_dirs for path in sorted(results_dir.glob("step_timing_*.csv")))
    cost_records = read_csv_records(path for results_dir in aws_results_dirs for path in sorted(results_dir.glob("cost_log_*.csv")))
    tables.extend(write_table_pair(tables_dir, "aws_run_manifest", manifest_records))
    tables.extend(write_table_pair(tables_dir, "aws_step_timing", step_timing_records))
    tables.extend(write_table_pair(tables_dir, "aws_cost_log", cost_records))
    aws_first_10_tables, aws_first_10_warnings = copy_aws_first_10_tables(aws_results_dirs, tables_dir, aws_run_ids)
    tables.extend(aws_first_10_tables)
    warnings.extend(aws_first_10_warnings)

    figures = generate_execution_time_charts(latest_rows, figures_dir)
    return GeneratedArtifacts(figures=figures, tables=tables, warnings=warnings)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--results-dir",
        action="append",
        type=Path,
        help="Benchmark results directory to scan. Repeatable. Defaults to local and Docker simulation result directories.",
    )
    parser.add_argument(
        "--benchmark-csv",
        action="append",
        type=Path,
        help="Explicit benchmark CSV to include. Repeatable. Overrides results-dir discovery.",
    )
    parser.add_argument("--outputs-dir", type=Path, default=DEFAULT_OUTPUTS_DIR, help="Technology outputs directory.")
    parser.add_argument("--figures-dir", type=Path, default=DEFAULT_FIGURES_DIR, help="Report figures directory.")
    parser.add_argument("--tables-dir", type=Path, default=DEFAULT_TABLES_DIR, help="Report tables directory.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    results_dirs = [resolve_project_path(path) for path in (args.results_dir or DEFAULT_RESULTS_DIRS)]
    benchmark_csvs = (
        [resolve_project_path(path) for path in args.benchmark_csv]
        if args.benchmark_csv
        else discover_benchmark_csvs(results_dirs)
    )
    artifacts = generate_artifacts(
        benchmark_csvs=benchmark_csvs,
        outputs_dir=resolve_project_path(args.outputs_dir),
        figures_dir=resolve_project_path(args.figures_dir),
        tables_dir=resolve_project_path(args.tables_dir),
    )

    for warning in artifacts.warnings:
        print(f"# Warning: {warning}", file=sys.stderr)
    print(f"# Figures written: {len(artifacts.figures)}")
    for path in artifacts.figures:
        print(f"# - {display_path(path)}")
    print(f"# Tables written: {len(artifacts.tables)}")
    for path in artifacts.tables:
        print(f"# - {display_path(path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
