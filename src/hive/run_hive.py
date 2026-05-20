"""Run the HiveQL analyses for the flight delay project."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = PROJECT_ROOT / "config" / "local.yaml"
HIVE_DIR = PROJECT_ROOT / "src" / "hive"
HIVE_FIELD_DELIMITER = "\x01"
HIVE_NULL_VALUE = r"\N"

DDL_FILE = HIVE_DIR / "ddl.sql"
DELAY_QUERY_FILE = HIVE_DIR / "analysis_delay_by_airport_month.sql"
RANKING_QUERY_FILE = HIVE_DIR / "analysis_airline_airport_ranking.sql"

HIVE_JDBC_URL = "jdbc:hive2://localhost:10000/"
LOCATION_PATTERN = re.compile(r"\bLOCATION\s+'[^']+'", re.IGNORECASE)

DELAY_OUTPUT_COLUMNS = [
    "origin_airport",
    "month",
    "delay_range",
    "flight_count",
    "avg_departure_delay",
    "avg_arrival_delay",
    "top_delay_or_cancellation_cause",
]

RANKING_OUTPUT_COLUMNS = [
    "origin_airport",
    "airline",
    "flight_count",
    "avg_departure_delay",
    "avg_arrival_delay",
    "cancellation_rate",
    "airport_avg_departure_delay",
    "difference_from_airport_avg_departure_delay",
    "rank_at_airport",
]


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)
    if not isinstance(data, dict):
        raise ValueError(f"{path} did not contain a YAML mapping")
    return data


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-path",
        type=Path,
        help="Prepared Parquet input to analyze. Defaults to the selected config paths.prepared_file.",
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG, help="YAML config path.")
    return parser.parse_args(argv)


def resolve_project_path(path_value: str) -> Path:
    path = Path(path_value)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path


def hive_output_root(local_config: dict[str, Any]) -> Path:
    paths = local_config.get("paths", {})
    outputs_dir = resolve_project_path(str(paths.get("outputs_dir", "outputs")))
    return outputs_dir / "hive"


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def clear_path(path: Path) -> None:
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()


def clear_hive_outputs(output_root: Path) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    for child in output_root.iterdir():
        if child.name == ".gitkeep":
            continue
        clear_path(child)


def metrics_file(output_root: Path) -> Path:
    return output_root / "runtime_metrics.json"


def write_metrics(metrics: dict[str, Any], output_root: Path) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    with metrics_file(output_root).open("w", encoding="utf-8") as file:
        json.dump(metrics, file, indent=2, sort_keys=True)
        file.write("\n")


def error_excerpt(error: Exception | str, max_chars: int = 3000) -> str:
    text = str(error)
    if len(text) <= max_chars:
        return text
    return f"{text[:max_chars]}... [truncated]"


def docker_executable() -> str:
    configured = os.environ.get("DOCKER")
    if configured:
        return configured.strip('"')

    discovered = shutil.which("docker")
    if discovered:
        return discovered

    if os.name == "nt":
        docker_desktop = Path("C:/Program Files/Docker/Docker/resources/bin/docker.exe")
        if docker_desktop.exists():
            return str(docker_desktop)

    raise FileNotFoundError("Docker was not found. Install Docker Desktop or set DOCKER to the docker executable.")


def docker_compose_command(*args: str) -> list[str]:
    return [docker_executable(), "compose", *args]


def run_command(command: list[str], timeout_seconds: int | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=timeout_seconds,
    )


def command_error(command: list[str], result: subprocess.CompletedProcess[str]) -> RuntimeError:
    output = "\n".join(part for part in [result.stdout.strip(), result.stderr.strip()] if part)
    return RuntimeError(
        f"Command failed with exit code {result.returncode}: {' '.join(command)}\n{error_excerpt(output)}"
    )


def validate_preconditions(prepared_file: Path) -> list[str]:
    errors: list[str] = []
    if not prepared_file.exists():
        errors.append(
            f"Prepared dataset was not found: {display_path(prepared_file)}. Run `make prepare` or `make generate-sizes` first."
        )
    for sql_file in (DDL_FILE, DELAY_QUERY_FILE, RANKING_QUERY_FILE):
        if not sql_file.exists():
            errors.append(f"Required Hive SQL file is missing: {display_path(sql_file)}")
    try:
        result = run_command(docker_compose_command("version"), timeout_seconds=30)
    except Exception as exc:
        errors.append(str(exc))
    else:
        if result.returncode != 0:
            errors.append(error_excerpt(result.stderr or result.stdout))
    try:
        result = run_command([docker_executable(), "info"], timeout_seconds=30)
    except Exception as exc:
        errors.append(str(exc))
    else:
        if result.returncode != 0:
            errors.append(
                "Docker daemon is not reachable. Start Docker Desktop before `make run-hive`. "
                + error_excerpt(result.stderr or result.stdout)
            )
    return errors


def start_hive_services() -> None:
    command = docker_compose_command("up", "-d", "--build", "hiveserver2")
    result = run_command(command, timeout_seconds=900)
    if result.returncode != 0:
        raise command_error(command, result)


def beeline_command(*args: str, show_header: bool = False, output_format: str = "csv2") -> list[str]:
    return docker_compose_command(
        "exec",
        "-T",
        "-e",
        "HOME=/tmp",
        "hiveserver2",
        "beeline",
        "-u",
        HIVE_JDBC_URL,
        "--silent=true",
        "--showWarnings=false",
        f"--showHeader={str(show_header).lower()}",
        f"--outputformat={output_format}",
        "--hiveconf",
        "hive.execution.engine=mr",
        "--hiveconf",
        "mapreduce.framework.name=local",
        "--hiveconf",
        "hive.exec.mode.local.auto=true",
        "--hiveconf",
        "hive.fetch.task.conversion=more",
        *args,
    )


def wait_for_hiveserver2(timeout_seconds: int = 240) -> None:
    deadline = time.monotonic() + timeout_seconds
    last_error = "HiveServer2 did not respond before the first readiness attempt completed."
    while time.monotonic() < deadline:
        command = beeline_command("-e", "SELECT 1")
        result = run_command(command, timeout_seconds=45)
        if result.returncode == 0 and "1" in result.stdout:
            return
        last_error = result.stderr.strip() or result.stdout.strip() or f"exit code {result.returncode}"
        time.sleep(5)
    raise TimeoutError(f"HiveServer2 did not become ready within {timeout_seconds} seconds: {error_excerpt(last_error)}")


def run_beeline_file(
    sql_file: Path,
    show_header: bool = False,
    timeout_seconds: int = 1800,
    output_format: str = "csv2",
) -> str:
    command = beeline_command(
        "-f",
        f"/workspace/{sql_file.relative_to(PROJECT_ROOT).as_posix()}",
        show_header=show_header,
        output_format=output_format,
    )
    result = run_command(command, timeout_seconds=timeout_seconds)
    if result.returncode != 0:
        raise command_error(command, result)
    return result.stdout


def query_without_trailing_semicolon(sql_file: Path) -> str:
    query = sql_file.read_text(encoding="utf-8").strip()
    if query.endswith(";"):
        query = query[:-1].rstrip()
    return query


def container_workspace_path(path: Path) -> str:
    return f"/workspace/{path.relative_to(PROJECT_ROOT).as_posix()}"


def hive_file_location(path: Path) -> str:
    return f"file://{container_workspace_path(path)}"


def build_ddl_sql(input_path: Path) -> str:
    ddl = DDL_FILE.read_text(encoding="utf-8")
    replacement = f"LOCATION '{hive_file_location(input_path)}'"
    updated, replacements = LOCATION_PATTERN.subn(replacement, ddl)
    if replacements != 1:
        raise ValueError(f"Expected exactly one LOCATION clause in {display_path(DDL_FILE)}, found {replacements}")
    return updated


def write_runtime_ddl(input_path: Path, query_root: Path) -> Path:
    query_root.mkdir(parents=True, exist_ok=True)
    runtime_ddl = query_root / "ddl.sql"
    runtime_ddl.write_text(build_ddl_sql(input_path), encoding="utf-8")
    return runtime_ddl


def build_export_sql(name: str, sql_file: Path, container_export_path: str) -> str:
    query = query_without_trailing_semicolon(sql_file)
    table_name = f"flight_delay.tmp_export_{name}"
    return (
        f"DROP TABLE IF EXISTS {table_name};\n"
        f"CREATE TABLE {table_name}\n"
        "ROW FORMAT DELIMITED\n"
        "FIELDS TERMINATED BY '\\001'\n"
        "STORED AS TEXTFILE\n"
        f"LOCATION 'file://{container_export_path}'\n"
        "AS\n"
        f"{query};\n"
    )


def export_query_to_directory(name: str, sql_file: Path, export_root: Path) -> Path:
    query_dir = export_root / ".queries"
    query_dir.mkdir(parents=True, exist_ok=True)
    local_export_path = export_root / name
    clear_path(local_export_path)
    local_export_path.parent.mkdir(parents=True, exist_ok=True)

    wrapper_sql = query_dir / f"{name}.sql"
    wrapper_sql.write_text(
        build_export_sql(name, sql_file, container_workspace_path(local_export_path)),
        encoding="utf-8",
    )
    run_beeline_file(wrapper_sql, show_header=False, output_format="tsv2")
    return local_export_path


def exported_part_files(export_path: Path) -> list[Path]:
    if not export_path.exists():
        raise FileNotFoundError(f"Hive export directory was not created: {display_path(export_path)}")
    parts = sorted(path for path in export_path.iterdir() if path.is_file() and not path.name.startswith((".", "_")))
    if not parts:
        raise FileNotFoundError(f"No Hive export part files found under {display_path(export_path)}")
    return parts


def dataframe_from_export(export_path: Path, expected_columns: list[str]) -> pd.DataFrame:
    frames = [
        pd.read_csv(
            part,
            sep=HIVE_FIELD_DELIMITER,
            header=None,
            names=expected_columns,
            na_values=[HIVE_NULL_VALUE],
            keep_default_na=True,
            engine="python",
        )
        for part in exported_part_files(export_path)
    ]
    df = pd.concat(frames, ignore_index=True)
    actual_columns = list(df.columns)
    if actual_columns != expected_columns:
        raise ValueError(f"Hive output columns differ. Expected {expected_columns}, found {actual_columns}")
    return df


def write_outputs(df: pd.DataFrame, full_output_path: Path, sample_output_path: Path) -> None:
    clear_path(full_output_path)
    full_output_path.mkdir(parents=True, exist_ok=True)
    sample_output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(full_output_path / "part-00000.csv", index=False)
    df.head(10).to_csv(sample_output_path, index=False)


def run_analysis(
    name: str,
    sql_file: Path,
    expected_columns: list[str],
    full_output_path: Path,
    sample_output_path: Path,
    export_root: Path,
) -> dict[str, Any]:
    started = time.perf_counter()
    status = "success"
    error: str | None = None
    output_rows = 0

    try:
        export_path = export_query_to_directory(name, sql_file, export_root)
        df = dataframe_from_export(export_path, expected_columns)
        output_rows = len(df)
        write_outputs(df, full_output_path, sample_output_path)
    except Exception as exc:
        status = "failed"
        error = error_excerpt(exc)
    finally:
        duration_seconds = round(time.perf_counter() - started, 6)

    metrics: dict[str, Any] = {
        "job_name": name,
        "duration_seconds": duration_seconds,
        "output_rows": output_rows,
        "full_output_path": display_path(full_output_path),
        "sample_output_path": display_path(sample_output_path),
        "status": status,
    }
    if error is not None:
        metrics["error"] = error
    return metrics


def mark_failed(metrics: dict[str, Any], stage: str, error: Exception | str) -> None:
    metrics["status"] = "failed"
    metrics["stage"] = stage
    metrics["error"] = error_excerpt(error)


def print_metrics(metrics: dict[str, Any], output_root: Path) -> None:
    print("# Hive Runtime Metrics")
    print(json.dumps(metrics, indent=2, sort_keys=True))
    print(f"Hive outputs written to: {display_path(output_root)}")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    config_path = args.config if args.config.is_absolute() else PROJECT_ROOT / args.config
    local_config = load_yaml(config_path)
    paths = local_config.get("paths", {})
    prepared_file_value = paths.get("prepared_file")
    if not prepared_file_value:
        raise ValueError(f"{config_path} does not define paths.prepared_file")

    prepared_file = args.input_path if args.input_path is not None else Path(str(prepared_file_value))
    if not prepared_file.is_absolute():
        prepared_file = PROJECT_ROOT / prepared_file
    output_root = hive_output_root(local_config)
    export_root = output_root / ".tmp_exports"
    query_root = output_root / ".tmp_queries"
    hive_table_location = hive_file_location(prepared_file)
    run_metrics: dict[str, Any] = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "technology": "hive",
        "status": "running",
        "stage": "preflight",
        "input_path": display_path(prepared_file),
        "hive_jdbc_url": HIVE_JDBC_URL,
        "hive_table": "flight_delay.flights_2024_clean",
        "hive_table_location": hive_table_location,
        "jobs": [],
    }

    preflight_errors = validate_preconditions(prepared_file)
    if preflight_errors:
        print("# Hive preflight failed", file=sys.stderr)
        for error in preflight_errors:
            print(f"- {error}", file=sys.stderr)
        mark_failed(run_metrics, "preflight", "; ".join(preflight_errors))
        write_metrics(run_metrics, output_root)
        print_metrics(run_metrics, output_root)
        return 1

    try:
        run_metrics["stage"] = "compose_up"
        write_metrics(run_metrics, output_root)
        start_hive_services()

        run_metrics["stage"] = "hiveserver2_ready"
        write_metrics(run_metrics, output_root)
        wait_for_hiveserver2()

        clear_hive_outputs(output_root)

        run_metrics["stage"] = "ddl"
        write_metrics(run_metrics, output_root)
        runtime_ddl = write_runtime_ddl(prepared_file, query_root)
        run_beeline_file(runtime_ddl, show_header=False, timeout_seconds=600)

        run_metrics["stage"] = "analysis"
        write_metrics(run_metrics, output_root)

        analyses = [
            (
                "delay_by_airport_month",
                DELAY_QUERY_FILE,
                DELAY_OUTPUT_COLUMNS,
                output_root / "delay_by_airport_month" / "full",
                output_root / "delay_by_airport_month" / "first_10.csv",
            ),
            (
                "airline_airport_ranking",
                RANKING_QUERY_FILE,
                RANKING_OUTPUT_COLUMNS,
                output_root / "airline_airport_ranking" / "full",
                output_root / "airline_airport_ranking" / "first_10.csv",
            ),
        ]

        for name, sql_file, expected_columns, full_path, sample_path in analyses:
            run_metrics["stage"] = f"job:{name}"
            job_metrics = run_analysis(name, sql_file, expected_columns, full_path, sample_path, export_root)
            run_metrics["jobs"].append(job_metrics)
            write_metrics(run_metrics, output_root)
            if job_metrics["status"] != "success":
                run_metrics["status"] = "failed"
                run_metrics["error"] = job_metrics.get("error")
                break
        else:
            run_metrics["status"] = "success"
            run_metrics["stage"] = "complete"
    except Exception as exc:
        mark_failed(run_metrics, str(run_metrics.get("stage", "unknown")), exc)

    write_metrics(run_metrics, output_root)
    print_metrics(run_metrics, output_root)
    return 0 if run_metrics["status"] == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())
