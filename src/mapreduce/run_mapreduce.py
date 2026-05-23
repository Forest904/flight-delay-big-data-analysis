"""Run the Hadoop Streaming MapReduce analyses."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import pyarrow.dataset as ds
import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.mapreduce.mapreduce_logic import (
    ALL_CAUSES_OUTPUT_COLUMNS,
    CANONICAL_COLUMNS,
    DELAY_OUTPUT_COLUMNS,
    RANKING_OUTPUT_COLUMNS,
    all_causes_output_sort_key,
    delay_output_sort_key,
    ranking_output_sort_key,
)


DEFAULT_CONFIG = PROJECT_ROOT / "config" / "local.yaml"
EXPORT_ROOT = PROJECT_ROOT / "data" / "generated" / "mapreduce_csv"
CONTAINER_WORKSPACE = "/workspace"
MAPREDUCE_LOGIC = PROJECT_ROOT / "src" / "mapreduce" / "mapreduce_logic.py"


@dataclass(frozen=True)
class ExportResult:
    csv_path: Path
    manifest_path: Path
    row_count: int
    reused: bool
    duration_seconds: float


@dataclass(frozen=True)
class JobSpec:
    name: str
    mapper: Path
    reducer: Path
    columns: list[str]
    sort_key: Callable[[list[Any]], Any]


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)
    if not isinstance(data, dict):
        raise ValueError(f"{display_path(path)} did not contain a YAML mapping")
    return data


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-path",
        type=Path,
        help="Prepared Parquet input to analyze. Defaults to the selected config paths.prepared_file.",
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG, help="YAML config path.")
    parser.add_argument(
        "--force-csv-export",
        action="store_true",
        help="Regenerate the canonical MapReduce CSV export even when the manifest matches.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        help="Output root for MapReduce artifacts. Defaults to paths.outputs_dir/mapreduce.",
    )
    parser.add_argument(
        "--reducers",
        type=int,
        default=1,
        help="Number of Hadoop Streaming reducers to request. Defaults to 1 for deterministic local output.",
    )
    return parser.parse_args(argv)


def resolve_project_path(path_value: str | Path) -> Path:
    path = Path(path_value)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path


def display_path(path: Path) -> str:
    try:
        return path.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def project_relative_path(path: Path) -> Path:
    try:
        return path.resolve().relative_to(PROJECT_ROOT.resolve())
    except ValueError as exc:
        raise ValueError(f"Path must be inside the repository for Docker-local MapReduce: {path}") from exc


def container_path(path: Path) -> str:
    return f"{CONTAINER_WORKSPACE}/{project_relative_path(path).as_posix()}"


def container_file_uri(path: Path) -> str:
    return f"file://{container_path(path)}"


def mapreduce_output_root(local_config: dict[str, Any]) -> Path:
    paths = local_config.get("paths", {})
    outputs_dir = resolve_project_path(str(paths.get("outputs_dir", "outputs")))
    return outputs_dir / "mapreduce"


def metrics_file(output_root: Path) -> Path:
    return output_root / "runtime_metrics.json"


def clear_path(path: Path) -> None:
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()


def clear_mapreduce_outputs(output_root: Path) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    for child in output_root.iterdir():
        if child.name == ".gitkeep":
            continue
        clear_path(child)


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


def run_command(command: list[str], timeout_seconds: int | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=timeout_seconds,
    )


def docker_compose_command(*args: str) -> list[str]:
    return [docker_executable(), "compose", *args]


def error_excerpt(error: Exception | str, max_chars: int = 3000) -> str:
    text = str(error)
    if len(text) <= max_chars:
        return text
    return f"{text[:max_chars]}... [truncated]"


def validate_preconditions(prepared_file: Path, output_root: Path) -> list[str]:
    errors: list[str] = []
    if not prepared_file.exists():
        errors.append(
            f"Prepared dataset was not found: {display_path(prepared_file)}. Run `make prepare` or `make generate-sizes` first."
        )
    for path in (prepared_file, output_root):
        try:
            project_relative_path(path)
        except ValueError as exc:
            errors.append(str(exc))
    scripts = [MAPREDUCE_LOGIC, *[path for job in mapreduce_jobs() for path in (job.mapper, job.reducer)]]
    for script in scripts:
        if not script.exists():
            errors.append(f"Required MapReduce script is missing: {display_path(script)}")
    try:
        result = run_command(docker_compose_command("version"), timeout_seconds=30)
    except Exception as exc:
        errors.append(str(exc))
    else:
        if result.returncode != 0:
            errors.append(error_excerpt(result.stderr or result.stdout))
    if not errors:
        try:
            runner_result = run_command(
                docker_compose_command(
                    "run",
                    "--rm",
                    "--no-deps",
                    "--build",
                    "mapreduce-runner",
                    "sh",
                    "-lc",
                    "test -f /opt/hadoop-streaming.jar && /usr/bin/python3 --version && /opt/hadoop/bin/hadoop version >/dev/null",
                ),
                timeout_seconds=180,
            )
        except Exception as exc:
            errors.append(str(exc))
        else:
            if runner_result.returncode != 0:
                errors.append(error_excerpt(runner_result.stderr or runner_result.stdout))
    return errors


def parquet_part_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    parts = sorted(part for part in path.rglob("*.parquet") if part.is_file())
    if not parts:
        raise FileNotFoundError(f"No Parquet part files found under {display_path(path)}")
    return parts


def source_signature(path: Path) -> list[dict[str, Any]]:
    signature = []
    for part in parquet_part_files(path):
        stat = part.stat()
        signature.append(
            {
                "path": display_path(part),
                "size_bytes": stat.st_size,
                "mtime_ns": stat.st_mtime_ns,
            }
        )
    return signature


def input_slug(input_path: Path) -> str:
    name = input_path.name
    if name.endswith(".parquet"):
        name = name[: -len(".parquet")]
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "_", name).strip("._")
    slug = slug or "prepared_input"
    path_hash = hashlib.sha1(display_path(input_path.resolve()).encode("utf-8")).hexdigest()[:10]
    return f"{slug}-{path_hash}"


def export_paths(input_path: Path) -> tuple[Path, Path]:
    export_dir = EXPORT_ROOT / input_slug(input_path)
    return export_dir / "part-00000.csv", export_dir / "manifest.json"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise ValueError(f"{display_path(path)} did not contain a JSON object")
    return data


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def csv_metadata(path: Path) -> dict[str, Any]:
    stat = path.stat()
    return {
        "csv_size_bytes": stat.st_size,
        "csv_sha256": file_sha256(path),
    }


def export_manifest_matches(manifest_path: Path, csv_path: Path, input_path: Path, signature: list[dict[str, Any]]) -> bool:
    if not manifest_path.exists() or not csv_path.exists():
        return False
    try:
        manifest = load_json(manifest_path)
    except Exception:
        return False
    try:
        metadata = csv_metadata(csv_path)
    except Exception:
        return False
    return (
        manifest.get("source_parquet_path") == display_path(input_path)
        and manifest.get("source_signature") == signature
        and manifest.get("canonical_columns") == CANONICAL_COLUMNS
        and manifest.get("csv_path") == display_path(csv_path)
        and manifest.get("status") == "success"
        and int(manifest.get("row_count", -1)) >= 0
        and manifest.get("csv_size_bytes") == metadata["csv_size_bytes"]
        and manifest.get("csv_sha256") == metadata["csv_sha256"]
    )


def csv_value(value: Any) -> Any:
    if value is None:
        return ""
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def write_export_manifest(
    manifest_path: Path,
    *,
    input_path: Path,
    csv_path: Path,
    signature: list[dict[str, Any]],
    row_count: int,
    duration_seconds: float,
    reused: bool,
) -> None:
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_parquet_path": display_path(input_path),
        "csv_path": display_path(csv_path),
        "canonical_columns": CANONICAL_COLUMNS,
        "source_signature": signature,
        **csv_metadata(csv_path),
        "row_count": row_count,
        "duration_seconds": duration_seconds,
        "reused": reused,
        "status": "success",
    }
    manifest_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def export_parquet_to_canonical_csv(input_path: Path, *, force: bool = False) -> ExportResult:
    signature = source_signature(input_path)
    csv_path, manifest_path = export_paths(input_path)
    started = time.perf_counter()

    if not force and export_manifest_matches(manifest_path, csv_path, input_path, signature):
        manifest = load_json(manifest_path)
        return ExportResult(
            csv_path=csv_path,
            manifest_path=manifest_path,
            row_count=int(manifest["row_count"]),
            reused=True,
            duration_seconds=round(time.perf_counter() - started, 6),
        )

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = csv_path.with_suffix(".csv.tmp")
    clear_path(temp_path)
    row_count = 0

    dataset = ds.dataset(str(input_path), format="parquet")
    scanner = dataset.scanner(columns=CANONICAL_COLUMNS, batch_size=65_536)
    with temp_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(CANONICAL_COLUMNS)
        for batch in scanner.to_batches():
            columns = batch.to_pydict()
            for index in range(batch.num_rows):
                writer.writerow([csv_value(columns[column][index]) for column in CANONICAL_COLUMNS])
                row_count += 1

    clear_path(csv_path)
    shutil.move(str(temp_path), str(csv_path))
    duration_seconds = round(time.perf_counter() - started, 6)
    write_export_manifest(
        manifest_path,
        input_path=input_path,
        csv_path=csv_path,
        signature=signature,
        row_count=row_count,
        duration_seconds=duration_seconds,
        reused=False,
    )
    return ExportResult(
        csv_path=csv_path,
        manifest_path=manifest_path,
        row_count=row_count,
        reused=False,
        duration_seconds=duration_seconds,
    )


def mapreduce_jobs() -> list[JobSpec]:
    source_dir = PROJECT_ROOT / "src" / "mapreduce"
    return [
        JobSpec(
            name="delay_by_airport_month",
            mapper=source_dir / "mapper_delay.py",
            reducer=source_dir / "reducer_delay.py",
            columns=DELAY_OUTPUT_COLUMNS,
            sort_key=delay_output_sort_key,
        ),
        JobSpec(
            name="delay_by_airport_month_all_causes",
            mapper=source_dir / "mapper_delay_all_causes.py",
            reducer=source_dir / "reducer_delay_all_causes.py",
            columns=ALL_CAUSES_OUTPUT_COLUMNS,
            sort_key=all_causes_output_sort_key,
        ),
        JobSpec(
            name="airline_airport_ranking",
            mapper=source_dir / "mapper_ranking.py",
            reducer=source_dir / "reducer_ranking.py",
            columns=RANKING_OUTPUT_COLUMNS,
            sort_key=ranking_output_sort_key,
        ),
    ]


def hadoop_streaming_command(job: JobSpec, input_csv: Path, hadoop_output_path: Path, *, reducers: int = 1) -> list[str]:
    localized_files = [job.mapper, job.reducer, MAPREDUCE_LOGIC]
    return docker_compose_command(
        "run",
        "--rm",
        "mapreduce-runner",
        "/opt/hadoop/bin/hadoop",
        "jar",
        "/opt/hadoop-streaming.jar",
        "-D",
        "mapreduce.framework.name=local",
        "-D",
        f"mapreduce.job.reduces={reducers}",
        "-files",
        ",".join(container_file_uri(path) for path in localized_files),
        "-cmdenv",
        f"PYTHONPATH={CONTAINER_WORKSPACE}:{CONTAINER_WORKSPACE}/src/mapreduce",
        "-input",
        container_file_uri(input_csv),
        "-output",
        container_file_uri(hadoop_output_path),
        "-mapper",
        f"python3 {job.mapper.name}",
        "-reducer",
        f"python3 {job.reducer.name}",
    )


def write_invocation_logs(output_root: Path, job_name: str, result: subprocess.CompletedProcess[str], command: list[str]) -> None:
    logs_dir = output_root / ".logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    stem = job_name
    (logs_dir / f"{stem}.stdout.log").write_text(result.stdout, encoding="utf-8")
    (logs_dir / f"{stem}.stderr.log").write_text(result.stderr, encoding="utf-8")
    (logs_dir / f"{stem}.command.txt").write_text(" ".join(command) + "\n", encoding="utf-8")


def hadoop_part_files(output_path: Path) -> list[Path]:
    parts = sorted(path for path in output_path.glob("part-*") if path.is_file())
    if not parts:
        raise FileNotFoundError(f"No Hadoop Streaming part files found under {display_path(output_path)}")
    return parts


def read_json_rows(output_path: Path) -> list[list[Any]]:
    rows: list[list[Any]] = []
    for part in hadoop_part_files(output_path):
        with part.open("r", encoding="utf-8") as file:
            for line in file:
                text = line.strip()
                if not text:
                    continue
                row = json.loads(text)
                if not isinstance(row, list):
                    raise ValueError(f"MapReduce reducer emitted a non-list row: {text}")
                rows.append(row)
    return rows


def write_rows_csv(path: Path, columns: list[str], rows: list[list[Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(columns)
        writer.writerows(rows)


def write_outputs(rows: list[list[Any]], columns: list[str], full_output_path: Path, sample_output_path: Path) -> None:
    clear_path(full_output_path)
    full_output_path.mkdir(parents=True, exist_ok=True)
    write_rows_csv(full_output_path / "part-00000.csv", columns, rows)
    write_rows_csv(sample_output_path, columns, rows[:10])


def run_analysis(job: JobSpec, input_csv: Path, output_root: Path, *, reducers: int = 1) -> dict[str, Any]:
    started = time.perf_counter()
    status = "success"
    error: str | None = None
    output_rows = 0
    hadoop_root = output_root / ".tmp_hadoop"
    hadoop_output_path = hadoop_root / job.name
    full_output_path = output_root / job.name / "full"
    sample_output_path = output_root / job.name / "first_10.csv"
    command = hadoop_streaming_command(job, input_csv, hadoop_output_path, reducers=reducers)

    try:
        clear_path(hadoop_output_path)
        hadoop_root.mkdir(parents=True, exist_ok=True)
        result = run_command(command)
        write_invocation_logs(output_root, job.name, result, command)
        if result.returncode != 0:
            raise RuntimeError(
                "Hadoop Streaming command failed with exit code "
                f"{result.returncode}: {error_excerpt(result.stderr or result.stdout)}"
            )
        rows = read_json_rows(hadoop_output_path)
        rows.sort(key=job.sort_key)
        output_rows = len(rows)
        write_outputs(rows, job.columns, full_output_path, sample_output_path)
    except Exception as exc:
        status = "failed"
        error = error_excerpt(exc)
    finally:
        duration_seconds = round(time.perf_counter() - started, 6)

    metrics: dict[str, Any] = {
        "job_name": job.name,
        "duration_seconds": duration_seconds,
        "output_rows": output_rows,
        "full_output_path": display_path(full_output_path),
        "sample_output_path": display_path(sample_output_path),
        "hadoop_output_path": display_path(hadoop_output_path),
        "reducers": reducers,
        "status": status,
    }
    if error is not None:
        metrics["error"] = error
    return metrics


def write_metrics(metrics: dict[str, Any], output_root: Path) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    metrics_file(output_root).write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def print_metrics(metrics: dict[str, Any], output_root: Path) -> None:
    print("# MapReduce Runtime Metrics")
    print(json.dumps(metrics, indent=2, sort_keys=True))
    print(f"MapReduce outputs written to: {display_path(output_root)}")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    config_path = args.config if args.config.is_absolute() else PROJECT_ROOT / args.config
    local_config = load_yaml(config_path)
    paths = local_config.get("paths", {})
    prepared_file_value = paths.get("prepared_file")
    if not prepared_file_value:
        raise ValueError(f"{display_path(config_path)} does not define paths.prepared_file")

    prepared_file = args.input_path if args.input_path is not None else Path(str(prepared_file_value))
    if not prepared_file.is_absolute():
        prepared_file = PROJECT_ROOT / prepared_file
    if args.reducers < 1:
        raise ValueError("--reducers must be at least 1")
    output_root = resolve_project_path(args.output_root) if args.output_root is not None else mapreduce_output_root(local_config)
    run_metrics: dict[str, Any] = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "technology": "mapreduce",
        "status": "running",
        "stage": "preflight",
        "input_path": display_path(prepared_file),
        "hadoop_streaming_mode": "docker-compose local MapReduce",
        "output_root": display_path(output_root),
        "reducers": args.reducers,
        "jobs": [],
    }

    preflight_errors = validate_preconditions(prepared_file, output_root)
    if preflight_errors:
        print("# MapReduce preflight failed", file=sys.stderr)
        for error in preflight_errors:
            print(f"- {error}", file=sys.stderr)
        run_metrics["status"] = "failed"
        run_metrics["error"] = "; ".join(preflight_errors)
        run_metrics["stage"] = "preflight"
        write_metrics(run_metrics, output_root)
        print_metrics(run_metrics, output_root)
        return 1

    try:
        run_metrics["stage"] = "csv_export"
        write_metrics(run_metrics, output_root)
        export = export_parquet_to_canonical_csv(prepared_file, force=args.force_csv_export)
        run_metrics["csv_export"] = {
            "csv_path": display_path(export.csv_path),
            "manifest_path": display_path(export.manifest_path),
            "row_count": export.row_count,
            "reused": export.reused,
            "duration_seconds": export.duration_seconds,
        }

        clear_mapreduce_outputs(output_root)
        run_metrics["stage"] = "analysis"
        run_metrics["status"] = "running"
        write_metrics(run_metrics, output_root)

        for job in mapreduce_jobs():
            run_metrics["stage"] = f"job:{job.name}"
            job_metrics = run_analysis(job, export.csv_path, output_root, reducers=args.reducers)
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
        run_metrics["status"] = "failed"
        run_metrics["error"] = error_excerpt(exc)

    write_metrics(run_metrics, output_root)
    print_metrics(run_metrics, output_root)
    return 0 if run_metrics["status"] == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())
