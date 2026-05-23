"""Upload and run the AWS EMR benchmark lane.

The script is intentionally dry-run friendly: every AWS-mutating operation has
an equivalent printed action so command construction can be unit tested before
spending Learner Lab budget.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.run_benchmarks import BENCHMARK_COLUMNS, write_benchmark_csv
from src.common.uri import is_s3_uri, join_uri, parse_s3_uri


DEFAULT_CONFIG = PROJECT_ROOT / "config" / "aws_emr.yaml"
DEFAULT_ENV_FILE = PROJECT_ROOT / ".env"
DEFAULT_STATE_NAME = "aws_emr_state.json"
TERMINAL_STEP_STATES = {"COMPLETED", "CANCELLED", "FAILED", "INTERRUPTED"}
SUCCESS_STEP_STATES = {"COMPLETED"}
TERMINAL_CLUSTER_STATES = {"TERMINATED", "TERMINATED_WITH_ERRORS"}
ACTIVE_CLUSTER_STATES = {"STARTING", "BOOTSTRAPPING", "RUNNING", "WAITING"}
AWS_PROJECT_ENVIRONMENTS = {"aws-emr", "aws-emr-larger"}
STEP_TIMING_COLUMNS = [
    "run_id",
    "cluster_id",
    "step_id",
    "step_name",
    "step_kind",
    "technology",
    "input_label",
    "repetition",
    "step_state",
    "submitted_at_utc",
    "started_at_utc",
    "ended_at_utc",
    "wall_clock_seconds",
    "failure_reason",
    "metrics_s3_uri",
]


@dataclass(frozen=True)
class AwsContext:
    config: dict[str, Any]
    bucket: str
    prefix: str
    region: str
    results_dir: Path


@dataclass(frozen=True)
class BenchmarkStep:
    input_label: str
    records: int
    technology: str
    repetition: int
    input_s3_uri: str
    output_root_s3_uri: str
    input_kind: str = ""
    synthetic_input: bool = False
    source_input_label: str = ""
    stress_variant_factor: int | str = ""


@dataclass(frozen=True)
class CodeUpload:
    source_uri: str
    runtime_config_uri: str
    source_sha256: str
    runtime_config_sha256: str


@dataclass(frozen=True)
class StepTiming:
    run_id: str
    cluster_id: str
    step_id: str
    step_name: str
    step_kind: str
    technology: str = ""
    input_label: str = ""
    repetition: int | str = ""
    step_state: str = ""
    submitted_at_utc: str = ""
    started_at_utc: str = ""
    ended_at_utc: str = ""
    wall_clock_seconds: float | str = ""
    failure_reason: str = ""
    metrics_s3_uri: str = ""


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)
    if not isinstance(data, dict):
        raise ValueError(f"{path} did not contain a YAML mapping")
    return data


def load_env_file(path: Path, *, override: bool = False) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and (override or key not in os.environ):
            os.environ[key] = value


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise ValueError(f"{path} did not contain a JSON object")
    return data


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def isoformat_utc(value: datetime | None = None) -> str:
    return (value or utc_now()).astimezone(timezone.utc).isoformat()


def datetime_to_iso(value: Any) -> str:
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat()
    return ""


def seconds_between(start: str, end: str) -> float | str:
    if not start or not end:
        return ""
    try:
        started = datetime.fromisoformat(start.replace("Z", "+00:00"))
        ended = datetime.fromisoformat(end.replace("Z", "+00:00"))
    except ValueError:
        return ""
    return round((ended - started).total_seconds(), 3)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_output(*args: str) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except Exception:
        return ""
    return result.stdout.strip()


def git_commit() -> str:
    return git_output("rev-parse", "HEAD")


def git_status_short() -> str:
    return git_output("status", "--short")


def run_id_from_timestamp(timestamp: datetime) -> str:
    return timestamp.strftime("%Y%m%dT%H%M%S%fZ")


def resolve_results_dir(config: dict[str, Any]) -> Path:
    configured = Path(str(config.get("paths", {}).get("results_dir", "experiments/results/aws-emr")))
    return configured if configured.is_absolute() else PROJECT_ROOT / configured


def context_from_config(config: dict[str, Any]) -> AwsContext:
    bucket_env = str(config.get("s3", {}).get("bucket_env", "AWS_FLIGHT_DELAY_BUCKET"))
    bucket = os.environ.get(bucket_env, "").strip()
    if not bucket:
        raise ValueError(f"Set {bucket_env} to the project S3 bucket name.")
    prefix = str(config.get("s3", {}).get("prefix", "flight-delay")).strip("/")
    region = os.environ.get("AWS_DEFAULT_REGION") or os.environ.get("AWS_REGION") or str(config.get("aws", {}).get("region", "us-east-1"))
    return AwsContext(config=config, bucket=bucket, prefix=prefix, region=region, results_dir=resolve_results_dir(config))


def configured_environment(config: dict[str, Any]) -> str:
    return str(config.get("environment", "aws-emr") or "aws-emr")


def s3_uri(ctx: AwsContext, *parts: str) -> str:
    return join_uri(f"s3://{ctx.bucket}/{ctx.prefix}", *parts)


def s3_key(ctx: AwsContext, *parts: str) -> str:
    return "/".join([ctx.prefix, *(part.strip("/") for part in parts if part.strip("/"))])


def benchmark_canonical_run_id(config: dict[str, Any]) -> str:
    return str(config.get("benchmark", {}).get("canonical_run_id", "")).strip()


def dependency_pins(config: dict[str, Any]) -> list[str]:
    pins = config.get("aws", {}).get("dependencies", [])
    if not isinstance(pins, list) or not pins:
        return ["PyYAML==6.0.3", "pandas==3.0.3", "pyarrow==24.0.0", "boto3==1.43.12"]
    return [str(pin).strip() for pin in pins if str(pin).strip()]


def timeout_seconds(config: dict[str, Any], key: str, default: int) -> int:
    value = config.get("aws", {}).get("timeouts", {}).get(key, default)
    return max(1, int(value))


def cluster_profile(config: dict[str, Any]) -> dict[str, Any]:
    return dict(config.get("emr", {}).get("cluster_profile", {}))


def cluster_node_count(config: dict[str, Any]) -> int:
    profile = cluster_profile(config)
    return int(profile.get("primary_nodes", 1)) + int(profile.get("core_nodes", 2))


def cluster_instance_type(config: dict[str, Any]) -> str:
    emr_config = config.get("emr", {})
    profile = cluster_profile(config)
    fallback = emr_config.get("instance_type_fallback_order", ["m5.xlarge"])
    return str(profile.get("instance_type") or fallback[0])


def data_s3_key_for_entry(ctx: AwsContext, entry: dict[str, Any]) -> str:
    local_name = Path(str(entry["local_path"]).rstrip("/")).name
    area = "prepared" if str(entry.get("method", "")) == "prepared_reference" else "generated"
    return s3_key(ctx, "data", area, local_name)


def data_s3_uri_for_entry(ctx: AwsContext, entry: dict[str, Any]) -> str:
    return f"s3://{ctx.bucket}/{data_s3_key_for_entry(ctx, entry)}"


def local_manifest_path(config: dict[str, Any]) -> Path:
    generated_dir = Path(str(config.get("paths", {}).get("generated_dir", "data/generated")))
    if not generated_dir.is_absolute():
        generated_dir = PROJECT_ROOT / generated_dir
    return generated_dir / "input_size_manifest.json"


def manifest_records_by_label(manifest: dict[str, Any]) -> dict[str, int]:
    records: dict[str, int] = {}
    for entry in manifest.get("datasets", []):
        if isinstance(entry, dict) and entry.get("validation_status") == "success":
            records[str(entry.get("label"))] = int(entry.get("actual_records", entry.get("target_records", 0)))
    return records


def manifest_entries_by_label(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    entries: dict[str, dict[str, Any]] = {}
    for entry in manifest.get("datasets", []):
        if isinstance(entry, dict) and entry.get("validation_status") == "success":
            entries[str(entry.get("label"))] = entry
    return entries


def configured_inputs(config: dict[str, Any], manifest: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    entries = config.get("benchmark", {}).get("input_sizes", [])
    if not isinstance(entries, list):
        raise ValueError("benchmark.input_sizes must be a list")
    manifest_records = manifest_records_by_label(manifest or {})
    manifest_entries = manifest_entries_by_label(manifest or {})
    normalized: list[dict[str, Any]] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        copied = dict(entry)
        label = str(copied["label"])
        if label in manifest_records:
            copied["records"] = manifest_records[label]
        if label in manifest_entries:
            manifest_entry = manifest_entries[label]
            for source_key, target_key in (
                ("input_kind", "input_kind"),
                ("synthetic_input", "synthetic_input"),
                ("source_input_label", "source_input_label"),
                ("variant_factor", "stress_variant_factor"),
            ):
                if source_key in manifest_entry:
                    copied[target_key] = manifest_entry[source_key]
        normalized.append(copied)
    return normalized


def repetition_count(entry: dict[str, Any]) -> int:
    repetitions = int(entry.get("repetitions", 1))
    if str(entry.get("label")) == "14m":
        override = os.environ.get("AWS_EMR_14M_REPETITIONS")
        if override:
            repetitions = int(override)
        repetitions = min(repetitions, int(entry.get("max_repetitions", repetitions)))
    return max(1, repetitions)


def expand_benchmark_steps(ctx: AwsContext, run_id: str, manifest: dict[str, Any]) -> list[BenchmarkStep]:
    technologies = [str(item) for item in ctx.config.get("benchmark", {}).get("technologies", ["spark_sql", "spark_core"])]
    steps: list[BenchmarkStep] = []
    for entry in configured_inputs(ctx.config, manifest):
        label = str(entry["label"])
        records = int(entry["records"])
        input_s3_uri = data_s3_uri_for_entry(ctx, entry)
        for technology in technologies:
            for repetition in range(1, repetition_count(entry) + 1):
                output_root = s3_uri(ctx, "results", "runs", run_id, "outputs", label, technology, f"rep{repetition}", technology)
                steps.append(
                    BenchmarkStep(
                        input_label=label,
                        records=records,
                        technology=technology,
                        repetition=repetition,
                        input_s3_uri=input_s3_uri,
                        output_root_s3_uri=output_root,
                        input_kind=str(entry.get("input_kind", "")),
                        synthetic_input=bool(entry.get("synthetic_input", False)),
                        source_input_label=str(entry.get("source_input_label", "")),
                        stress_variant_factor=entry.get("stress_variant_factor", ""),
                    )
                )
    return steps


def smoke_steps(steps: list[BenchmarkStep]) -> list[BenchmarkStep]:
    return [step for step in steps if step.input_label == "100k" and step.repetition == 1]


def non_smoke_steps(steps: list[BenchmarkStep]) -> list[BenchmarkStep]:
    smoke = set(smoke_steps(steps))
    return [step for step in steps if step not in smoke]


def runtime_config(ctx: AwsContext, run_id: str) -> dict[str, Any]:
    config = dict(ctx.config)
    config["environment"] = configured_environment(ctx.config)
    config["paths"] = dict(config.get("paths", {}))
    config["paths"]["outputs_dir"] = s3_uri(ctx, "results", "runs", run_id, "outputs")
    config["paths"]["results_dir"] = str(ctx.results_dir.relative_to(PROJECT_ROOT))
    config["spark"] = dict(config.get("spark", {}))
    config["spark"]["master"] = "yarn"
    config["spark"].setdefault("app_name", "flight-delay-big-data-analysis-aws-emr")
    return config


def build_source_bundle(output_path: Path) -> Path:
    include_roots = ["src", "config", "experiments"]
    include_files = ["requirements.txt", "README.md"]
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for root_name in include_roots:
            root = PROJECT_ROOT / root_name
            if not root.exists():
                continue
            for path in root.rglob("*"):
                if path.is_file() and "__pycache__" not in path.parts:
                    archive.write(path, path.relative_to(PROJECT_ROOT).as_posix())
        for file_name in include_files:
            path = PROJECT_ROOT / file_name
            if path.exists():
                archive.write(path, path.relative_to(PROJECT_ROOT).as_posix())
    return output_path


def boto3_session(ctx: AwsContext) -> Any:
    import boto3

    return boto3.Session(region_name=ctx.region)


def ensure_bucket(ctx: AwsContext, *, dry_run: bool) -> None:
    if dry_run:
        print(f"DRY-RUN create bucket if missing: s3://{ctx.bucket} ({ctx.region})")
        return
    s3 = boto3_session(ctx).client("s3")
    try:
        s3.head_bucket(Bucket=ctx.bucket)
        return
    except Exception:
        pass
    if ctx.region == "us-east-1":
        s3.create_bucket(Bucket=ctx.bucket)
    else:
        s3.create_bucket(Bucket=ctx.bucket, CreateBucketConfiguration={"LocationConstraint": ctx.region})


def upload_file(ctx: AwsContext, local_path: Path, key: str, *, dry_run: bool) -> None:
    if dry_run:
        print(f"DRY-RUN upload file: {local_path.relative_to(PROJECT_ROOT) if local_path.is_relative_to(PROJECT_ROOT) else local_path} -> s3://{ctx.bucket}/{key}")
        return
    boto3_session(ctx).client("s3").upload_file(str(local_path), ctx.bucket, key)


def upload_directory(ctx: AwsContext, local_dir: Path, key_prefix: str, *, dry_run: bool) -> None:
    if not local_dir.exists():
        raise FileNotFoundError(f"Missing dataset directory: {local_dir}")
    for path in local_dir.rglob("*"):
        if not path.is_file() or path.name.endswith(".crc") or path.name == ".gitkeep":
            continue
        relative = path.relative_to(local_dir).as_posix()
        upload_file(ctx, path, f"{key_prefix.rstrip('/')}/{relative}", dry_run=dry_run)


def upload_data(ctx: AwsContext, manifest: dict[str, Any], *, dry_run: bool) -> None:
    for entry in configured_inputs(ctx.config, manifest):
        local_path = Path(str(entry["local_path"]))
        if not local_path.is_absolute():
            local_path = PROJECT_ROOT / local_path
        upload_directory(ctx, local_path, data_s3_key_for_entry(ctx, entry), dry_run=dry_run)
    upload_file(ctx, local_manifest_path(ctx.config), s3_key(ctx, "data", "generated", "input_size_manifest.json"), dry_run=dry_run)


def upload_code(ctx: AwsContext, run_id: str, *, dry_run: bool) -> CodeUpload:
    source_key = s3_key(ctx, "code", "runs", run_id, "source.zip")
    runtime_key = s3_key(ctx, "code", "runs", run_id, "aws_emr_runtime.yaml")
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        source_zip = build_source_bundle(temp_path / "source.zip")
        runtime_yaml = temp_path / "aws_emr_runtime.yaml"
        runtime_yaml.write_text(yaml.safe_dump(runtime_config(ctx, run_id), sort_keys=False), encoding="utf-8")
        source_sha256 = sha256_file(source_zip)
        runtime_sha256 = sha256_file(runtime_yaml)
        upload_file(ctx, source_zip, source_key, dry_run=dry_run)
        upload_file(ctx, runtime_yaml, runtime_key, dry_run=dry_run)
    return CodeUpload(
        source_uri=f"s3://{ctx.bucket}/{source_key}",
        runtime_config_uri=f"s3://{ctx.bucket}/{runtime_key}",
        source_sha256=source_sha256,
        runtime_config_sha256=runtime_sha256,
    )


def dependency_step(config: dict[str, Any]) -> dict[str, Any]:
    pins = " ".join(dependency_pins(config))
    return {
        "Name": "Install Python benchmark dependencies",
        "ActionOnFailure": "CANCEL_AND_WAIT",
        "HadoopJarStep": {
            "Jar": "command-runner.jar",
            "Args": ["bash", "-lc", f"python3 -m pip install --user {pins} && python3 -m pip freeze | tee /tmp/flight-delay-emr-pip-freeze.txt"],
        },
    }


def build_spark_step(step: BenchmarkStep, *, run_id: str, source_uri: str, runtime_config_uri: str) -> dict[str, Any]:
    script = {
        "spark_sql": "src/spark_sql/run_spark_sql.py",
        "spark_core": "src/spark_core/run_spark_core.py",
    }[step.technology]
    work_dir = f"/mnt/var/lib/hadoop/flight-delay-{run_id}"
    command = " && ".join(
        [
            f"mkdir -p {work_dir}",
            f"aws s3 cp {source_uri} {work_dir}/source.zip",
            f"aws s3 cp {runtime_config_uri} {work_dir}/aws_emr_runtime.yaml",
            f"rm -rf {work_dir}/source",
            f"unzip -oq {work_dir}/source.zip -d {work_dir}/source",
            f"cd {work_dir}/source",
            (
                "spark-submit --master yarn --deploy-mode client "
                "--conf spark.pyspark.python=python3 "
                "--conf spark.pyspark.driver.python=python3 "
                f"--py-files {work_dir}/source.zip "
                f"{script} "
                f"--config {work_dir}/aws_emr_runtime.yaml "
                f"--input-path {step.input_s3_uri} "
                f"--output-root {step.output_root_s3_uri}"
            ),
        ]
    )
    return {
        "Name": f"{step.technology} {step.input_label} rep{step.repetition}",
        "ActionOnFailure": "CANCEL_AND_WAIT",
        "HadoopJarStep": {"Jar": "command-runner.jar", "Args": ["bash", "-lc", command]},
    }


def metric_uri_for_step(step: BenchmarkStep) -> str:
    return join_uri(step.output_root_s3_uri, "runtime_metrics.json")


def ordered_benchmark_row(row: dict[str, Any]) -> dict[str, Any]:
    return {column: row.get(column, "") for column in BENCHMARK_COLUMNS}


def read_s3_json(ctx: AwsContext, uri: str) -> dict[str, Any] | None:
    bucket, key = parse_s3_uri(uri)
    try:
        response = boto3_session(ctx).client("s3").get_object(Bucket=bucket, Key=key)
    except Exception:
        return None
    return json.loads(response["Body"].read().decode("utf-8"))


def require_s3_json(ctx: AwsContext, uri: str) -> dict[str, Any]:
    data = read_s3_json(ctx, uri)
    if data is None:
        raise RuntimeError(f"Missing required runtime metrics JSON: {uri}")
    return data


def s3_prefix_contains_parquet(ctx: AwsContext, uri: str) -> bool:
    bucket, key = parse_s3_uri(uri.rstrip("/") + "/")
    s3 = boto3_session(ctx).client("s3")
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix=key):
        for item in page.get("Contents", []):
            name = str(item.get("Key", ""))
            if name.endswith(".parquet") or "/part-" in name:
                return True
    return False


def validate_uploaded_inputs(ctx: AwsContext, steps: list[BenchmarkStep], *, dry_run: bool) -> None:
    unique_inputs = sorted({step.input_s3_uri for step in steps})
    if dry_run:
        for uri in unique_inputs:
            print(f"DRY-RUN validate input prefix contains Parquet data: {uri}")
        return
    missing = [uri for uri in unique_inputs if not s3_prefix_contains_parquet(ctx, uri)]
    if missing:
        formatted = "\n".join(f"- {uri}" for uri in missing)
        raise RuntimeError(f"Uploaded EMR input prefix has no Parquet data:\n{formatted}")


def normalize_step_rows(
    step: BenchmarkStep,
    *,
    run_id: str,
    timestamp_utc: str,
    execution_setting: str,
    metrics: dict[str, Any] | None,
    step_state: str,
    environment: str = "aws-emr",
    failure_reason: str = "",
) -> list[dict[str, Any]]:
    common = {
        "run_id": run_id,
        "repetition": step.repetition,
        "technology": step.technology,
        "input_label": step.input_label,
        "records": step.records,
        "input_kind": step.input_kind,
        "synthetic_input": step.synthetic_input,
        "source_input_label": step.source_input_label,
        "stress_variant_factor": step.stress_variant_factor,
        "environment": environment,
        "execution_setting": execution_setting,
        "timestamp_utc": timestamp_utc,
        "input_path": step.input_s3_uri,
        "metrics_path": metric_uri_for_step(step),
    }
    if not metrics:
        return [
            ordered_benchmark_row({
                **common,
                "job_name": "__run__",
                "duration_seconds": "",
                "input_read_seconds": "",
                "plan_build_seconds": "",
                "result_collect_seconds": "",
                "full_output_write_seconds": "",
                "sample_output_write_seconds": "",
                "materialization_mode": "",
                "output_rows": 0,
                "status": "success" if step_state in SUCCESS_STEP_STATES else "failed",
                "error": failure_reason,
                "stage": f"emr_step:{step_state.lower()}",
            })
        ]

    rows = []
    for job in metrics.get("jobs", []):
        if isinstance(job, dict):
            rows.append(
                ordered_benchmark_row({
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
                })
            )
    return rows or [
        ordered_benchmark_row({
            **common,
            "job_name": "__run__",
            "duration_seconds": "",
            "input_read_seconds": "",
            "plan_build_seconds": "",
            "result_collect_seconds": "",
            "full_output_write_seconds": "",
            "sample_output_write_seconds": "",
            "materialization_mode": "",
            "output_rows": 0,
            "status": str(metrics.get("status", "unknown")),
            "error": str(metrics.get("error", failure_reason)),
            "stage": str(metrics.get("stage", f"emr_step:{step_state.lower()}")),
        })
    ]


def write_state(ctx: AwsContext, state: dict[str, Any], *, dry_run: bool) -> None:
    if dry_run:
        print(f"DRY-RUN write state: {state}")
        return
    ctx.results_dir.mkdir(parents=True, exist_ok=True)
    (ctx.results_dir / DEFAULT_STATE_NAME).write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_state(ctx: AwsContext) -> dict[str, Any]:
    path = ctx.results_dir / DEFAULT_STATE_NAME
    return load_json(path) if path.exists() else {}


def run_manifest(
    ctx: AwsContext,
    *,
    run_id: str,
    run_kind: str,
    code_upload: CodeUpload,
    config_path: Path = DEFAULT_CONFIG,
    cluster_id: str = "",
    status: str = "running",
    notes: str = "",
) -> dict[str, Any]:
    emr_config = ctx.config.get("emr", {})
    profile = cluster_profile(ctx.config)
    budget = ctx.config.get("aws", {}).get("budget", {})
    budget_env_name = str(budget.get("remaining_budget_env", "AWS_LEARNER_LAB_BUDGET_REMAINING_USD"))
    status_short = git_status_short()
    canonical_run_id = benchmark_canonical_run_id(ctx.config)
    return {
        "run_id": run_id,
        "run_kind": run_kind,
        "status": status,
        "notes": notes,
        "canonical_run_id": canonical_run_id,
        "is_canonical_full_run": run_id == canonical_run_id,
        "generated_at_utc": isoformat_utc(),
        "git": {
            "commit": git_commit(),
            "dirty": bool(status_short),
            "status_short": status_short,
        },
        "artifacts": {
            "source_bundle_s3_uri": code_upload.source_uri,
            "source_bundle_sha256": code_upload.source_sha256,
            "runtime_config_s3_uri": code_upload.runtime_config_uri,
            "runtime_config_sha256": code_upload.runtime_config_sha256,
            "config_path": str(config_path.relative_to(PROJECT_ROOT) if config_path.is_absolute() and config_path.is_relative_to(PROJECT_ROOT) else config_path),
            "config_sha256": sha256_file(config_path) if config_path.exists() else "",
        },
        "aws": {
            "bucket": ctx.bucket,
            "prefix": ctx.prefix,
            "region": ctx.region,
            "cluster_id": cluster_id,
            "emr_release": str(emr_config.get("release_label") or emr_config.get("release_label_fallback", "")),
            "instance_type": cluster_instance_type(ctx.config),
            "primary_nodes": int(profile.get("primary_nodes", 1)),
            "core_nodes": int(profile.get("core_nodes", 2)),
            "node_count": cluster_node_count(ctx.config),
            "service_role": str(emr_config.get("iam_role_candidates", {}).get("service_role", [""])[0]),
            "ec2_instance_profile": str(emr_config.get("iam_role_candidates", {}).get("ec2_instance_profile", [""])[0]),
            "idle_timeout_seconds": int(profile.get("idle_timeout_seconds", 0) or 0),
            "timeouts": dict(ctx.config.get("aws", {}).get("timeouts", {})),
            "budget_env_name": budget_env_name,
            "budget_env_value": os.environ.get(budget_env_name, ""),
        },
        "python_dependencies": dependency_pins(ctx.config),
    }


def write_run_manifest(ctx: AwsContext, run_id: str, manifest: dict[str, Any], *, dry_run: bool) -> Path:
    path = ctx.results_dir / f"run_manifest_{run_id}.json"
    if dry_run:
        print(f"DRY-RUN write run manifest: {path.relative_to(PROJECT_ROOT)}")
        return path
    ctx.results_dir.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    upload_file(ctx, path, s3_key(ctx, "results", "runs", run_id, f"run_manifest_{run_id}.json"), dry_run=False)
    return path


def write_step_timing(ctx: AwsContext, run_id: str, rows: list[StepTiming], *, dry_run: bool) -> Path:
    path = ctx.results_dir / f"step_timing_{run_id}.csv"
    if dry_run:
        print(f"DRY-RUN write step timing CSV: {path.relative_to(PROJECT_ROOT)} ({len(rows)} rows)")
        return path
    ctx.results_dir.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=STEP_TIMING_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: asdict(row).get(column, "") for column in STEP_TIMING_COLUMNS})
    upload_file(ctx, path, s3_key(ctx, "results", "runs", run_id, f"step_timing_{run_id}.csv"), dry_run=False)
    return path


def create_cluster(ctx: AwsContext, run_id: str, *, dry_run: bool) -> str:
    emr_config = ctx.config.get("emr", {})
    profile = cluster_profile(ctx.config)
    release_label = str(emr_config.get("release_label") or emr_config.get("release_label_fallback", "emr-7.13.0"))
    instance_type = cluster_instance_type(ctx.config)
    primary_nodes = int(profile.get("primary_nodes", 1))
    core_nodes = int(profile.get("core_nodes", 2))
    environment = configured_environment(ctx.config)
    service_role = str(emr_config.get("iam_role_candidates", {}).get("service_role", ["EMR_DefaultRole"])[0])
    job_flow_role = str(emr_config.get("iam_role_candidates", {}).get("ec2_instance_profile", ["EMR_EC2_DefaultRole"])[0])
    cluster_args = {
        "Name": f"flight-delay-aws-emr-{run_id}",
        "ReleaseLabel": release_label,
        "Applications": [{"Name": name} for name in emr_config.get("applications", ["Spark"])],
        "LogUri": s3_uri(ctx, "logs", "emr", run_id, ""),
        "Instances": {
            "KeepJobFlowAliveWhenNoSteps": True,
            "TerminationProtected": False,
            "InstanceGroups": [
                {"Name": "Primary", "Market": "ON_DEMAND", "InstanceRole": "MASTER", "InstanceType": instance_type, "InstanceCount": primary_nodes},
                {"Name": "Core", "Market": "ON_DEMAND", "InstanceRole": "CORE", "InstanceType": instance_type, "InstanceCount": core_nodes},
            ],
        },
        "ServiceRole": service_role,
        "JobFlowRole": job_flow_role,
        "VisibleToAllUsers": True,
        "Tags": [
            {"Key": "Project", "Value": "flight-delay-big-data-analysis"},
            {"Key": "Environment", "Value": environment},
            {"Key": "RunId", "Value": run_id},
        ],
    }
    idle_timeout = int(profile.get("idle_timeout_seconds", 0) or 0)
    if idle_timeout > 0:
        cluster_args["AutoTerminationPolicy"] = {"IdleTimeout": idle_timeout}
    if dry_run:
        print("DRY-RUN create EMR cluster:")
        print(json.dumps(cluster_args, indent=2, sort_keys=True))
        return f"dry-run-{run_id}"
    response = boto3_session(ctx).client("emr").run_job_flow(**cluster_args)
    return str(response["JobFlowId"])


def wait_for_cluster(ctx: AwsContext, cluster_id: str) -> None:
    emr = boto3_session(ctx).client("emr")
    deadline = time.monotonic() + timeout_seconds(ctx.config, "cluster_startup_seconds", 900)
    while True:
        state = emr.describe_cluster(ClusterId=cluster_id)["Cluster"]["Status"]["State"]
        if state in {"WAITING", "RUNNING"}:
            return
        if state in TERMINAL_CLUSTER_STATES:
            raise RuntimeError(f"Cluster {cluster_id} reached terminal state {state}")
        if time.monotonic() > deadline:
            raise TimeoutError(f"Cluster {cluster_id} did not become ready within configured startup timeout")
        time.sleep(30)


def submit_and_wait_step(
    ctx: AwsContext,
    cluster_id: str,
    step_spec: dict[str, Any],
    *,
    dry_run: bool,
    run_id: str,
    step_kind: str,
    benchmark_step: BenchmarkStep | None = None,
) -> StepTiming:
    submitted_at = isoformat_utc()
    if dry_run:
        print("DRY-RUN submit EMR step:")
        print(json.dumps(step_spec, indent=2, sort_keys=True))
        return StepTiming(
            run_id=run_id,
            cluster_id=cluster_id,
            step_id=f"dry-run-{step_kind}",
            step_name=str(step_spec.get("Name", step_kind)),
            step_kind=step_kind,
            technology=benchmark_step.technology if benchmark_step else "",
            input_label=benchmark_step.input_label if benchmark_step else "",
            repetition=benchmark_step.repetition if benchmark_step else "",
            step_state="COMPLETED",
            submitted_at_utc=submitted_at,
            started_at_utc=submitted_at,
            ended_at_utc=submitted_at,
            wall_clock_seconds=0.0,
            metrics_s3_uri=metric_uri_for_step(benchmark_step) if benchmark_step else "",
        )
    emr = boto3_session(ctx).client("emr")
    step_id = emr.add_job_flow_steps(JobFlowId=cluster_id, Steps=[step_spec])["StepIds"][0]
    deadline = time.monotonic() + timeout_seconds(ctx.config, "step_seconds", 1800)
    while True:
        step = emr.describe_step(ClusterId=cluster_id, StepId=step_id)["Step"]
        status = step["Status"]
        state = status["State"]
        if state in TERMINAL_STEP_STATES:
            details = status.get("FailureDetails", {})
            failure = str(details.get("Message") or details.get("Reason") or status.get("StateChangeReason", {}).get("Message", ""))
            log_file = str(details.get("LogFile", ""))
            if log_file:
                failure = f"{failure} (logs: {log_file})" if failure else f"logs: {log_file}"
            timeline = status.get("Timeline", {})
            started_at = datetime_to_iso(timeline.get("StartDateTime")) or submitted_at
            ended_at = datetime_to_iso(timeline.get("EndDateTime")) or isoformat_utc()
            return StepTiming(
                run_id=run_id,
                cluster_id=cluster_id,
                step_id=step_id,
                step_name=str(step.get("Name", step_spec.get("Name", step_kind))),
                step_kind=step_kind,
                technology=benchmark_step.technology if benchmark_step else "",
                input_label=benchmark_step.input_label if benchmark_step else "",
                repetition=benchmark_step.repetition if benchmark_step else "",
                step_state=state,
                submitted_at_utc=datetime_to_iso(timeline.get("CreationDateTime")) or submitted_at,
                started_at_utc=started_at,
                ended_at_utc=ended_at,
                wall_clock_seconds=seconds_between(started_at, ended_at),
                failure_reason=failure,
                metrics_s3_uri=metric_uri_for_step(benchmark_step) if benchmark_step else "",
            )
        if time.monotonic() > deadline:
            raise TimeoutError(f"EMR step {step_id} ({step_spec.get('Name', step_kind)}) exceeded configured step timeout")
        time.sleep(20)


def terminate_cluster(ctx: AwsContext, cluster_id: str, *, dry_run: bool) -> None:
    if not cluster_id:
        return
    if dry_run:
        print(f"DRY-RUN terminate cluster: {cluster_id}")
        return
    boto3_session(ctx).client("emr").terminate_job_flows(JobFlowIds=[cluster_id])


def list_active_project_clusters(ctx: AwsContext) -> list[str]:
    emr = boto3_session(ctx).client("emr")
    cluster_ids: list[str] = []
    paginator = emr.get_paginator("list_clusters")
    for page in paginator.paginate(ClusterStates=sorted(ACTIVE_CLUSTER_STATES)):
        for summary in page.get("Clusters", []):
            cluster_id = str(summary.get("Id", ""))
            if not cluster_id:
                continue
            cluster = emr.describe_cluster(ClusterId=cluster_id)["Cluster"]
            tags = {str(item.get("Key", "")): str(item.get("Value", "")) for item in cluster.get("Tags", [])}
            environment = tags.get("Environment", "")
            if tags.get("Project") == "flight-delay-big-data-analysis" and (
                environment in AWS_PROJECT_ENVIRONMENTS or environment.startswith("aws-emr")
            ):
                cluster_ids.append(cluster_id)
    return sorted(set(cluster_ids))


def cluster_is_active(ctx: AwsContext, cluster_id: str) -> bool:
    if not cluster_id:
        return False
    try:
        state = boto3_session(ctx).client("emr").describe_cluster(ClusterId=cluster_id)["Cluster"]["Status"]["State"]
    except Exception:
        return False
    return state in ACTIVE_CLUSTER_STATES


def write_cost_log(ctx: AwsContext, run_id: str, rows: list[dict[str, Any]], *, dry_run: bool) -> Path:
    path = ctx.results_dir / f"cost_log_{run_id}.csv"
    if dry_run:
        print(f"DRY-RUN write cost log: {path.relative_to(PROJECT_ROOT)}")
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "run_id",
        "cluster_id",
        "started_at_utc",
        "ended_at_utc",
        "status",
        "node_count",
        "primary_nodes",
        "core_nodes",
        "instance_type",
        "cluster_lifetime_minutes",
        "node_hours",
        "estimated_hourly_usd_per_node",
        "estimated_cost_usd",
        "budget_env_name",
        "budget_env_value",
        "notes",
    ]
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})
    upload_file(ctx, path, s3_key(ctx, "results", "runs", run_id, "cost_log.csv"), dry_run=False)
    return path


def cost_log_row(
    ctx: AwsContext,
    *,
    run_id: str,
    cluster_id: str,
    started_at_utc: str,
    ended_at_utc: str,
    status: str,
    notes: str,
) -> dict[str, Any]:
    profile = cluster_profile(ctx.config)
    node_count = cluster_node_count(ctx.config)
    lifetime_seconds = seconds_between(started_at_utc, ended_at_utc)
    lifetime_minutes = "" if lifetime_seconds == "" else round(float(lifetime_seconds) / 60.0, 3)
    node_hours = "" if lifetime_seconds == "" else round(node_count * float(lifetime_seconds) / 3600.0, 6)
    budget = ctx.config.get("aws", {}).get("budget", {})
    hourly = budget.get("estimated_hourly_usd_per_node", "")
    try:
        estimated_cost = "" if node_hours == "" or hourly in ("", None) else round(float(node_hours) * float(hourly), 4)
    except (TypeError, ValueError):
        estimated_cost = ""
    budget_env_name = str(budget.get("remaining_budget_env", "AWS_LEARNER_LAB_BUDGET_REMAINING_USD"))
    return {
        "run_id": run_id,
        "cluster_id": cluster_id,
        "started_at_utc": started_at_utc,
        "ended_at_utc": ended_at_utc,
        "status": status,
        "node_count": node_count,
        "primary_nodes": int(profile.get("primary_nodes", 1)),
        "core_nodes": int(profile.get("core_nodes", 2)),
        "instance_type": cluster_instance_type(ctx.config),
        "cluster_lifetime_minutes": lifetime_minutes,
        "node_hours": node_hours,
        "estimated_hourly_usd_per_node": hourly,
        "estimated_cost_usd": estimated_cost,
        "budget_env_name": budget_env_name,
        "budget_env_value": os.environ.get(budget_env_name, ""),
        "notes": notes,
    }


def write_benchmark_outputs(ctx: AwsContext, run_id: str, rows: list[dict[str, Any]], *, dry_run: bool) -> Path:
    path = ctx.results_dir / f"benchmark_{run_id}.csv"
    if dry_run:
        print(f"DRY-RUN write benchmark CSV: {path.relative_to(PROJECT_ROOT)} ({len(rows)} rows)")
        return path
    ctx.results_dir.mkdir(parents=True, exist_ok=True)
    write_benchmark_csv(path, rows)
    write_benchmark_csv(ctx.results_dir / "benchmark_latest.csv", rows)
    upload_file(ctx, path, s3_key(ctx, "results", "runs", run_id, f"benchmark_{run_id}.csv"), dry_run=False)
    return path


def upload_step_manifest(ctx: AwsContext, run_id: str, steps: list[BenchmarkStep], *, dry_run: bool) -> None:
    manifest = {"run_id": run_id, "steps": [asdict(step) for step in steps]}
    with tempfile.TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "step_manifest.json"
        path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        upload_file(ctx, path, s3_key(ctx, "code", "runs", run_id, "step_manifest.json"), dry_run=dry_run)


def command_upload(args: argparse.Namespace) -> int:
    config = load_yaml(args.config)
    ctx = context_from_config(config)
    manifest = load_json(local_manifest_path(config))
    run_id = args.run_id or run_id_from_timestamp(datetime.now(timezone.utc))
    ensure_bucket(ctx, dry_run=args.dry_run)
    upload_data(ctx, manifest, dry_run=args.dry_run)
    upload_code(ctx, run_id, dry_run=args.dry_run)
    return 0


def command_run(args: argparse.Namespace) -> int:
    config = load_yaml(args.config)
    ctx = context_from_config(config)
    manifest = load_json(local_manifest_path(config))
    run_started = utc_now()
    run_id = args.run_id or run_id_from_timestamp(run_started)
    timestamp_utc = run_started.isoformat()
    run_kind = "smoke" if args.smoke_only else "full"
    total_deadline = time.monotonic() + timeout_seconds(config, "total_run_seconds", 7200)
    ensure_bucket(ctx, dry_run=args.dry_run)
    code_upload = upload_code(ctx, run_id, dry_run=args.dry_run)
    steps = expand_benchmark_steps(ctx, run_id, manifest)
    if args.smoke_only:
        steps = smoke_steps(steps)
    validate_uploaded_inputs(ctx, steps, dry_run=args.dry_run)
    upload_step_manifest(ctx, run_id, steps, dry_run=args.dry_run)
    execution_setting = str(config.get("benchmark", {}).get("execution_setting", "Amazon EMR"))
    environment = configured_environment(config)
    rows: list[dict[str, Any]] = []
    step_timings: list[StepTiming] = []
    cluster_id = ""
    status = "success"
    notes = ""
    try:
        cluster_id = create_cluster(ctx, run_id, dry_run=args.dry_run)
        write_state(ctx, {"run_id": run_id, "cluster_id": cluster_id, "status": "running"}, dry_run=args.dry_run)
        write_run_manifest(
            ctx,
            run_id,
            run_manifest(ctx, run_id=run_id, run_kind=run_kind, code_upload=code_upload, config_path=args.config, cluster_id=cluster_id, status="running"),
            dry_run=args.dry_run,
        )
        if not args.dry_run:
            wait_for_cluster(ctx, cluster_id)
        dependency_timing = submit_and_wait_step(
            ctx,
            cluster_id,
            dependency_step(config),
            dry_run=args.dry_run,
            run_id=run_id,
            step_kind="dependency",
        )
        step_timings.append(dependency_timing)
        if dependency_timing.step_state not in SUCCESS_STEP_STATES:
            raise RuntimeError(f"Dependency step failed: {dependency_timing.failure_reason}")

        for step in steps:
            if time.monotonic() > total_deadline:
                raise TimeoutError(f"Run {run_id} exceeded configured total run timeout")
            timing = submit_and_wait_step(
                ctx,
                cluster_id,
                build_spark_step(step, run_id=run_id, source_uri=code_upload.source_uri, runtime_config_uri=code_upload.runtime_config_uri),
                dry_run=args.dry_run,
                run_id=run_id,
                step_kind="benchmark",
                benchmark_step=step,
            )
            step_timings.append(timing)
            metrics = None if args.dry_run or timing.step_state not in SUCCESS_STEP_STATES else require_s3_json(ctx, metric_uri_for_step(step))
            rows.extend(
                normalize_step_rows(
                    step,
                    run_id=run_id,
                    timestamp_utc=timestamp_utc,
                    execution_setting=execution_setting,
                    environment=environment,
                    metrics=metrics,
                    step_state=timing.step_state,
                    failure_reason=timing.failure_reason,
                )
            )
            if timing.step_state not in SUCCESS_STEP_STATES:
                raise RuntimeError(f"Benchmark step failed: {step.technology} {step.input_label} rep{step.repetition}: {timing.failure_reason}")
    except Exception as exc:
        status = "failed"
        notes = str(exc)
        print(f"# AWS EMR benchmark failed: {exc}", file=sys.stderr)
    finally:
        terminate_cluster(ctx, cluster_id, dry_run=args.dry_run)
        write_state(ctx, {"run_id": run_id, "cluster_id": cluster_id, "status": "terminated"}, dry_run=args.dry_run)

    if args.dry_run and not rows:
        for step in steps:
            rows.extend(
                normalize_step_rows(
                    step,
                    run_id=run_id,
                    timestamp_utc=timestamp_utc,
                    execution_setting=execution_setting,
                    environment=environment,
                    metrics=None,
                    step_state="COMPLETED",
                )
            )
    benchmark_path = write_benchmark_outputs(ctx, run_id, rows, dry_run=args.dry_run)
    write_step_timing(ctx, run_id, step_timings, dry_run=args.dry_run)
    ended_at_utc = isoformat_utc()
    write_cost_log(
        ctx,
        run_id,
        [
            cost_log_row(
                ctx,
                run_id=run_id,
                cluster_id=cluster_id,
                started_at_utc=timestamp_utc,
                ended_at_utc=ended_at_utc,
                status=status,
                notes=notes,
            )
        ],
        dry_run=args.dry_run,
    )
    write_run_manifest(
        ctx,
        run_id,
        run_manifest(ctx, run_id=run_id, run_kind=run_kind, code_upload=code_upload, config_path=args.config, cluster_id=cluster_id, status=status, notes=notes),
        dry_run=args.dry_run,
    )
    print(f"# AWS EMR benchmark CSV: {benchmark_path}")
    return 0 if status == "success" else 1


def command_fetch_results(args: argparse.Namespace) -> int:
    config = load_yaml(args.config)
    ctx = context_from_config(config)
    run_id = args.run_id or str(read_state(ctx).get("run_id", ""))
    if not run_id:
        raise ValueError("Provide --run-id or run benchmark-aws-emr first.")
    prefix = s3_key(ctx, "results", "runs", run_id)
    destination = ctx.results_dir / "downloaded" / run_id
    if args.dry_run:
        print(f"DRY-RUN download s3://{ctx.bucket}/{prefix}/ -> {destination.relative_to(PROJECT_ROOT)}")
        return 0
    s3 = boto3_session(ctx).client("s3")
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=ctx.bucket, Prefix=prefix):
        for item in page.get("Contents", []):
            key = item["Key"]
            target = destination / Path(key).relative_to(prefix)
            target.parent.mkdir(parents=True, exist_ok=True)
            s3.download_file(ctx.bucket, key, str(target))
    print(f"# Downloaded AWS EMR results to {destination.relative_to(PROJECT_ROOT)}")
    return 0


def command_cleanup(args: argparse.Namespace) -> int:
    config = load_yaml(args.config)
    ctx = context_from_config(config)
    cluster_ids = set(list_active_project_clusters(ctx))
    explicit_cluster_id = args.cluster_id or str(read_state(ctx).get("cluster_id", ""))
    if explicit_cluster_id and cluster_is_active(ctx, explicit_cluster_id):
        cluster_ids.add(explicit_cluster_id)
    if args.dry_run:
        if cluster_ids:
            for cluster_id in sorted(cluster_ids):
                print(f"DRY-RUN terminate active tagged EMR cluster: {cluster_id}")
        else:
            print("# No active tracked or tagged EMR clusters to terminate.")
        return 0
    if not cluster_ids:
        print("# No active tracked or tagged EMR clusters to terminate.")
        return 0
    for cluster_id in sorted(cluster_ids):
        terminate_cluster(ctx, cluster_id, dry_run=False)
        print(f"# Termination requested for EMR cluster: {cluster_id}")
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--env-file", type=Path, default=DEFAULT_ENV_FILE)
    parser.add_argument("--dry-run", action="store_true")
    subparsers = parser.add_subparsers(dest="command", required=True)

    upload = subparsers.add_parser("upload")
    upload.add_argument("--run-id")
    upload.set_defaults(func=command_upload)

    run = subparsers.add_parser("run")
    run.add_argument("--run-id")
    run.add_argument("--smoke-only", action="store_true", help="Run only the 100k Spark SQL/Core smoke gate.")
    run.set_defaults(func=command_run)

    fetch = subparsers.add_parser("fetch-results")
    fetch.add_argument("--run-id")
    fetch.set_defaults(func=command_fetch_results)

    cleanup = subparsers.add_parser("cleanup")
    cleanup.add_argument("--cluster-id")
    cleanup.set_defaults(func=command_cleanup)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    load_env_file(args.env_file)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
