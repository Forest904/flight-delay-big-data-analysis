"""Generate report-ready benchmark charts and tables."""

from __future__ import annotations

import argparse
import csv
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
DEFAULT_RESULTS_DIRS = (
    PROJECT_ROOT / "experiments" / "results" / "local",
    PROJECT_ROOT / "experiments" / "results" / "cluster",
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
}
BENCHMARK_FILE_RE = re.compile(r"^benchmark_\d{8}T\d{6}(?:\d{6})?Z(?:_\d+)?\.csv$")
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
    ),
}
LEGACY_ENVIRONMENT_LABELS = {
    "docker-cluster": "docker-simulation",
}


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
    text = str(value or "")
    return LEGACY_ENVIRONMENT_LABELS.get(text, text)


def discover_benchmark_csvs(results_dirs: Iterable[Path]) -> list[Path]:
    csvs: list[Path] = []
    for results_dir in results_dirs:
        if not results_dir.exists():
            continue
        csvs.extend(
            path
            for path in results_dir.glob("benchmark_*.csv")
            if BENCHMARK_FILE_RE.fullmatch(path.name)
        )
    return sorted(csvs)


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
        with csv_path.open(newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
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
    latest_by_key: dict[tuple[str, str, str, str], dict[str, object]] = {}
    for row in rows:
        key = (
            str(row.get("environment", "")),
            str(row.get("input_label", "")),
            str(row.get("job_name", "")),
            str(row.get("technology", "")),
        )
        current = latest_by_key.get(key)
        if current is None or row["_timestamp"] > current["_timestamp"]:
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
        if current is None or row["_timestamp"] > current["_timestamp"]:
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
    records: list[dict[str, object]] = []
    for row in rows:
        records.append(
            {
                "environment": row.get("environment", ""),
                "input_label": row.get("input_label", ""),
                "records": int(float(row.get("records") or 0)),
                "job_name": row.get("job_name", ""),
                "technology": TECHNOLOGY_LABELS.get(str(row.get("technology", "")), row.get("technology", "")),
                "duration_seconds": float(row.get("duration_seconds") or 0),
                "output_rows": int(float(row.get("output_rows") or 0)),
                "run_id": row.get("run_id", ""),
                "timestamp_utc": row.get("timestamp_utc", ""),
            }
        )
    return records


def benchmark_pivot_records(summary: list[dict[str, object]]) -> list[dict[str, object]]:
    if not summary:
        return []

    frame = pd.DataFrame(summary)
    pivot = (
        frame.pivot_table(
            index=["environment", "input_label", "records", "job_name"],
            columns="technology",
            values="duration_seconds",
            aggfunc="first",
        )
        .reset_index()
        .sort_values(["environment", "records", "input_label", "job_name"])
    )

    ordered_columns = ["environment", "input_label", "records", "job_name"]
    ordered_columns.extend(label for label in TECHNOLOGY_LABELS.values() if label in pivot.columns)
    ordered_columns.extend(column for column in pivot.columns if column not in ordered_columns)
    pivot = pivot[ordered_columns]
    pivot = pivot.rename(columns={label: f"{label} duration_seconds" for label in TECHNOLOGY_LABELS.values()})
    return pivot.where(pd.notna(pivot), "").to_dict(orient="records")


def rows_per_second_records(summary: list[dict[str, object]]) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for row in summary:
        duration_seconds = positive_float(row.get("duration_seconds"))
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
                "duration_seconds": row.get("duration_seconds", ""),
                "rows_per_second": rows_per_second,
            }
        )
    return records


def speedup_records(pivot: list[dict[str, object]]) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for row in pivot:
        spark_sql = row.get("Spark SQL duration_seconds", "")
        spark_core = row.get("Spark Core duration_seconds", "")
        hive = row.get("Hive duration_seconds", "")
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
        baseline_duration = positive_float(baseline.get("duration_seconds"))
        baseline_records = positive_float(baseline.get("records"))
        if baseline_duration is None or baseline_records is None:
            continue
        baseline_throughput = baseline_records / baseline_duration

        for _, row in group.iterrows():
            records_value = positive_float(row.get("records"))
            duration_value = positive_float(row.get("duration_seconds"))
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
                    "duration_vs_100k": divide_or_blank(duration_value, baseline_duration),
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
        for input_label, records in inputs:
            for job_name in JOB_LABELS:
                for technology in CORE_TECHNOLOGY_ORDER:
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
    fieldnames = list(records[0].keys()) if records else []
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

    columns = list(records[0].keys())
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
            if chart_kind == "line":
                if len(tech_group) >= 2:
                    plt.plot(
                        positions,
                        tech_group["duration_seconds"],
                        marker="o",
                        linewidth=1.8,
                        label=technology_label,
                    )
                else:
                    plt.scatter(
                        positions,
                        tech_group["duration_seconds"],
                        marker="o",
                        s=38,
                        label=technology_label,
                    )
            else:
                offset = (technology_index - (len(technology_labels) - 1) / 2) * bar_width
                plt.bar(
                    [position + offset for position in positions],
                    tech_group["duration_seconds"],
                    width=bar_width,
                    label=technology_label,
                )

        environment_label = ENVIRONMENT_LABELS.get(str(environment), str(environment))
        plt.title(f"{JOB_LABELS.get(str(job_name), job_name)} - {environment_label}")
        plt.xlabel("Input size (record count)")
        plt.ylabel("Execution time (seconds)")
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

    tables: list[Path] = []
    tables.extend(write_table_pair(tables_dir, "benchmark_summary", summary))
    tables.extend(write_table_pair(tables_dir, "benchmark_pivot", pivot))
    tables.extend(write_table_pair(tables_dir, "benchmark_status", status))
    tables.extend(write_table_pair(tables_dir, "rows_per_second", rows_per_second))
    tables.extend(write_table_pair(tables_dir, "speedup", speedups))
    tables.extend(write_table_pair(tables_dir, "scalability_ratios", scalability))

    first_10_tables, first_10_warnings = copy_first_10_tables(outputs_dir, tables_dir)
    tables.extend(first_10_tables)
    warnings.extend(first_10_warnings)

    figures = generate_execution_time_charts(latest_rows, figures_dir)
    return GeneratedArtifacts(figures=figures, tables=tables, warnings=warnings)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--results-dir",
        action="append",
        type=Path,
        help="Benchmark results directory to scan. Repeatable. Defaults to local and cluster result directories.",
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
