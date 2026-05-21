"""Read-only AWS Learner Lab feasibility checks for the EMR milestone."""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = PROJECT_ROOT / "config" / "aws_emr.yaml"
DEFAULT_REPORT_DIR = PROJECT_ROOT / "report" / "tables"
REQUIRED_AWS_ENV_VARS = (
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_SESSION_TOKEN",
)


@dataclass(frozen=True)
class CheckResult:
    category: str
    item: str
    status: str
    required: bool
    detail: str


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


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)
    if not isinstance(data, dict):
        raise ValueError(f"{path} did not contain a YAML mapping")
    return data


def aws_error_detail(exc: Exception) -> str:
    response = getattr(exc, "response", None)
    if isinstance(response, dict):
        error = response.get("Error", {})
        code = error.get("Code", exc.__class__.__name__)
        message = error.get("Message", str(exc))
        return f"{code}: {message}"
    return f"{exc.__class__.__name__}: {exc}"


def add_result(
    results: list[CheckResult],
    category: str,
    item: str,
    status: str,
    detail: str,
    *,
    required: bool = True,
) -> None:
    results.append(CheckResult(category=category, item=item, status=status, required=required, detail=detail))


def parse_budget(value: str | None) -> float | None:
    if value is None or not value.strip():
        return None
    try:
        return float(value.strip().replace("$", ""))
    except ValueError:
        return None


def check_local_inputs(config: dict[str, Any], results: list[CheckResult]) -> str:
    missing = [name for name in REQUIRED_AWS_ENV_VARS if not os.environ.get(name)]
    if missing:
        add_result(results, "credentials", "temporary AWS keys", "fail", "missing " + ", ".join(missing))
    else:
        add_result(results, "credentials", "temporary AWS keys", "pass", "required Learner Lab env vars are present")

    region = os.environ.get("AWS_DEFAULT_REGION") or os.environ.get("AWS_REGION") or str(config["aws"]["region"])
    expected_region = str(config["aws"]["region"])
    status = "pass" if region == expected_region else "warn"
    detail = f"using {region}; expected default is {expected_region}"
    add_result(results, "config", "region", status, detail)

    budget_config = config.get("aws", {}).get("budget", {})
    budget_env = str(budget_config.get("remaining_budget_env", "AWS_LEARNER_LAB_BUDGET_REMAINING_USD"))
    remaining = parse_budget(os.environ.get(budget_env))
    minimum = float(budget_config.get("minimum_remaining_usd", 0))
    if remaining is None:
        add_result(results, "budget", "remaining learner lab budget", "fail", f"set {budget_env} from the Learner Lab page")
    elif remaining >= minimum:
        add_result(results, "budget", "remaining learner lab budget", "pass", f"{remaining:.2f} USD >= {minimum:.2f} USD")
    else:
        add_result(results, "budget", "remaining learner lab budget", "fail", f"{remaining:.2f} USD < {minimum:.2f} USD")

    return region


def newest_emr_release(emr_client: Any) -> str | None:
    try:
        response = emr_client.list_release_labels()
    except Exception:
        return None
    labels = response.get("ReleaseLabels", [])
    if not isinstance(labels, list):
        return None
    for label in labels:
        text = str(label)
        if text.startswith("emr-7."):
            return text
    return str(labels[0]) if labels else None


def selected_release_label(config: dict[str, Any], emr_client: Any, results: list[CheckResult]) -> str:
    emr_config = config.get("emr", {})
    configured = str(emr_config.get("release_label", "auto"))
    fallback = str(emr_config.get("release_label_fallback", "emr-7.10.0"))
    if configured != "auto":
        add_result(results, "emr", "release label", "pass", configured)
        return configured

    detected = newest_emr_release(emr_client)
    if detected:
        add_result(results, "emr", "release label", "pass", f"auto-detected {detected}")
        return detected
    add_result(results, "emr", "release label", "warn", f"could not auto-detect release; using fallback {fallback}")
    return fallback


def instance_size_score(instance: dict[str, Any]) -> tuple[float, float, str]:
    vcpu = float(instance.get("VCPU", instance.get("vCPU", 0)) or 0)
    memory = float(instance.get("MemoryGB", 0) or 0)
    return (vcpu, memory, str(instance.get("Type", "")))


