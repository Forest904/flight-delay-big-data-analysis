"""Validate Spark Core outputs against the Spark SQL reference outputs."""

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
    "top_1_cause",
    "top_1_count",
    "top_2_cause",
    "top_2_count",
    "top_3_cause",
    "top_3_count",
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

DELAY_NUMERIC_COLUMNS = [
    "flight_count",
    "avg_departure_delay",
    "avg_arrival_delay",
    "top_1_count",
    "top_2_count",
    "top_3_count",
]
DELAY_CAUSE_COLUMNS = ["top_1_cause", "top_2_cause", "top_3_cause"]
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
    return outputs_dir / "spark_sql", outputs_dir / "spark_core"


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


def assert_key_sets_match(sql: pd.DataFrame, core: pd.DataFrame, keys: list[str], label: str) -> None:
    sql_keys = set(map(tuple, sql[keys].itertuples(index=False, name=None)))
    core_keys = set(map(tuple, core[keys].itertuples(index=False, name=None)))
    missing = sql_keys - core_keys
    extra = core_keys - sql_keys
    if missing or extra:
        raise AssertionError(
            f"{label} key mismatch. Missing from Spark Core: {len(missing)}; extra in Spark Core: {len(extra)}"
        )


def assert_unique_keys(df: pd.DataFrame, keys: list[str], label: str) -> None:
    duplicates = df[df.duplicated(keys, keep=False)]
    if not duplicates.empty:
        sample = duplicates[keys].head(5).to_dict(orient="records")
        raise AssertionError(f"{label} contains duplicate keys for {keys}: {sample}")


def assert_equal_row_count(sql: pd.DataFrame, core: pd.DataFrame, label: str) -> None:
    if len(sql) != len(core):
        raise AssertionError(f"{label} row counts differ. Spark SQL: {len(sql)}; Spark Core: {len(core)}")


def assert_numeric_close(
    merged: pd.DataFrame,
    columns: list[str],
    label: str,
) -> None:
    for column in columns:
        sql_col = f"{column}_sql"
        core_col = f"{column}_core"
        sql_values = pd.to_numeric(merged[sql_col], errors="coerce")
        core_values = pd.to_numeric(merged[core_col], errors="coerce")
        both_null = sql_values.isna() & core_values.isna()
        differences = (sql_values - core_values).abs()
        bad = ~(both_null | (differences <= TOLERANCE))
        if bad.any():
            sample = merged.loc[bad].head(3)
            raise AssertionError(f"{label} numeric column {column} differs beyond {TOLERANCE}: {sample}")


def assert_string_columns_equal(
    merged: pd.DataFrame,
    columns: list[str],
    left_suffix: str,
    right_suffix: str,
    label: str,
) -> None:
    for column in columns:
        left_col = f"{column}_{left_suffix}"
        right_col = f"{column}_{right_suffix}"
        both_null = merged[left_col].isna() & merged[right_col].isna()
        mismatch = ~(both_null | (merged[left_col] == merged[right_col]))
        if mismatch.any():
            sample = merged.loc[mismatch].head(3)
            raise AssertionError(f"{label} string column {column} differs: {sample}")


def validate_delay(sql: pd.DataFrame, core: pd.DataFrame) -> None:
    assert_columns(sql, DELAY_COLUMNS, "spark_sql delay_by_airport_month")
    assert_columns(core, DELAY_COLUMNS, "spark_core delay_by_airport_month")
    assert_equal_row_count(sql, core, "delay_by_airport_month")
    assert_unique_keys(sql, DELAY_KEYS, "spark_sql delay_by_airport_month")
    assert_unique_keys(core, DELAY_KEYS, "spark_core delay_by_airport_month")
    assert_key_sets_match(sql, core, DELAY_KEYS, "delay_by_airport_month")

    merged = sql.merge(core, on=DELAY_KEYS, suffixes=("_sql", "_core"), how="inner")
    assert_numeric_close(merged, DELAY_NUMERIC_COLUMNS, "delay_by_airport_month")
    assert_string_columns_equal(
        merged,
        DELAY_CAUSE_COLUMNS,
        "sql",
        "core",
        "delay_by_airport_month",
    )


def assert_ranking_order(ranking: pd.DataFrame, label: str) -> None:
    for origin_airport, group in ranking.groupby("origin_airport"):
        ordered = group.sort_values(["rank_at_airport", "avg_departure_delay", "airline"], na_position="last")
        delay_values = ordered["avg_departure_delay"].dropna().tolist()
        if delay_values != sorted(delay_values):
            raise AssertionError(f"{label} ranking is not ascending for {origin_airport}")

        tied = group.dropna(subset=["avg_departure_delay"]).groupby("avg_departure_delay")["rank_at_airport"].nunique()
        if (tied > 1).any():
            raise AssertionError(f"{label} equal average delays have different ranks for {origin_airport}")


def validate_ranking(sql: pd.DataFrame, core: pd.DataFrame) -> None:
    assert_columns(sql, RANKING_COLUMNS, "spark_sql airline_airport_ranking")
    assert_columns(core, RANKING_COLUMNS, "spark_core airline_airport_ranking")
    assert_equal_row_count(sql, core, "airline_airport_ranking")
    assert_unique_keys(sql, RANKING_KEYS, "spark_sql airline_airport_ranking")
    assert_unique_keys(core, RANKING_KEYS, "spark_core airline_airport_ranking")
    assert_key_sets_match(sql, core, RANKING_KEYS, "airline_airport_ranking")

    merged = sql.merge(core, on=RANKING_KEYS, suffixes=("_sql", "_core"), how="inner")
    assert_numeric_close(merged, RANKING_NUMERIC_COLUMNS, "airline_airport_ranking")

    assert_ranking_order(sql, "Spark SQL")
    assert_ranking_order(core, "Spark Core")


def main() -> int:
    local_config = load_yaml(LOCAL_CONFIG)
    sql_root, core_root = output_roots(local_config)

    sql_metrics = assert_metrics_success(sql_root, "spark_sql")
    core_metrics = assert_metrics_success(core_root, "spark_core")
    sql_metric_rows = {job["job_name"]: job["output_rows"] for job in sql_metrics["jobs"]}
    core_metric_rows = {job["job_name"]: job["output_rows"] for job in core_metrics["jobs"]}

    sql_delay = read_csv_dir(sql_root / "delay_by_airport_month" / "full")
    core_delay = read_csv_dir(core_root / "delay_by_airport_month" / "full")
    sql_ranking = read_csv_dir(sql_root / "airline_airport_ranking" / "full")
    core_ranking = read_csv_dir(core_root / "airline_airport_ranking" / "full")

    if len(core_delay) != core_metric_rows["delay_by_airport_month"]:
        raise AssertionError("Spark Core delay row count does not match runtime metrics")
    if len(core_ranking) != core_metric_rows["airline_airport_ranking"]:
        raise AssertionError("Spark Core ranking row count does not match runtime metrics")
    if len(sql_delay) != sql_metric_rows["delay_by_airport_month"]:
        raise AssertionError("Spark SQL delay row count does not match runtime metrics")
    if len(sql_ranking) != sql_metric_rows["airline_airport_ranking"]:
        raise AssertionError("Spark SQL ranking row count does not match runtime metrics")

    validate_delay(sql_delay, core_delay)
    validate_ranking(sql_ranking, core_ranking)

    print("Spark Core output validation passed")
    print(f"delay rows: {len(core_delay)}; ranking rows: {len(core_ranking)}")
    print(f"numeric tolerance: {TOLERANCE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
