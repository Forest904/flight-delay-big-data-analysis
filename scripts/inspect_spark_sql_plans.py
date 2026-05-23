"""Write formatted Spark SQL physical plans for representative inputs."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from pyspark.sql import DataFrame, SparkSession


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.common.prepared_data import read_prepared_parquet
from src.common.uri import display_location, resolve_local_or_uri
from src.preparation.prepare_spark import ensure_java_17
from src.spark_sql.run_spark_sql import (
    DEFAULT_CONFIG,
    airline_airport_ranking_query,
    build_spark,
    delay_all_causes_query,
    delay_report_query,
    load_yaml,
)


DEFAULT_LABELS = ("1m", "full", "14m")
PLAN_BUILDERS: dict[str, Callable[[SparkSession], DataFrame]] = {
    "delay_by_airport_month": delay_report_query,
    "delay_by_airport_month_all_causes": delay_all_causes_query,
    "airline_airport_ranking": airline_airport_ranking_query,
}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG, help="YAML config path.")
    parser.add_argument(
        "--input-label",
        action="append",
        default=None,
        help="Input label from data/generated/input_size_manifest.json. Defaults to 1m, full, and 14m.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "outputs" / "spark_sql" / "plans",
        help="Directory for generated plan text files.",
    )
    return parser.parse_args(argv)


def resolve_project_path(path_value: str | Path) -> Path:
    path = Path(path_value)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path


def manifest_path(local_config: dict[str, Any]) -> Path:
    generated_dir = resolve_project_path(str(local_config.get("paths", {}).get("generated_dir", "data/generated")))
    return generated_dir / "input_size_manifest.json"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise ValueError(f"{path} did not contain a JSON object")
    return data


def manifest_entries_by_label(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
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


def explain_formatted(df: DataFrame) -> str:
    jvm = df.sparkSession.sparkContext._jvm
    return jvm.PythonSQLUtils.explainString(df._jdf.queryExecution(), "formatted")


def write_plan(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def inspect_plans(
    *,
    config_path: Path,
    input_labels: list[str],
    output_dir: Path,
) -> list[Path]:
    local_config = load_yaml(config_path)
    manifest = load_json(manifest_path(local_config))
    manifest_entries = manifest_entries_by_label(manifest)
    missing = [label for label in input_labels if label not in manifest_entries]
    if missing:
        raise ValueError(f"No successful manifest entry found for input label(s): {', '.join(missing)}")

    spark = build_spark(local_config)
    written: list[Path] = []
    try:
        for label in input_labels:
            input_path = resolve_local_or_uri(str(manifest_entries[label]["path"]), PROJECT_ROOT)
            flights = read_prepared_parquet(spark, input_path)
            flights.createOrReplaceTempView("flights")
            for job_name, builder in PLAN_BUILDERS.items():
                plan = explain_formatted(builder(spark))
                header = {
                    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
                    "input_label": label,
                    "input_path": display_location(input_path, PROJECT_ROOT),
                    "job_name": job_name,
                    "explain_mode": "formatted",
                }
                output_path = output_dir / f"{label}_{job_name}.formatted.txt"
                write_plan(output_path, json.dumps(header, indent=2, sort_keys=True) + "\n\n" + plan)
                written.append(output_path)
    finally:
        spark.stop()
    return written


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    ensure_java_17()
    config_path = args.config if args.config.is_absolute() else PROJECT_ROOT / args.config
    output_dir = args.output_dir if args.output_dir.is_absolute() else PROJECT_ROOT / args.output_dir
    labels = args.input_label or list(DEFAULT_LABELS)
    written = inspect_plans(config_path=config_path, input_labels=labels, output_dir=output_dir)
    print("# Spark SQL formatted plans written:")
    for path in written:
        print(f"# - {display_location(path, PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