def choose_instance_type(
    supported_instances: list[dict[str, Any]],
    fallback_order: list[str],
) -> tuple[str | None, str]:
    supported_by_type = {str(item.get("Type")): item for item in supported_instances if item.get("Type")}
    for candidate in fallback_order:
        if candidate in supported_by_type:
            return candidate, "configured fallback order"
    if not supported_instances:
        return None, "no supported instances returned"
    largest = max(supported_instances, key=instance_size_score)
    return str(largest.get("Type")), "largest EMR-supported type returned by AWS"


def check_sts(session: Any, results: list[CheckResult]) -> str | None:
    try:
        identity = session.client("sts").get_caller_identity()
    except Exception as exc:
        add_result(results, "aws", "sts caller identity", "fail", aws_error_detail(exc))
        return None
    account = identity.get("Account", "unknown")
    arn = identity.get("Arn", "unknown")
    add_result(results, "aws", "sts caller identity", "pass", f"account {account}; arn {arn}")
    return str(account)


def check_s3(session: Any, config: dict[str, Any], results: list[CheckResult]) -> bool:
    client = session.client("s3")
    try:
        client.list_buckets()
    except Exception as exc:
        add_result(results, "service", "s3", "fail", aws_error_detail(exc))
        return False
    add_result(results, "service", "s3", "pass", "ListBuckets succeeded")

    bucket_env = str(config.get("s3", {}).get("bucket_env", "AWS_FLIGHT_DELAY_BUCKET"))
    bucket = os.environ.get(bucket_env)
    if bucket:
        try:
            client.head_bucket(Bucket=bucket)
        except Exception as exc:
            add_result(results, "s3", "project bucket", "warn", f"{bucket}: {aws_error_detail(exc)}", required=False)
        else:
            add_result(results, "s3", "project bucket", "pass", bucket, required=False)
    else:
        add_result(results, "s3", "project bucket", "warn", f"{bucket_env} is not set yet", required=False)
    return True


def check_emr(session: Any, config: dict[str, Any], results: list[CheckResult]) -> list[dict[str, Any]]:
    client = session.client("emr")
    try:
        client.list_clusters(ClusterStates=["STARTING", "BOOTSTRAPPING", "RUNNING", "WAITING", "TERMINATING"])
    except Exception as exc:
        add_result(results, "service", "emr", "fail", aws_error_detail(exc))
        return []
    add_result(results, "service", "emr", "pass", "ListClusters succeeded")

    release_label = selected_release_label(config, client, results)
    try:
        response = client.list_supported_instance_types(ReleaseLabel=release_label)
    except Exception as exc:
        add_result(results, "emr", "supported instance types", "fail", aws_error_detail(exc))
        return []

    instances = response.get("SupportedInstanceTypes", [])
    if not isinstance(instances, list):
        instances = []
    fallback_order = [str(item) for item in config.get("emr", {}).get("instance_type_fallback_order", [])]
    chosen, reason = choose_instance_type(instances, fallback_order)
    if chosen:
        add_result(results, "emr", "selected instance type", "pass", f"{chosen} ({reason})")
    else:
        add_result(results, "emr", "selected instance type", "fail", reason)
    add_result(results, "emr", "supported instance type count", "pass", str(len(instances)), required=False)
    return instances


def check_ec2(session: Any, config: dict[str, Any], results: list[CheckResult]) -> None:
    client = session.client("ec2")
    fallback_order = [str(item) for item in config.get("emr", {}).get("instance_type_fallback_order", [])]
    try:
        response = client.describe_instance_type_offerings(
            LocationType="region",
            Filters=[{"Name": "instance-type", "Values": fallback_order}],
        )
    except Exception as exc:
        add_result(results, "service", "ec2", "fail", aws_error_detail(exc))
        return
    offered = sorted({item.get("InstanceType", "") for item in response.get("InstanceTypeOfferings", []) if item.get("InstanceType")})
    detail = ", ".join(offered) if offered else "EC2 reachable, but no fallback instance offerings returned"
    status = "pass" if offered else "warn"
    add_result(results, "service", "ec2", status, detail)


