"""Validate Hive outputs against the Spark SQL reference outputs."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd
import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


LOCAL_CONFIG = PROJECT_ROOT / "config" / "local.yaml"
TOLERANCE = 1e-6

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

DELAY_KEYS = ["origin_airport", "month", "delay_range"]
RANKING_KEYS = ["origin_airport", "airline"]

DELAY_NUMERIC_COLUMNS = ["flight_count", "avg_departure_delay", "avg_arrival_delay"]
RANKING_NUMERIC_COLUMNS = [
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


def output_roots(local_config: dict[str, Any]) -> tuple[Path, Path]:
    paths = local_config.get("paths", {})
    outputs_dir = resolve_project_path(str(paths.get("outputs_dir", "outputs")))
    return outputs_dir / "spark_sql", outputs_dir / "hive"


def read_csv_dir(path: Path) -> pd.DataFrame:
    parts = sorted(path.glob("part*.csv"))
    if not parts:
        raise FileNotFoundError(f"No CSV part files found under {path}")
    return pd.concat([pd.read_csv(part) for part in parts], ignore_index=True)


def assert_columns(df: pd.DataFrame, expected: list[str], label: str) -> None:
    actual = list(df.columns)
    if actual != expected:
        raise AssertionError(f"{label} columns differ. Expected {expected}, found {actual}")


def assert_metrics_success(output_root: Path, technology: str) -> dict[str, Any]:
    metrics_path = output_root / "runtime_metrics.json"
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    if metrics.get("technology") != technology:
        raise AssertionError(f"{metrics_path} has unexpected technology: {metrics.get('technology')}")
    if metrics.get("status") != "success":
        raise AssertionError(f"{technology} metrics status is not success: {metrics.get('status')}")
    return metrics


def assert_first_10(output_root: Path, job_name: str, expected_columns: list[str]) -> None:
    sample_path = output_root / job_name / "first_10.csv"
    if not sample_path.exists():
        raise AssertionError(f"Missing first 10 sample file: {sample_path}")
    sample = pd.read_csv(sample_path)
    assert_columns(sample, expected_columns, f"hive {job_name} first_10")
    if len(sample) > 10:
        raise AssertionError(f"{sample_path} contains more than 10 rows")


def assert_key_sets_match(sql: pd.DataFrame, hive: pd.DataFrame, keys: list[str], label: str) -> None:
    sql_keys = set(map(tuple, sql[keys].itertuples(index=False, name=None)))
    hive_keys = set(map(tuple, hive[keys].itertuples(index=False, name=None)))
    missing = sql_keys - hive_keys
    extra = hive_keys - sql_keys
    if missing or extra:
        raise AssertionError(f"{label} key mismatch. Missing from Hive: {len(missing)}; extra in Hive: {len(extra)}")


def assert_unique_keys(df: pd.DataFrame, keys: list[str], label: str) -> None:
    duplicates = df[df.duplicated(keys, keep=False)]
    if not duplicates.empty:
        sample = duplicates[keys].head(5).to_dict(orient="records")
        raise AssertionError(f"{label} contains duplicate keys for {keys}: {sample}")


def assert_equal_row_count(sql: pd.DataFrame, hive: pd.DataFrame, label: str) -> None:
    if len(sql) != len(hive):
        raise AssertionError(f"{label} row counts differ. Spark SQL: {len(sql)}; Hive: {len(hive)}")


def assert_numeric_close(merged: pd.DataFrame, columns: list[str], label: str) -> None:
    for column in columns:
        sql_col = f"{column}_sql"
        hive_col = f"{column}_hive"
        sql_values = pd.to_numeric(merged[sql_col], errors="coerce")
        hive_values = pd.to_numeric(merged[hive_col], errors="coerce")
        both_null = sql_values.isna() & hive_values.isna()
        differences = (sql_values - hive_values).abs()
        bad = ~(both_null | (differences <= TOLERANCE))
        if bad.any():
            sample = merged.loc[bad].head(3)
            raise AssertionError(f"{label} numeric column {column} differs beyond {TOLERANCE}: {sample}")


def validate_delay(sql: pd.DataFrame, hive: pd.DataFrame) -> None:
    assert_columns(sql, DELAY_COLUMNS, "spark_sql delay_by_airport_month")
    assert_columns(hive, DELAY_COLUMNS, "hive delay_by_airport_month")
    assert_equal_row_count(sql, hive, "delay_by_airport_month")
    assert_unique_keys(sql, DELAY_KEYS, "spark_sql delay_by_airport_month")
    assert_unique_keys(hive, DELAY_KEYS, "hive delay_by_airport_month")
    assert_key_sets_match(sql, hive, DELAY_KEYS, "delay_by_airport_month")

    merged = sql.merge(hive, on=DELAY_KEYS, suffixes=("_sql", "_hive"), how="inner")
    assert_numeric_close(merged, DELAY_NUMERIC_COLUMNS, "delay_by_airport_month")

    cause_mismatch = (
        merged["top_delay_or_cancellation_cause_sql"]
        != merged["top_delay_or_cancellation_cause_hive"]
    )
    if cause_mismatch.any():
        sample = merged.loc[cause_mismatch].head(3)
        raise AssertionError(f"Delay top causes differ between Spark SQL and Hive: {sample}")


def assert_ranking_order(ranking: pd.DataFrame, label: str) -> None:
    for origin_airport, group in ranking.groupby("origin_airport"):
        ordered = group.sort_values(["rank_at_airport", "avg_departure_delay", "airline"], na_position="last")
        delay_values = ordered["avg_departure_delay"].dropna().tolist()
        if delay_values != sorted(delay_values):
            raise AssertionError(f"{label} ranking is not ascending for {origin_airport}")

        tied = group.dropna(subset=["avg_departure_delay"]).groupby("avg_departure_delay")["rank_at_airport"].nunique()
        if (tied > 1).any():
            raise AssertionError(f"{label} equal average delays have different ranks for {origin_airport}")


def validate_ranking(sql: pd.DataFrame, hive: pd.DataFrame) -> None:
    assert_columns(sql, RANKING_COLUMNS, "spark_sql airline_airport_ranking")
    assert_columns(hive, RANKING_COLUMNS, "hive airline_airport_ranking")
    assert_equal_row_count(sql, hive, "airline_airport_ranking")
    assert_unique_keys(sql, RANKING_KEYS, "spark_sql airline_airport_ranking")
    assert_unique_keys(hive, RANKING_KEYS, "hive airline_airport_ranking")
    assert_key_sets_match(sql, hive, RANKING_KEYS, "airline_airport_ranking")

    merged = sql.merge(hive, on=RANKING_KEYS, suffixes=("_sql", "_hive"), how="inner")
    assert_numeric_close(merged, RANKING_NUMERIC_COLUMNS, "airline_airport_ranking")

    assert_ranking_order(sql, "Spark SQL")
    assert_ranking_order(hive, "Hive")


def main() -> int:
    local_config = load_yaml(LOCAL_CONFIG)
    sql_root, hive_root = output_roots(local_config)

    sql_metrics = assert_metrics_success(sql_root, "spark_sql")
    hive_metrics = assert_metrics_success(hive_root, "hive")
    sql_metric_rows = {job["job_name"]: job["output_rows"] for job in sql_metrics["jobs"]}
    hive_metric_rows = {job["job_name"]: job["output_rows"] for job in hive_metrics["jobs"]}

    sql_delay = read_csv_dir(sql_root / "delay_by_airport_month" / "full")
    hive_delay = read_csv_dir(hive_root / "delay_by_airport_month" / "full")
    sql_ranking = read_csv_dir(sql_root / "airline_airport_ranking" / "full")
    hive_ranking = read_csv_dir(hive_root / "airline_airport_ranking" / "full")

    if len(hive_delay) != hive_metric_rows["delay_by_airport_month"]:
        raise AssertionError("Hive delay row count does not match runtime metrics")
    if len(hive_ranking) != hive_metric_rows["airline_airport_ranking"]:
        raise AssertionError("Hive ranking row count does not match runtime metrics")
    if len(sql_delay) != sql_metric_rows["delay_by_airport_month"]:
        raise AssertionError("Spark SQL delay row count does not match runtime metrics")
    if len(sql_ranking) != sql_metric_rows["airline_airport_ranking"]:
        raise AssertionError("Spark SQL ranking row count does not match runtime metrics")

    assert_first_10(hive_root, "delay_by_airport_month", DELAY_COLUMNS)
    assert_first_10(hive_root, "airline_airport_ranking", RANKING_COLUMNS)
    validate_delay(sql_delay, hive_delay)
    validate_ranking(sql_ranking, hive_ranking)

    print("Hive output validation passed")
    print(f"delay rows: {len(hive_delay)}; ranking rows: {len(hive_ranking)}")
    print(f"numeric tolerance: {TOLERANCE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
