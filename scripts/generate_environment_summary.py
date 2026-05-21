"""Generate report-ready hardware and runtime environment summaries."""

from __future__ import annotations

import argparse
import csv
import json
import os
import platform
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import psutil
import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TABLES_DIR = PROJECT_ROOT / "report" / "tables"
DEFAULT_CONFIGS = (
    PROJECT_ROOT / "config" / "local.yaml",
    PROJECT_ROOT / "config" / "cluster.yaml",
)


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


def run_command(command: list[str], timeout_seconds: int = 20) -> str:
    try:
        result = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout_seconds,
        )
    except Exception as exc:  # pragma: no cover - defensive diagnostics
        return f"unavailable ({exc})"

    output = (result.stdout or result.stderr).strip()
    if result.returncode != 0:
        return f"unavailable ({output or 'exit code ' + str(result.returncode)})"
    return output or "available"


def powershell_value(script: str) -> str:
    return run_command(["powershell", "-NoProfile", "-Command", script])


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)
    return data if isinstance(data, dict) else {}


def add_record(records: list[dict[str, str]], category: str, item: str, value: object, source: str) -> None:
    records.append(
        {
            "category": category,
            "item": item,
            "value": str(value),
            "source": source,
        }
    )


def first_line(text: str) -> str:
    return text.splitlines()[0] if text else ""


def dockerfile_base_image(path: Path) -> str:
    if not path.exists():
        return "unavailable (Dockerfile.hive not found)"
    match = re.search(r"^FROM\s+([^\s]+)", path.read_text(encoding="utf-8"), flags=re.MULTILINE)
    return match.group(1) if match else "unavailable (no FROM line found)"


def collect_host_records(records: list[dict[str, str]]) -> None:
    timestamp = datetime.now(timezone.utc).isoformat()
    add_record(records, "campaign", "summary_generated_at_utc", timestamp, "script timestamp")
    add_record(records, "host", "os", platform.platform(), "platform.platform")
    add_record(records, "host", "python_executable", sys.executable, "sys.executable")
    add_record(records, "host", "python_version", platform.python_version(), "platform.python_version")
    add_record(records, "host", "cpu_model", platform.processor() or "unknown", "platform.processor")
    add_record(records, "host", "physical_cores", psutil.cpu_count(logical=False) or "unknown", "psutil")
    add_record(records, "host", "logical_cores", psutil.cpu_count(logical=True) or "unknown", "psutil")
    add_record(records, "host", "ram_bytes", psutil.virtual_memory().total, "psutil")

    disk = psutil.disk_usage(str(PROJECT_ROOT.anchor or PROJECT_ROOT))
    add_record(records, "host", "project_drive_total_bytes", disk.total, "psutil.disk_usage")
    add_record(records, "host", "project_drive_free_bytes", disk.free, "psutil.disk_usage")

    if os.name == "nt":
        cpu = powershell_value(
            "(Get-CimInstance Win32_Processor | Select-Object -First 1 -ExpandProperty Name)"
        )
        add_record(records, "host", "windows_cpu_model", cpu, "Win32_Processor")
        os_detail = powershell_value(
            "$os=Get-CimInstance Win32_OperatingSystem; "
            "'{0} {1} build {2} {3}' -f $os.Caption,$os.Version,$os.BuildNumber,$os.OSArchitecture"
        )
        add_record(records, "host", "windows_os_detail", os_detail, "Win32_OperatingSystem")
        disk_type = powershell_value(
            "Get-PhysicalDisk | Select-Object -First 1 | "
            "ForEach-Object { '{0}; media={1}; bus={2}; size={3}' -f $_.FriendlyName,$_.MediaType,$_.BusType,$_.Size }"
        )
        add_record(records, "host", "disk_type", disk_type, "Get-PhysicalDisk")


