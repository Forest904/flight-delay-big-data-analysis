"""Run and audit the final submission gate."""

from __future__ import annotations

import argparse
import csv
import re
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TABLES_DIR = PROJECT_ROOT / "report" / "tables"
FIGURES_DIR = PROJECT_ROOT / "report" / "figures"

JOBS = ("delay_by_airport_month", "airline_airport_ranking")
OUTPUT_JOBS = (*JOBS, "delay_by_airport_month_all_causes")
CORE_TECHNOLOGIES = ("Spark SQL", "Spark Core", "Hive")
LOCAL_INPUTS = ("100k", "500k", "1m", "3m", "full", "14m", "28m")
DOCKER_INPUTS = ("100k", "500k", "1m", "3m", "full", "14m", "28m")
NOTE_COLUMNS = ("environment", "input_label", "job_name", "technology", "run_id", "classification", "note")
NOTE_CLASSIFICATIONS = {"smoke", "budget_limited", "resource_limited"}

REQUIRED_TABLES = (
    "benchmark_summary.csv",
    "benchmark_summary.md",
    "benchmark_phase_summary.csv",
    "benchmark_phase_summary.md",
    "benchmark_status.csv",
    "benchmark_status.md",
    "benchmark_pivot.csv",
    "benchmark_pivot.md",
    "rows_per_second.csv",
    "rows_per_second.md",
    "speedup.csv",
    "speedup.md",
    "scalability_ratios.csv",
    "scalability_ratios.md",
    "cluster_size_comparison.csv",
    "cluster_size_comparison.md",
    "environment_summary.csv",
    "environment_summary.md",
    "environment_summary.json",
    "benchmark_notes.csv",
)
REQUIRED_FIGURES = (
    "execution_time_local_delay_by_airport_month.png",
    "execution_time_local_airline_airport_ranking.png",
    "execution_time_local_delay_by_airport_month_spark_hive.png",
    "execution_time_local_airline_airport_ranking_spark_hive.png",
    "execution_time_docker-simulation_delay_by_airport_month.png",
    "execution_time_docker-simulation_airline_airport_ranking.png",
    "execution_time_docker-simulation_delay_by_airport_month_spark_hive.png",
    "execution_time_docker-simulation_airline_airport_ranking_spark_hive.png",
    "execution_time_aws-emr-larger_delay_by_airport_month.png",
    "execution_time_aws-emr-larger_airline_airport_ranking.png",
)
TECHNOLOGY_SLUGS = {
    "spark_sql": "spark_sql",
    "spark_core": "spark_core",
    "hive": "hive",
    "mapreduce": "mapreduce",
}
GATE_COMMANDS = (
    (sys.executable, "-m", "pytest", "-q"),
    ("make", "validate-spark-sql"),
    ("make", "validate-spark-core"),
    ("make", "validate-hive"),
    ("make", "validate-mapreduce"),
    ("make", "charts"),
    ("make", "report"),
)

SECRET_PATTERNS = (
    re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    re.compile(r"\bKAGGLE_KEY\s*=\s*(?!your_|<|\.{3}|$)[A-Za-z0-9_-]{20,}\b", re.IGNORECASE),
    re.compile(r"\bKGAT[A-Za-z0-9_-]{16,}\b"),
    re.compile(r"\bAWS_SECRET_ACCESS_KEY\s*=\s*(?!your_|<|\.{3}|$)[A-Za-z0-9/+=]{30,}", re.IGNORECASE),
    re.compile(r"\bAWS_SESSION_TOKEN\s*=\s*(?!your_|<|\.{3}|$)[A-Za-z0-9/+=]{40,}", re.IGNORECASE),
)
BINARY_SUFFIXES = {".pdf", ".png", ".jpg", ".jpeg", ".gif", ".ico", ".parquet", ".zip", ".jar"}


def display_path(path: Path, project_root: Path = PROJECT_ROOT) -> str:
    try:
        return path.relative_to(project_root).as_posix()
    except ValueError:
        return path.as_posix()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))


def run_gate_commands(project_root: Path = PROJECT_ROOT) -> list[str]:
    failures: list[str] = []
    for command in GATE_COMMANDS:
        print("# " + " ".join(command))
        result = subprocess.run(command, cwd=project_root, text=True, check=False)
        if result.returncode != 0:
            failures.append(f"Command failed with exit code {result.returncode}: {' '.join(command)}")
            break
    return failures


def required_first_10_table_names() -> list[str]:
    names: list[str] = []
    for technology in TECHNOLOGY_SLUGS:
        for job in OUTPUT_JOBS:
            stem = f"first_10_{technology}_{job}"
            names.extend([f"{stem}.csv", f"{stem}.md"])
    return names


def audit_report_artifacts(
    tables_dir: Path = TABLES_DIR,
    figures_dir: Path = FIGURES_DIR,
) -> list[str]:
    failures: list[str] = []
    required_tables = (*REQUIRED_TABLES, *required_first_10_table_names())
    for name in required_tables:
        path = tables_dir / name
        if not path.is_file() or path.stat().st_size == 0:
            failures.append(f"Missing or empty report table: {display_path(path)}")
    for name in REQUIRED_FIGURES:
        path = figures_dir / name
        if not path.is_file() or path.stat().st_size == 0:
            failures.append(f"Missing or empty report figure: {display_path(path)}")
    return failures


def benchmark_key(row: dict[str, str]) -> tuple[str, str, str, str]:
    return (
        row.get("environment", ""),
        row.get("input_label", ""),
        row.get("job_name", ""),
        row.get("technology", ""),
    )


