"""Run benchmark matrices and normalize technology runtime metrics."""

from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = PROJECT_ROOT / "config" / "local.yaml"
DEFAULT_TECHNOLOGIES = ("spark_sql", "spark_core", "hive")
SUPPORTED_TECHNOLOGIES = (*DEFAULT_TECHNOLOGIES, "mapreduce")
PHASE_BENCHMARK_COLUMNS = [
    "input_read_seconds",
    "plan_build_seconds",
    "result_collect_seconds",
    "full_output_write_seconds",
    "sample_output_write_seconds",
    "materialization_mode",
]
BENCHMARK_COLUMNS = [
    "run_id",
    "repetition",
    "technology",
    "job_name",
    "input_label",
    "records",
    "environment",
    "execution_setting",
    "duration_seconds",
    *PHASE_BENCHMARK_COLUMNS,
    "output_rows",
    "status",
    "timestamp_utc",
    "input_path",
    "metrics_path",
    "error",
    "stage",
]


@dataclass(frozen=True)
class BenchmarkInput:
    label: str
    records: int
    path: Path


@dataclass(frozen=True)
class CommandSpec:
    command: list[str]
    metrics_path: Path


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)
    if not isinstance(data, dict):
        raise ValueError(f"{path} did not contain a YAML mapping")
    return data


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise ValueError(f"{display_path(path)} did not contain a JSON object")
    return data


def resolve_project_path(path_value: str | Path, project_root: Path = PROJECT_ROOT) -> Path:
    path = Path(path_value)
    if not path.is_absolute():
        path = project_root / path
    return path


def display_path(path: Path, project_root: Path = PROJECT_ROOT) -> str:
    try:
        return path.relative_to(project_root).as_posix()
    except ValueError:
        return path.as_posix()


def container_workspace_path(path: Path, *, project_root: Path = PROJECT_ROOT, workspace: str = "/workspace") -> str:
    return f"{workspace.rstrip('/')}/{display_path(path, project_root=project_root)}"


def manifest_path(local_config: dict[str, Any], project_root: Path = PROJECT_ROOT) -> Path:
    generated_dir = resolve_project_path(
        str(local_config.get("paths", {}).get("generated_dir", "data/generated")),
        project_root=project_root,
    )
    return generated_dir / "input_size_manifest.json"