def check_iam(session: Any, config: dict[str, Any], results: list[CheckResult]) -> None:
    client = session.client("iam")
    candidates = config.get("emr", {}).get("iam_role_candidates", {})
    found: list[str] = []
    failures: list[str] = []
    for group, names in candidates.items():
        for name in names:
            try:
                client.get_role(RoleName=str(name))
            except Exception as exc:
                failures.append(f"{group}/{name}: {aws_error_detail(exc)}")
            else:
                found.append(f"{group}/{name}")
                break
    if found:
        add_result(results, "service", "iam roles", "pass", "; ".join(found))
    else:
        add_result(results, "service", "iam roles", "fail", "no configured role candidates were readable; " + " | ".join(failures[:3]))


def check_logging(session: Any, s3_available: bool, config: dict[str, Any], results: list[CheckResult]) -> None:
    require_s3_logs = bool(config.get("checks", {}).get("logging", {}).get("require_s3_logs", True))
    if s3_available and require_s3_logs:
        add_result(results, "logging", "s3 log destination", "pass", "S3 is reachable for EMR log-uri use")
    elif require_s3_logs:
        add_result(results, "logging", "s3 log destination", "fail", "S3 is not available")

    try:
        session.client("logs").describe_log_groups(limit=1)
    except Exception as exc:
        add_result(results, "logging", "cloudwatch logs", "warn", aws_error_detail(exc), required=False)
    else:
        add_result(results, "logging", "cloudwatch logs", "pass", "DescribeLogGroups succeeded", required=False)


def run_checks(config: dict[str, Any], session: Any) -> list[CheckResult]:
    results: list[CheckResult] = []
    check_local_inputs(config, results)
    check_sts(session, results)
    s3_available = check_s3(session, config, results)
    check_emr(session, config, results)
    check_ec2(session, config, results)
    check_iam(session, config, results)
    check_logging(session, s3_available, config, results)
    return results


def print_results(results: list[CheckResult]) -> None:
    width = max(len(result.item) for result in results) if results else 0
    for result in results:
        required = "required" if result.required else "optional"
        print(f"[{result.status.upper():4}] {result.item:<{width}} ({required}) - {result.detail}")
    required_failures = [result for result in results if result.required and result.status == "fail"]
    if required_failures:
        print(f"AWS feasibility check failed: {len(required_failures)} required item(s) need attention.")
    else:
        print("AWS feasibility check passed for all required items.")


def write_report_files(results: list[CheckResult], report_dir: Path) -> None:
    report_dir.mkdir(parents=True, exist_ok=True)
    records = [asdict(result) for result in results]
    timestamp = datetime.now(timezone.utc).isoformat()
    payload = {"generated_at_utc": timestamp, "results": records}
    (report_dir / "aws_feasibility.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    with (report_dir / "aws_feasibility.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["category", "item", "status", "required", "detail"])
        writer.writeheader()
        writer.writerows(records)

    lines = [
        "| category | item | status | required | detail |",
        "| --- | --- | --- | --- | --- |",
    ]
    for record in records:
        values = [str(record[column]).replace("|", "\\|").replace("\n", " ") for column in ("category", "item", "status", "required", "detail")]
        lines.append("| " + " | ".join(values) + " |")
    (report_dir / "aws_feasibility.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run read-only AWS Learner Lab feasibility checks.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--env-file", type=Path, default=PROJECT_ROOT / ".env")
    parser.add_argument("--write-report", action="store_true", help="Write report/tables/aws_feasibility.{json,csv,md}.")
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    load_env_file(args.env_file)
    config = load_yaml(args.config)
    region = check_local_inputs(config, [])

    try:
        import boto3
    except ImportError:
        print("boto3 is not installed. Run `make setup` or install requirements.txt first.", file=sys.stderr)
        return 1

    session = boto3.Session(region_name=region)
    results = run_checks(config, session)
    print_results(results)
    if args.write_report:
        write_report_files(results, args.report_dir)
    return 1 if any(result.required and result.status == "fail" for result in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
