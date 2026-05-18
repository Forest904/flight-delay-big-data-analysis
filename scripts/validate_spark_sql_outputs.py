"""Validate generated Spark SQL reference outputs."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd
import yaml
from pyspark.sql import SparkSession
from pyspark.sql import functions as F


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.common.prepared_data import read_prepared_parquet
from src.preparation.prepare_spark import ensure_java_17


LOCAL_CONFIG = PROJECT_ROOT / "config" / "local.yaml"

DELAY_COLUMNS = [
    "origin_airport",
    "month",
    "delay_range",
    "flight_count",
    "avg_departure_delay",
    "avg_arrival_delay",
    "top_delay_or_cancellation_cause",
]

RANKING_COLUMNS = [
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


def resolve_project_path(path_value: str) -> Path:
    path = Path(path_value)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path


def spark_sql_output_root(local_config: dict[str, Any]) -> Path:
    paths = local_config.get("paths", {})
    outputs_dir = resolve_project_path(str(paths.get("outputs_dir", "outputs")))
    return outputs_dir / "spark_sql"


def read_csv_dir(path: Path) -> pd.DataFrame:
    parts = sorted(path.glob("part*.csv"))
    if not parts:
        raise FileNotFoundError(f"No CSV part files found under {path}")
    return pd.concat([pd.read_csv(part) for part in parts], ignore_index=True)


def assert_columns(df: pd.DataFrame, expected: list[str], label: str) -> None:
    actual = list(df.columns)
    if actual != expected:
        raise AssertionError(f"{label} columns differ. Expected {expected}, found {actual}")


def assert_ranking_order(ranking: pd.DataFrame) -> None:
    for origin_airport, group in ranking.groupby("origin_airport"):
        ordered = group.sort_values(["rank_at_airport", "avg_departure_delay", "airline"], na_position="last")
        delay_values = ordered["avg_departure_delay"].dropna().tolist()
        if delay_values != sorted(delay_values):
            raise AssertionError(f"Ranking is not ascending for {origin_airport}")

        tied = group.dropna(subset=["avg_departure_delay"]).groupby("avg_departure_delay")["rank_at_airport"].nunique()
        if (tied > 1).any():
            raise AssertionError(f"Equal average delays have different ranks for {origin_airport}")


def main() -> int:
    local_config = load_yaml(LOCAL_CONFIG)
    paths = local_config.get("paths", {})
    prepared_file_value = paths.get("prepared_file")
    if not prepared_file_value:
        raise ValueError(f"{LOCAL_CONFIG} does not define paths.prepared_file")

    prepared_file = resolve_project_path(str(prepared_file_value))
    output_root = spark_sql_output_root(local_config)
    metrics_file = output_root / "runtime_metrics.json"

    metrics = json.loads(metrics_file.read_text(encoding="utf-8"))
    if metrics.get("status") != "success":
        raise AssertionError(f"Spark SQL metrics status is not success: {metrics.get('status')}")
    metric_rows = {job["job_name"]: job["output_rows"] for job in metrics["jobs"]}

    delay = read_csv_dir(output_root / "delay_by_airport_month" / "full")
    ranking = read_csv_dir(output_root / "airline_airport_ranking" / "full")

    assert_columns(delay, DELAY_COLUMNS, "delay_by_airport_month")
    assert_columns(ranking, RANKING_COLUMNS, "airline_airport_ranking")
    if len(delay) != metric_rows["delay_by_airport_month"]:
        raise AssertionError("Delay output row count does not match runtime metrics")
    if len(ranking) != metric_rows["airline_airport_ranking"]:
        raise AssertionError("Ranking output row count does not match runtime metrics")

    delay_ranges = set(delay["delay_range"].unique())
    if not delay_ranges <= {"low", "medium", "high"}:
        raise AssertionError(f"Unexpected delay ranges: {sorted(delay_ranges)}")
    if not ranking["cancellation_rate"].between(0, 1).all():
        raise AssertionError("Cancellation rates must be between 0 and 1")
    if not (ranking["rank_at_airport"] >= 1).all():
        raise AssertionError("Ranking values must start at 1 or greater")
    if not (ranking.groupby("origin_airport")["rank_at_airport"].min() == 1).all():
        raise AssertionError("Every airport partition must have a rank 1")

    difference_error = (
        ranking["avg_departure_delay"]
        - ranking["airport_avg_departure_delay"]
        - ranking["difference_from_airport_avg_departure_delay"]
    ).abs().max()
    if difference_error >= 1e-9:
        raise AssertionError("Difference from airport average is inconsistent")
    assert_ranking_order(ranking)

    ensure_java_17()
    spark = SparkSession.builder.master("local[*]").appName("validate-spark-sql-outputs").getOrCreate()
    try:
        flights = read_prepared_parquet(spark, prepared_file)
        non_null_departure_rows = flights.where(F.col("departure_delay").isNotNull()).count()
        total_prepared_rows = flights.count()
    finally:
        spark.stop()

    if int(delay["flight_count"].sum()) != non_null_departure_rows:
        raise AssertionError("Delay grouped flight counts do not match non-null departure-delay rows")
    if int(ranking["flight_count"].sum()) != total_prepared_rows:
        raise AssertionError("Ranking grouped flight counts do not match all prepared rows")

    print("Spark SQL output validation passed")
    print(f"delay rows: {len(delay)}; ranking rows: {len(ranking)}")
    print(f"delay grouped flights: {int(delay['flight_count'].sum())}; non-null departure rows: {non_null_departure_rows}")
    print(f"ranking grouped flights: {int(ranking['flight_count'].sum())}; prepared rows: {total_prepared_rows}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