def successful_manifest_entries(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    datasets = manifest.get("datasets", [])
    if not isinstance(datasets, list):
        return {}
    return {
        str(entry.get("label")): entry
        for entry in datasets
        if isinstance(entry, dict)
        and entry.get("label") is not None
        and entry.get("validation_status") == "success"
    }


def selected_benchmark_inputs(
    local_config: dict[str, Any],
    manifest: dict[str, Any],
    *,
    include_optional: bool = False,
    labels: list[str] | None = None,
    project_root: Path = PROJECT_ROOT,
) -> list[BenchmarkInput]:
    configured_inputs = local_config.get("benchmark", {}).get("input_sizes", [])
    if not isinstance(configured_inputs, list):
        raise ValueError("config benchmark.input_sizes must be a list")

    manifest_entries = successful_manifest_entries(manifest)
    requested_labels = set(labels or [])
    selected: list[BenchmarkInput] = []
    missing_required: list[str] = []
    missing_optional: list[str] = []

    for entry in configured_inputs:
        if not isinstance(entry, dict):
            continue
        label = str(entry.get("label"))
        is_requested = label in requested_labels
        is_optional = bool(entry.get("optional", False))
        if requested_labels and not is_requested:
            continue
        if is_optional and not include_optional and not is_requested:
            continue

        manifest_entry = manifest_entries.get(label)
        if manifest_entry is None:
            if is_optional:
                missing_optional.append(label)
            else:
                missing_required.append(label)
            continue

        selected.append(
            BenchmarkInput(
                label=label,
                records=int(manifest_entry.get("actual_records", entry.get("records", 0))),
                path=resolve_project_path(str(manifest_entry.get("path", entry.get("path"))), project_root=project_root),
            )
        )

    if requested_labels:
        selected_labels = {item.label for item in selected}
        unknown = sorted(requested_labels - selected_labels)
        if unknown:
            raise ValueError(f"No successfully validated benchmark input found for label(s): {', '.join(unknown)}")
    if missing_required:
        raise ValueError(
            "Missing required benchmark input(s) from the successful manifest: "
            + ", ".join(sorted(missing_required))
            + ". Run `make generate-sizes` first."
        )
    if not selected:
        raise ValueError("No successfully validated benchmark inputs were selected.")
    if missing_optional and not requested_labels:
        print(f"# Skipping missing or unvalidated optional input(s): {', '.join(missing_optional)}", file=sys.stderr)
    return selected


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


def output_root_for_technology(local_config: dict[str, Any], technology: str, project_root: Path = PROJECT_ROOT) -> Path:
    outputs_dir = resolve_project_path(
        str(local_config.get("paths", {}).get("outputs_dir", "outputs")),
        project_root=project_root,
    )
    return outputs_dir / technology


def mapreduce_benchmark_output_root(
    local_config: dict[str, Any],
    *,
    run_id: str,
    input_label: str,
    project_root: Path = PROJECT_ROOT,
) -> Path:
    return output_root_for_technology(local_config, "mapreduce", project_root=project_root) / ".benchmark_runs" / run_id / input_label


def build_command(
    technology: str,
    input_path: Path,
    local_config: dict[str, Any],
    *,
    config_path: Path = DEFAULT_CONFIG,
    project_root: Path = PROJECT_ROOT,
    python_executable: str = sys.executable,
    os_name: str = os.name,
    docker_bin: str | None = None,
    run_id: str | None = None,
    input_label: str | None = None,
) -> CommandSpec:
    input_arg = display_path(input_path, project_root=project_root)
    metrics_path = output_root_for_technology(local_config, technology, project_root=project_root) / "runtime_metrics.json"
    config_arg = display_path(config_path, project_root=project_root)
    benchmark_config = local_config.get("benchmark", {})
    spark_driver_service = benchmark_config.get("spark_driver_service")
    container_workspace = str(benchmark_config.get("container_workspace", "/workspace"))

    if spark_driver_service and technology in {"spark_sql", "spark_core"}:
        script = {
            "spark_sql": "src/spark_sql/run_spark_sql.py",
            "spark_core": "src/spark_core/run_spark_core.py",
        }[technology]
        return CommandSpec(
            command=[
                docker_bin or docker_executable(),
                "compose",
                "exec",
                "-T",
                str(spark_driver_service),
                "python",
                script,
                "--config",
                container_workspace_path(config_path, project_root=project_root, workspace=container_workspace),
                "--input-path",
                container_workspace_path(input_path, project_root=project_root, workspace=container_workspace),
            ],
            metrics_path=metrics_path,
        )

    if technology == "spark_sql":
        command = [
            python_executable,
            "src/spark_sql/run_spark_sql.py",
            "--config",
            config_arg,
            "--input-path",
            input_arg,
        ]
    elif technology == "spark_core":
        if os_name == "nt":
            command = [
                docker_bin or docker_executable(),
                "compose",
                "run",
                "--rm",
                "spark-core",
                "python",
                "src/spark_core/run_spark_core.py",
                "--config",
                config_arg,
                "--input-path",
                input_arg,
            ]
        else:
            command = [
                python_executable,
                "src/spark_core/run_spark_core.py",
                "--config",
                config_arg,
                "--input-path",
                input_arg,
            ]
    elif technology == "hive":
        command = [
            python_executable,
            "src/hive/run_hive.py",
            "--config",
            config_arg,
            "--input-path",
            input_arg,
        ]
    elif technology == "mapreduce":
        if run_id is not None and input_label is not None:
            output_root = mapreduce_benchmark_output_root(
                local_config,
                run_id=run_id,
                input_label=input_label,
                project_root=project_root,
            )
            metrics_path = output_root / "runtime_metrics.json"
            output_root_arg = display_path(output_root, project_root=project_root)
        else:
            output_root_arg = None
        command = [
            python_executable,
            "src/mapreduce/run_mapreduce.py",
            "--config",
            config_arg,
            "--input-path",
            input_arg,
        ]
        if output_root_arg is not None:
            command.extend(["--output-root", output_root_arg])
    else:
        raise ValueError(f"Unsupported technology: {technology}")

    return CommandSpec(command=command, metrics_path=metrics_path)


def run_command(command: list[str], project_root: Path = PROJECT_ROOT) -> tuple[subprocess.CompletedProcess[str], float]:
    started = time.perf_counter()
    result = subprocess.run(command, cwd=project_root, capture_output=True, text=True, check=False)
    return result, round(time.perf_counter() - started, 6)


def write_invocation_logs(
    logs_dir: Path,
    *,
    input_label: str,
    technology: str,
    repetition: int,
    command: list[str],
    result: subprocess.CompletedProcess[str],
) -> None:
    logs_dir.mkdir(parents=True, exist_ok=True)
    stem = f"{input_label}_{technology}_rep{repetition}"
    (logs_dir / f"{stem}.stdout.log").write_text(result.stdout, encoding="utf-8")
    (logs_dir / f"{stem}.stderr.log").write_text(result.stderr, encoding="utf-8")
    (logs_dir / f"{stem}.command.txt").write_text(" ".join(command) + "\n", encoding="utf-8")


def clear_metrics_file(metrics_path: Path) -> None:
    if metrics_path.exists():
        metrics_path.unlink()


def read_metrics(metrics_path: Path) -> dict[str, Any] | None:
    if not metrics_path.exists():
        return None
    return load_json(metrics_path)


def error_excerpt(text: str, max_chars: int = 3000) -> str:
    text = text.strip()
    if len(text) <= max_chars:
        return text
    return f"{text[:max_chars]}... [truncated]"


def comparable_display_path(path_value: str | Path, *, container_workspace: str = "/workspace") -> str:
    value = str(path_value).replace("\\", "/")
    workspace = container_workspace.rstrip("/")
    for prefix in (f"file://{workspace}/", f"{workspace}/"):
        if value.startswith(prefix):
            return value[len(prefix) :]
    return value


def metrics_input_matches(
    metrics: dict[str, Any],
    benchmark_input: BenchmarkInput,
    *,
    container_workspace: str = "/workspace",
) -> bool:
    actual = metrics.get("input_path")
    if actual is None:
        return False
    return comparable_display_path(actual, container_workspace=container_workspace) == comparable_display_path(
        display_path(benchmark_input.path),
        container_workspace=container_workspace,
    )


def run_id_from_timestamp(timestamp: datetime) -> str:
    return timestamp.strftime("%Y%m%dT%H%M%S%fZ")


def unique_result_path(results_dir: Path, run_id: str) -> tuple[str, Path]:
    candidate_run_id = run_id
    candidate = results_dir / f"benchmark_{candidate_run_id}.csv"
    suffix = 1
    while candidate.exists():
        candidate_run_id = f"{run_id}_{suffix}"
        candidate = results_dir / f"benchmark_{candidate_run_id}.csv"
        suffix += 1
    return candidate_run_id, candidate


def normalize_metrics_rows(
    *,
    run_id: str,
    repetition: int,
    technology: str,
    benchmark_input: BenchmarkInput,
    environment: str,
    execution_setting: str,
    timestamp_utc: str,
    metrics_path: Path,
    metrics: dict[str, Any] | None,
    returncode: int,
    process_duration_seconds: float,
    stderr: str = "",
    container_workspace: str = "/workspace",
) -> list[dict[str, Any]]:
    common = {
        "run_id": run_id,
        "repetition": repetition,
        "technology": technology,
        "input_label": benchmark_input.label,
        "records": benchmark_input.records,
        "environment": environment,
        "execution_setting": execution_setting,
        "timestamp_utc": timestamp_utc,
        "input_path": display_path(benchmark_input.path),
        "metrics_path": display_path(metrics_path),
    }

    if metrics is None:
        return [
            {
                **common,
                "job_name": "__run__",
                "duration_seconds": process_duration_seconds,
                "input_read_seconds": "",
                "plan_build_seconds": "",
                "result_collect_seconds": "",
                "full_output_write_seconds": "",
                "sample_output_write_seconds": "",
                "materialization_mode": "",
                "output_rows": 0,
                "status": "failed",
                "error": error_excerpt(stderr or f"Command exited with code {returncode} before writing metrics."),
                "stage": "metrics_missing",
            }
        ]

    if not metrics_input_matches(metrics, benchmark_input, container_workspace=container_workspace):
        actual = str(metrics.get("input_path", ""))
        expected = display_path(benchmark_input.path)
        return [
            {
                **common,
                "job_name": "__run__",
                "duration_seconds": process_duration_seconds,
                "input_read_seconds": "",
                "plan_build_seconds": "",
                "result_collect_seconds": "",
                "full_output_write_seconds": "",
                "sample_output_write_seconds": "",
                "materialization_mode": "",
                "output_rows": 0,
                "status": "failed",
                "error": f"Metrics input_path mismatch. Expected {expected}; found {actual or '<missing>'}.",
                "stage": "metrics_input_mismatch",
            }
        ]

    jobs = metrics.get("jobs", [])
    if isinstance(jobs, list) and jobs:
        rows = []
        for job in jobs:
            if not isinstance(job, dict):
                continue
            rows.append(
                {
                    **common,
                    "job_name": str(job.get("job_name", "")),
                    "duration_seconds": job.get("duration_seconds", ""),
                    "input_read_seconds": job.get("input_read_seconds", metrics.get("input_read_seconds", "")),
                    "plan_build_seconds": job.get("plan_build_seconds", ""),
                    "result_collect_seconds": job.get("result_collect_seconds", ""),
                    "full_output_write_seconds": job.get("full_output_write_seconds", ""),
                    "sample_output_write_seconds": job.get("sample_output_write_seconds", ""),
                    "materialization_mode": job.get("materialization_mode", ""),
                    "output_rows": job.get("output_rows", 0),
                    "status": str(job.get("status", metrics.get("status", "unknown"))),
                    "error": str(job.get("error", "")),
                    "stage": str(metrics.get("stage", "")),
                }
            )
        return rows

    status = str(metrics.get("status", "failed" if returncode else "unknown"))
    return [
        {
            **common,
            "job_name": "__run__",
            "duration_seconds": process_duration_seconds,
            "input_read_seconds": "",
            "plan_build_seconds": "",
            "result_collect_seconds": "",
            "full_output_write_seconds": "",
            "sample_output_write_seconds": "",
            "materialization_mode": "",
            "output_rows": 0,
            "status": status,
            "error": str(metrics.get("error", "")) or error_excerpt(stderr),
            "stage": str(metrics.get("stage", "")),
        }
    ]


def write_benchmark_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=BENCHMARK_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG, help="YAML config path.")
    parser.add_argument("--environment", default="local", help="Benchmark environment label.")
    parser.add_argument(
        "--technology",
        action="append",
        choices=SUPPORTED_TECHNOLOGIES,
        help="Technology to benchmark. Repeat to select multiple. Defaults to all local technologies.",
    )
    parser.add_argument("--input-label", action="append", help="Benchmark input label to include. Repeatable.")
    parser.add_argument("--include-optional", action="store_true", help="Include validated optional input sizes.")
    parser.add_argument("--results-dir", type=Path, help="Directory for benchmark CSVs and logs.")
    parser.add_argument(
        "--repetitions",
        type=int,
        default=3,
        help="Number of times to run each selected input and technology. Defaults to 3.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.repetitions < 1:
        print("# --repetitions must be at least 1.", file=sys.stderr)
        return 1

    config_path = resolve_project_path(args.config)
    local_config = load_yaml(config_path)
    results_dir = (
        resolve_project_path(args.results_dir)
        if args.results_dir is not None
        else resolve_project_path(str(local_config.get("paths", {}).get("results_dir", "experiments/results/local")))
    )

    input_manifest_path = manifest_path(local_config)
    if not input_manifest_path.exists():
        print(
            f"# Benchmark input manifest was not found: {display_path(input_manifest_path)}. "
            "Run `make generate-sizes` first.",
            file=sys.stderr,
        )
        return 1

    manifest = load_json(input_manifest_path)
    inputs = selected_benchmark_inputs(
        local_config,
        manifest,
        include_optional=args.include_optional,
        labels=args.input_label,
    )
    technologies = args.technology or list(DEFAULT_TECHNOLOGIES)
    execution_setting = str(local_config.get("benchmark", {}).get("execution_setting", args.environment))
    container_workspace = str(local_config.get("benchmark", {}).get("container_workspace", "/workspace"))

    run_started = datetime.now(timezone.utc)
    run_id = run_id_from_timestamp(run_started)
    run_id, result_path = unique_result_path(results_dir, run_id)
    timestamp_utc = run_started.isoformat()
    logs_dir = results_dir / "logs" / run_id
    rows: list[dict[str, Any]] = []
    any_failed = False

    print(f"# Benchmark run {run_id}")
    print(f"# Inputs: {', '.join(item.label for item in inputs)}")
    print(f"# Technologies: {', '.join(technologies)}")
    print(f"# Repetitions: {args.repetitions}")

    for benchmark_input in inputs:
        for technology in technologies:
            for repetition in range(1, args.repetitions + 1):
                spec = build_command(
                    technology,
                    benchmark_input.path,
                    local_config,
                    config_path=config_path,
                    run_id=run_id,
                    input_label=benchmark_input.label,
                )
                print(f"# Running {technology} on {benchmark_input.label} (repetition {repetition}/{args.repetitions})")
                clear_metrics_file(spec.metrics_path)
                result, process_duration_seconds = run_command(spec.command)
                write_invocation_logs(
                    logs_dir,
                    input_label=benchmark_input.label,
                    technology=technology,
                    repetition=repetition,
                    command=spec.command,
                    result=result,
                )
                metrics = read_metrics(spec.metrics_path)
                normalized = normalize_metrics_rows(
                    run_id=run_id,
                    repetition=repetition,
                    technology=technology,
                    benchmark_input=benchmark_input,
                    environment=args.environment,
                    execution_setting=execution_setting,
                    timestamp_utc=timestamp_utc,
                    metrics_path=spec.metrics_path,
                    metrics=metrics,
                    returncode=result.returncode,
                    process_duration_seconds=process_duration_seconds,
                    stderr=result.stderr,
                    container_workspace=container_workspace,
                )
                rows.extend(normalized)
                if result.returncode != 0 or any(row["status"] != "success" for row in normalized):
                    any_failed = True

    latest_path = results_dir / "benchmark_latest.csv"
    write_benchmark_csv(result_path, rows)
    write_benchmark_csv(latest_path, rows)

    print(f"# Benchmark CSV written to: {display_path(result_path)}")
    print(f"# Latest benchmark CSV written to: {display_path(latest_path)}")
    print(f"# Logs written to: {display_path(logs_dir)}")
    return 1 if any_failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
