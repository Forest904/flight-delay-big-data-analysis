"""Shared output validation helpers for cross-technology comparisons."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
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

ALL_CAUSES_COLUMNS = [
    "origin_airport",
    "month",
    "delay_range",
    "cause_rank",
    "cause",
    "cause_count",
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
ALL_CAUSES_KEYS = ["origin_airport", "month", "delay_range", "cause"]
ALL_CAUSES_RANK_KEYS = ["origin_airport", "month", "delay_range", "cause_rank"]
RANKING_KEYS = ["origin_airport", "airline"]
CANCELLED_NO_DEPARTURE_DELAY_RANGE = "cancelled_no_departure_delay"
ALLOWED_DELAY_RANGES = {"low", "medium", "high", CANCELLED_NO_DEPARTURE_DELAY_RANGE}
ALLOWED_DELAY_CAUSES = {
    "delay:carrier",
    "delay:weather",
    "delay:nas",
    "delay:security",
    "delay:late_aircraft",
}

DELAY_NUMERIC_COLUMNS = [
    "flight_count",
    "avg_departure_delay",
    "avg_arrival_delay",
    "top_1_count",
    "top_2_count",
    "top_3_count",
]
DELAY_CAUSE_COLUMNS = ["top_1_cause", "top_2_cause", "top_3_cause"]
ALL_CAUSES_NUMERIC_COLUMNS = ["cause_rank", "cause_count"]
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


def resolve_project_path(path_value: str | Path) -> Path:
    path = Path(path_value)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path


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


def comparable_input_path(value: object, *, container_workspace: str = "/workspace") -> str:
    text = str(value or "").strip().replace("\\", "/")
    if text.startswith("file://"):
        text = text[len("file://") :]
    workspace = container_workspace.rstrip("/")
    for prefix in (f"{workspace}/",):
        if text.startswith(prefix):
            text = text[len(prefix) :]

    project_root = PROJECT_ROOT.resolve().as_posix()
    if text.startswith(project_root + "/"):
        text = text[len(project_root) + 1 :]
    if text.startswith("./"):
        text = text[2:]
    return text


def assert_same_input_path(reference_metrics: dict[str, Any], candidate_metrics: dict[str, Any], candidate_label: str) -> None:
    reference = comparable_input_path(reference_metrics.get("input_path"))
    candidate = comparable_input_path(candidate_metrics.get("input_path"))
    if not reference or not candidate:
        raise AssertionError("Both runtime metrics files must include input_path before cross-technology validation")
    if reference != candidate:
        raise AssertionError(f"Spark SQL and {candidate_label} input_path differ. Spark SQL: {reference}; {candidate_label}: {candidate}")


def canonical_validation_input_path(local_config: dict[str, Any]) -> str:
    paths = local_config.get("paths", {})
    prepared_file = paths.get("prepared_file")
    if not prepared_file:
        raise AssertionError("config/local.yaml must define paths.prepared_file for canonical validation")
    return comparable_input_path(prepared_file)


def assert_canonical_input_path(metrics: dict[str, Any], local_config: dict[str, Any], technology_label: str) -> None:
    actual = comparable_input_path(metrics.get("input_path"))
    expected = canonical_validation_input_path(local_config)
    if not actual:
        raise AssertionError(f"{technology_label} runtime metrics must include input_path")
    if actual != expected:
        raise AssertionError(
            f"{technology_label} input_path must be canonical validation input. Expected {expected}; found {actual}"
        )


def metric_rows(metrics: dict[str, Any]) -> dict[str, int]:
    return {str(job["job_name"]): int(job["output_rows"]) for job in metrics["jobs"]}


def assert_output_row_count(frame: pd.DataFrame, metric_row_counts: dict[str, int], job_name: str, label: str) -> None:
    if len(frame) != metric_row_counts[job_name]:
        raise AssertionError(f"{label} {job_name} row count does not match runtime metrics")


def assert_first_10(output_root: Path, job_name: str, expected_columns: list[str], technology_label: str) -> None:
    sample_path = output_root / job_name / "first_10.csv"
    if not sample_path.exists():
        raise AssertionError(f"Missing first 10 sample file: {sample_path}")
    sample = pd.read_csv(sample_path)
    assert_columns(sample, expected_columns, f"{technology_label} {job_name} first_10")
    if len(sample) > 10:
        raise AssertionError(f"{sample_path} contains more than 10 rows")


def assert_key_sets_match(sql: pd.DataFrame, candidate: pd.DataFrame, keys: list[str], label: str, candidate_label: str) -> None:
    sql_keys = set(map(tuple, sql[keys].itertuples(index=False, name=None)))
    candidate_keys = set(map(tuple, candidate[keys].itertuples(index=False, name=None)))
    missing = sql_keys - candidate_keys
    extra = candidate_keys - sql_keys
    if missing or extra:
        raise AssertionError(
            f"{label} key mismatch. Missing from {candidate_label}: {len(missing)}; extra in {candidate_label}: {len(extra)}"
        )


def assert_unique_keys(df: pd.DataFrame, keys: list[str], label: str) -> None:
    duplicates = df[df.duplicated(keys, keep=False)]
    if not duplicates.empty:
        sample = duplicates[keys].head(5).to_dict(orient="records")
        raise AssertionError(f"{label} contains duplicate keys for {keys}: {sample}")


def assert_equal_row_count(sql: pd.DataFrame, candidate: pd.DataFrame, label: str, candidate_label: str) -> None:
    if len(sql) != len(candidate):
        raise AssertionError(f"{label} row counts differ. Spark SQL: {len(sql)}; {candidate_label}: {len(candidate)}")


def assert_numeric_close(merged: pd.DataFrame, columns: list[str], label: str, candidate_suffix: str) -> None:
    for column in columns:
        sql_col = f"{column}_sql"
        candidate_col = f"{column}_{candidate_suffix}"
        sql_values = pd.to_numeric(merged[sql_col], errors="coerce")
        candidate_values = pd.to_numeric(merged[candidate_col], errors="coerce")
        both_null = sql_values.isna() & candidate_values.isna()
        differences = (sql_values - candidate_values).abs()
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


def validate_delay(sql: pd.DataFrame, candidate: pd.DataFrame, *, technology: str, candidate_label: str) -> None:
    assert_columns(sql, DELAY_COLUMNS, "spark_sql delay_by_airport_month")
    assert_columns(candidate, DELAY_COLUMNS, f"{technology} delay_by_airport_month")
    assert_delay_range_domain(sql, "spark_sql delay_by_airport_month")
    assert_delay_range_domain(candidate, f"{technology} delay_by_airport_month")
    assert_cancellation_bucket_semantics(sql, "spark_sql delay_by_airport_month")
    assert_cancellation_bucket_semantics(candidate, f"{technology} delay_by_airport_month")
    assert_equal_row_count(sql, candidate, "delay_by_airport_month", candidate_label)
    assert_unique_keys(sql, DELAY_KEYS, "spark_sql delay_by_airport_month")
    assert_unique_keys(candidate, DELAY_KEYS, f"{technology} delay_by_airport_month")
    assert_key_sets_match(sql, candidate, DELAY_KEYS, "delay_by_airport_month", candidate_label)

    merged = sql.merge(candidate, on=DELAY_KEYS, suffixes=("_sql", f"_{technology}"), how="inner")
    assert_numeric_close(merged, DELAY_NUMERIC_COLUMNS, "delay_by_airport_month", technology)
    assert_string_columns_equal(merged, DELAY_CAUSE_COLUMNS, "sql", technology, "delay_by_airport_month")


def validate_all_causes(sql: pd.DataFrame, candidate: pd.DataFrame, *, technology: str, candidate_label: str) -> None:
    assert_columns(sql, ALL_CAUSES_COLUMNS, "spark_sql delay_by_airport_month_all_causes")
    assert_columns(candidate, ALL_CAUSES_COLUMNS, f"{technology} delay_by_airport_month_all_causes")
    assert_delay_range_domain(sql, "spark_sql delay_by_airport_month_all_causes")
    assert_delay_range_domain(candidate, f"{technology} delay_by_airport_month_all_causes")
    assert_all_causes_semantics(sql, "spark_sql delay_by_airport_month_all_causes")
    assert_all_causes_semantics(candidate, f"{technology} delay_by_airport_month_all_causes")
    assert_equal_row_count(sql, candidate, "delay_by_airport_month_all_causes", candidate_label)
    assert_unique_keys(sql, ALL_CAUSES_KEYS, "spark_sql delay_by_airport_month_all_causes")
    assert_unique_keys(candidate, ALL_CAUSES_KEYS, f"{technology} delay_by_airport_month_all_causes")
    assert_unique_keys(sql, ALL_CAUSES_RANK_KEYS, "spark_sql delay_by_airport_month_all_causes")
    assert_unique_keys(candidate, ALL_CAUSES_RANK_KEYS, f"{technology} delay_by_airport_month_all_causes")
    assert_key_sets_match(sql, candidate, ALL_CAUSES_KEYS, "delay_by_airport_month_all_causes", candidate_label)

    merged = sql.merge(candidate, on=ALL_CAUSES_KEYS, suffixes=("_sql", f"_{technology}"), how="inner")
    assert_numeric_close(merged, ALL_CAUSES_NUMERIC_COLUMNS, "delay_by_airport_month_all_causes", technology)


def assert_delay_range_domain(delay: pd.DataFrame, label: str) -> None:
    delay_ranges = set(delay["delay_range"].unique())
    if not delay_ranges <= ALLOWED_DELAY_RANGES:
        raise AssertionError(f"{label} has unexpected delay ranges: {sorted(delay_ranges)}")


def assert_cancellation_bucket_semantics(delay: pd.DataFrame, label: str) -> None:
    bucket = delay[delay["delay_range"] == CANCELLED_NO_DEPARTURE_DELAY_RANGE]
    if bucket.empty:
        raise AssertionError(f"{label} is missing {CANCELLED_NO_DEPARTURE_DELAY_RANGE}")
    if not bucket["avg_departure_delay"].isna().all():
        raise AssertionError(f"{label} cancellation bucket must have null avg_departure_delay")
    for cause_column, count_column in (
        ("top_1_cause", "top_1_count"),
        ("top_2_cause", "top_2_count"),
        ("top_3_cause", "top_3_count"),
    ):
        positive_count = pd.to_numeric(bucket[count_column], errors="coerce") > 0
        bad = positive_count & ~bucket[cause_column].fillna("").str.startswith("cancellation:")
        if bad.any():
            sample = bucket.loc[bad].head(3)
            raise AssertionError(f"{label} cancellation bucket has non-cancellation cause labels: {sample}")


def assert_all_causes_semantics(all_causes: pd.DataFrame, label: str) -> None:
    if all_causes.empty:
        raise AssertionError(f"{label} must contain at least one cause row")
    if all_causes["cause"].isna().any():
        raise AssertionError(f"{label} cause must not contain null values")

    cause_count = pd.to_numeric(all_causes["cause_count"], errors="coerce")
    if not (cause_count > 0).all():
        raise AssertionError(f"{label} cause_count values must be positive")

    cause_rank = pd.to_numeric(all_causes["cause_rank"], errors="coerce")
    if not (cause_rank >= 1).all():
        raise AssertionError(f"{label} cause_rank values must start at 1")

    valid_cause = all_causes["cause"].isin(ALLOWED_DELAY_CAUSES) | all_causes["cause"].str.startswith(
        "cancellation:", na=False
    )
    if not valid_cause.all():
        sample = all_causes.loc[~valid_cause].head(3)
        raise AssertionError(f"{label} has unexpected cause labels: {sample}")

    for key, group in all_causes.groupby(DELAY_KEYS, sort=False):
        comparable = group.copy()
        comparable["cause_count"] = pd.to_numeric(comparable["cause_count"], errors="coerce")
        comparable["cause_rank"] = pd.to_numeric(comparable["cause_rank"], errors="coerce")
        ordered = comparable.sort_values(["cause_count", "cause"], ascending=[False, True])
        expected_ranks = list(range(1, len(ordered) + 1))
        actual_ranks = ordered["cause_rank"].astype(int).tolist()
        if actual_ranks != expected_ranks:
            raise AssertionError(f"{label} ranks are not deterministic for {key}: {ordered.head(5)}")


def assert_ranking_order(ranking: pd.DataFrame, label: str) -> None:
    for origin_airport, group in ranking.groupby("origin_airport"):
        ordered = group.sort_values(["rank_at_airport", "avg_departure_delay", "airline"], na_position="last")
        delay_values = ordered["avg_departure_delay"].dropna().tolist()
        if delay_values != sorted(delay_values):
            raise AssertionError(f"{label} ranking is not ascending for {origin_airport}")

        tied = group.dropna(subset=["avg_departure_delay"]).groupby("avg_departure_delay")["rank_at_airport"].nunique()
        if (tied > 1).any():
            raise AssertionError(f"{label} equal average delays have different ranks for {origin_airport}")


def validate_ranking(sql: pd.DataFrame, candidate: pd.DataFrame, *, technology: str, candidate_label: str) -> None:
    assert_columns(sql, RANKING_COLUMNS, "spark_sql airline_airport_ranking")
    assert_columns(candidate, RANKING_COLUMNS, f"{technology} airline_airport_ranking")
    assert_equal_row_count(sql, candidate, "airline_airport_ranking", candidate_label)
    assert_unique_keys(sql, RANKING_KEYS, "spark_sql airline_airport_ranking")
    assert_unique_keys(candidate, RANKING_KEYS, f"{technology} airline_airport_ranking")
    assert_key_sets_match(sql, candidate, RANKING_KEYS, "airline_airport_ranking", candidate_label)

    merged = sql.merge(candidate, on=RANKING_KEYS, suffixes=("_sql", f"_{technology}"), how="inner")
    assert_numeric_close(merged, RANKING_NUMERIC_COLUMNS, "airline_airport_ranking", technology)

    assert_ranking_order(sql, "Spark SQL")
    assert_ranking_order(candidate, candidate_label)