def audit_required_benchmark_cells(rows: list[dict[str, str]]) -> list[str]:
    failures: list[str] = []
    present = {benchmark_key(row) for row in rows}
    required: list[tuple[str, str, str, str]] = []
    for input_label in LOCAL_INPUTS:
        for job_name in JOBS:
            for technology in CORE_TECHNOLOGIES:
                required.append(("local", input_label, job_name, technology))
    for input_label in DOCKER_INPUTS:
        for job_name in JOBS:
            for technology in CORE_TECHNOLOGIES:
                required.append(("docker-simulation", input_label, job_name, technology))

    for key in required:
        if key not in present:
            failures.append("Missing benchmark summary cell: " + " / ".join(key))
    return failures


def validate_notes(notes: list[dict[str, str]]) -> list[str]:
    failures: list[str] = []
    for index, note in enumerate(notes, start=2):
        missing = [column for column in NOTE_COLUMNS if column not in note]
        if missing:
            failures.append(f"benchmark_notes.csv row {index} is missing column(s): {', '.join(missing)}")
            continue
        classification = note.get("classification", "")
        if classification not in NOTE_CLASSIFICATIONS:
            failures.append(f"benchmark_notes.csv row {index} has invalid classification: {classification}")
        if not note.get("note", "").strip():
            failures.append(f"benchmark_notes.csv row {index} must include a note")
    return failures


def note_matches(row: dict[str, str], note: dict[str, str]) -> bool:
    if row.get("environment", "") != note.get("environment", ""):
        return False
    for column in ("input_label", "job_name", "technology", "run_id"):
        expected = note.get(column, "")
        if expected != "*" and row.get(column, "") != expected:
            return False
    return True


def audit_single_run_notes(rows: list[dict[str, str]], notes: list[dict[str, str]]) -> list[str]:
    failures: list[str] = []
    failures.extend(validate_notes(notes))
    if failures:
        return failures

    for row in rows:
        try:
            runs = int(float(row.get("runs", "0") or 0))
        except ValueError:
            failures.append(f"Invalid runs value in benchmark_summary.csv: {row.get('runs')}")
            continue
        if runs != 1:
            continue
        if not any(note_matches(row, note) for note in notes):
            failures.append(
                "runs=1 benchmark row lacks explicit note: "
                f"{row.get('environment')} / {row.get('input_label')} / {row.get('job_name')} / "
                f"{row.get('technology')} / {row.get('run_id')}"
            )
    return failures


def audit_benchmark_summary(tables_dir: Path = TABLES_DIR) -> list[str]:
    summary_path = tables_dir / "benchmark_summary.csv"
    notes_path = tables_dir / "benchmark_notes.csv"
    failures: list[str] = []
    if not summary_path.is_file():
        return [f"Missing benchmark summary: {display_path(summary_path)}"]
    if not notes_path.is_file():
        return [f"Missing benchmark notes: {display_path(notes_path)}"]

    rows = read_csv(summary_path)
    notes = read_csv(notes_path)
    failures.extend(audit_required_benchmark_cells(rows))
    failures.extend(audit_single_run_notes(rows, notes))
    return failures


def tracked_files(project_root: Path = PROJECT_ROOT) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=project_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git ls-files failed")
    return [line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip()]


def is_gitkeep(path: str) -> bool:
    return path.endswith("/.gitkeep")


def forbidden_tracked_artifact(path: str) -> str | None:
    if path == ".env":
        return "private environment file is tracked"
    if path == "derby.log":
        return "Derby scratch log is tracked"
    if path.endswith(".parquet"):
        return "generated or prepared Parquet file is tracked"
    for prefix in ("data/raw/", "data/prepared/", "data/generated/"):
        if path.startswith(prefix) and not is_gitkeep(path):
            return f"runtime data path is tracked: {prefix}"
    if path.startswith("outputs/") and not is_gitkeep(path):
        return "runtime output artifact is tracked"
    if path.startswith("experiments/results/") and not is_gitkeep(path):
        return "benchmark result/log/download artifact is tracked"
    if "/downloaded/" in path:
        return "downloaded AWS artifact is tracked"
    return None


def audit_tracked_artifacts(files: list[str]) -> list[str]:
    failures: list[str] = []
    for path in files:
        reason = forbidden_tracked_artifact(path)
        if reason is not None:
            failures.append(f"{path}: {reason}")
    return failures


def scan_text_for_secrets(path: Path) -> list[str]:
    if path.suffix.lower() in BINARY_SUFFIXES:
        return []
    if not path.exists():
        return []
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []
    findings: list[str] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if any(pattern.search(line) for pattern in SECRET_PATTERNS):
            findings.append(f"{display_path(path)}:{line_number}: credential-like value")
    return findings


def audit_credentials(files: list[str], project_root: Path = PROJECT_ROOT) -> list[str]:
    failures: list[str] = []
    for path in files:
        failures.extend(scan_text_for_secrets(project_root / path))
    return failures


def audit_hygiene(project_root: Path = PROJECT_ROOT) -> list[str]:
    files = tracked_files(project_root)
    failures: list[str] = []
    failures.extend(audit_tracked_artifacts(files))
    failures.extend(audit_credentials(files, project_root=project_root))
    return failures


def audit_submission(project_root: Path = PROJECT_ROOT) -> list[str]:
    failures: list[str] = []
    failures.extend(audit_report_artifacts(project_root / "report" / "tables", project_root / "report" / "figures"))
    failures.extend(audit_benchmark_summary(project_root / "report" / "tables"))
    failures.extend(audit_hygiene(project_root))
    return failures


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit-only", action="store_true", help="Skip rebuild commands and only audit current artifacts.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    failures: list[str] = []
    if not args.audit_only:
        failures.extend(run_gate_commands(PROJECT_ROOT))
    if not failures:
        failures.extend(audit_submission(PROJECT_ROOT))

    if failures:
        print("# Submission check failed", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print("Submission check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