def collect_runtime_records(records: list[dict[str, str]]) -> None:
    add_record(records, "runtime", "java_version", first_line(run_command(["java", "-version"])), "java -version")
    add_record(records, "runtime", "docker_version", run_command(["docker", "--version"]), "docker --version")
    add_record(records, "runtime", "docker_compose_version", run_command(["docker", "compose", "version"]), "docker compose version")
    add_record(
        records,
        "runtime",
        "docker_desktop_limits",
        run_command(["docker", "info", "--format", "CPUs={{.NCPU}}; MemBytes={{.MemTotal}}; Server={{.ServerVersion}}; OS={{.OperatingSystem}}"]),
        "docker info",
    )
    add_record(records, "runtime", "hive_base_image", dockerfile_base_image(PROJECT_ROOT / "Dockerfile.hive"), "Dockerfile.hive")
    add_record(
        records,
        "runtime",
        "mapreduce_base_image",
        dockerfile_base_image(PROJECT_ROOT / "Dockerfile.mapreduce"),
        "Dockerfile.mapreduce",
    )

    try:
        import pandas
        import pyarrow
        import pyspark

        add_record(records, "runtime", "pyspark_version", pyspark.__version__, "Python import")
        add_record(records, "runtime", "pandas_version", pandas.__version__, "Python import")
        add_record(records, "runtime", "pyarrow_version", pyarrow.__version__, "Python import")
    except Exception as exc:  # pragma: no cover - import diagnostics
        add_record(records, "runtime", "python_package_versions", f"unavailable ({exc})", "Python import")


def collect_config_records(records: list[dict[str, str]], configs: list[Path]) -> None:
    for config_path in configs:
        config = load_yaml(config_path)
        label = str(config.get("environment", config_path.stem))
        spark = config.get("spark", {})
        benchmark = config.get("benchmark", {})

        add_record(records, "spark_config", f"{label}_config_path", display_path(config_path), "config yaml")
        add_record(records, "spark_config", f"{label}_spark_master", spark.get("master", ""), "config yaml")
        add_record(records, "spark_config", f"{label}_shuffle_partitions", spark.get("shuffle_partitions", ""), "config yaml")
        add_record(records, "spark_config", f"{label}_cluster_size", benchmark.get("cluster_size", ""), "config yaml")
        if benchmark.get("spark_driver_service"):
            add_record(records, "spark_config", f"{label}_spark_driver_service", benchmark["spark_driver_service"], "config yaml")
        if benchmark.get("container_workspace"):
            add_record(records, "spark_config", f"{label}_container_workspace", benchmark["container_workspace"], "config yaml")


def collect_compose_records(records: list[dict[str, str]]) -> None:
    compose_path = PROJECT_ROOT / "docker-compose.yml"
    if not compose_path.exists():
        add_record(records, "docker_topology", "compose_file", "unavailable", "docker-compose.yml")
        return

    compose = load_yaml(compose_path)
    services = compose.get("services", {})
    add_record(records, "docker_topology", "compose_services", ", ".join(sorted(services)), "docker-compose.yml")
    for worker_name in ("spark-worker-1", "spark-worker-2"):
        command = services.get(worker_name, {}).get("command", [])
        command_text = " ".join(str(part) for part in command) if isinstance(command, list) else str(command)
        add_record(records, "docker_topology", f"{worker_name}_command", command_text, "docker-compose.yml")
    add_record(records, "docker_topology", "worker_count_variation", "not used in M2; Compose defines two named workers", "M2 plan")


def collect_environment_records(configs: list[Path]) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    collect_host_records(records)
    collect_runtime_records(records)
    collect_config_records(records, configs)
    collect_compose_records(records)
    return records


def write_csv(path: Path, records: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["category", "item", "value", "source"])
        writer.writeheader()
        writer.writerows(records)


def markdown_escape(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def write_markdown(path: Path, records: list[dict[str, str]]) -> None:
    lines = [
        "| category | item | value | source |",
        "| --- | --- | --- | --- |",
    ]
    for record in records:
        lines.append(
            "| "
            + " | ".join(markdown_escape(record[column]) for column in ("category", "item", "value", "source"))
            + " |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_json(path: Path, records: list[dict[str, str]]) -> None:
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "records": records,
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_environment_summary(tables_dir: Path, records: list[dict[str, str]]) -> list[Path]:
    tables_dir.mkdir(parents=True, exist_ok=True)
    csv_path = tables_dir / "environment_summary.csv"
    md_path = tables_dir / "environment_summary.md"
    json_path = tables_dir / "environment_summary.json"
    write_csv(csv_path, records)
    write_markdown(md_path, records)
    write_json(json_path, records)
    return [csv_path, md_path, json_path]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tables-dir", type=Path, default=DEFAULT_TABLES_DIR, help="Report tables directory.")
    parser.add_argument("--config", action="append", type=Path, help="YAML config to summarize. Repeatable.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    configs = [resolve_project_path(path) for path in (args.config or DEFAULT_CONFIGS)]
    records = collect_environment_records(configs)
    paths = write_environment_summary(resolve_project_path(args.tables_dir), records)
    for path in paths:
        print(f"# Wrote {display_path(path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
