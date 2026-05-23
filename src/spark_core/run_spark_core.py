"""Run the Spark Core RDD analyses for the flight delay project."""

from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.common.runtime import configure_pyspark_python, ensure_java_17
from src.common.timing import MATERIALIZATION_MODE_SMALL_RESULT, rounded_seconds, timed_call
from src.common.uri import (
    display_location,
    is_s3_uri,
    join_uri,
    location_exists,
    resolve_local_or_uri,
    write_json_location,
    write_text_location,
)


ensure_java_17()
PYSPARK_PYTHON = configure_pyspark_python()

from pyspark.rdd import RDD
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import (
    DoubleType,
    IntegerType,
    LongType,
    StringType,
    StructField,
    StructType,
)

from src.common.prepared_data import read_prepared_parquet


DEFAULT_CONFIG = PROJECT_ROOT / "config" / "local.yaml"

DELAY_OUTPUT_COLUMNS = [
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

ALL_CAUSES_OUTPUT_COLUMNS = [
    "origin_airport",
    "month",
    "delay_range",
    "cause_rank",
    "cause",
    "cause_count",
]

RANKING_OUTPUT_COLUMNS = [
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

CANCELLED_NO_DEPARTURE_DELAY_RANGE = "cancelled_no_departure_delay"
DELAY_RANGE_SORT_ORDER = {
    CANCELLED_NO_DEPARTURE_DELAY_RANGE: 0,
    "low": 1,
    "medium": 2,
    "high": 3,
}

DELAY_SCHEMA = StructType(
    [
        StructField("origin_airport", StringType(), False),
        StructField("month", IntegerType(), False),
        StructField("delay_range", StringType(), False),
        StructField("flight_count", LongType(), False),
        StructField("avg_departure_delay", DoubleType(), True),
        StructField("avg_arrival_delay", DoubleType(), True),
        StructField("top_1_cause", StringType(), True),
        StructField("top_1_count", LongType(), False),
        StructField("top_2_cause", StringType(), True),
        StructField("top_2_count", LongType(), False),
        StructField("top_3_cause", StringType(), True),
        StructField("top_3_count", LongType(), False),
    ]
)

ALL_CAUSES_SCHEMA = StructType(
    [
        StructField("origin_airport", StringType(), False),
        StructField("month", IntegerType(), False),
        StructField("delay_range", StringType(), False),
        StructField("cause_rank", IntegerType(), False),
        StructField("cause", StringType(), False),
        StructField("cause_count", LongType(), False),
    ]
)

RANKING_SCHEMA = StructType(
    [
        StructField("origin_airport", StringType(), False),
        StructField("airline", StringType(), False),
        StructField("flight_count", LongType(), False),
        StructField("avg_departure_delay", DoubleType(), True),
        StructField("avg_arrival_delay", DoubleType(), True),
        StructField("cancellation_rate", DoubleType(), False),
        StructField("airport_avg_departure_delay", DoubleType(), True),
        StructField("difference_from_airport_avg_departure_delay", DoubleType(), True),
        StructField("rank_at_airport", IntegerType(), False),
    ]
)


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)
    if not isinstance(data, dict):
        raise ValueError(f"{path} did not contain a YAML mapping")
    return data


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke-rdd", action="store_true", help="Run only the Spark Core RDD worker smoke check.")
    parser.add_argument(
        "--input-path",
        help="Prepared Parquet input to analyze. Defaults to the selected config paths.prepared_file.",
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG, help="YAML config path.")
    parser.add_argument(
        "--output-root",
        help="Technology output root. Defaults to <config paths.outputs_dir>/spark_core.",
    )
    return parser.parse_args(argv)


def resolve_project_path(path_value: str) -> Path:
    path = Path(path_value)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path


def spark_core_output_root(local_config: dict[str, Any]) -> str:
    paths = local_config.get("paths", {})
    outputs_dir = resolve_local_or_uri(str(paths.get("outputs_dir", "outputs")), PROJECT_ROOT)
    return join_uri(outputs_dir, "spark_core")


def metrics_file(output_root: str | Path) -> str:
    return join_uri(output_root, "runtime_metrics.json")


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def display_runtime_path(path: str | Path) -> str:
    return display_location(path, PROJECT_ROOT)


def clear_path(path: str | Path) -> None:
    if is_s3_uri(path):
        return
    local_path = Path(path)
    if local_path.is_dir():
        shutil.rmtree(local_path)
    elif local_path.exists():
        local_path.unlink()


def clear_spark_core_outputs(output_root: str | Path) -> None:
    if is_s3_uri(output_root):
        return
    local_root = Path(output_root)
    local_root.mkdir(parents=True, exist_ok=True)
    for child in local_root.iterdir():
        if child.name == ".gitkeep":
            continue
        clear_path(child)


def validate_preconditions(prepared_file: str | Path) -> list[str]:
    errors: list[str] = []
    if not location_exists(prepared_file):
        errors.append(
            f"Prepared dataset was not found: {prepared_file}. Run `make prepare` or `make generate-sizes` first."
        )
    return errors


def build_spark(local_config: dict[str, Any]) -> SparkSession:
    spark_config = local_config.get("spark", {})
    master = str(spark_config.get("master", "local[*]"))
    app_name = str(spark_config.get("app_name", "flight-delay-big-data-analysis-local"))
    shuffle_partitions = str(spark_config.get("shuffle_partitions", 8))

    builder = (
        SparkSession.builder.master(master)
        .appName(f"{app_name}-spark-core")
        .config("spark.sql.shuffle.partitions", shuffle_partitions)
        .config("spark.pyspark.python", PYSPARK_PYTHON)
        .config("spark.pyspark.driver.python", PYSPARK_PYTHON)
        .config("spark.python.worker.faulthandler.enabled", "true")
        .config("spark.sql.execution.pyspark.udf.faulthandler.enabled", "true")
    )
    if spark_config.get("driver_host"):
        builder = builder.config("spark.driver.host", str(spark_config["driver_host"]))
    if spark_config.get("driver_bind_address"):
        builder = builder.config("spark.driver.bindAddress", str(spark_config["driver_bind_address"]))
    return builder.getOrCreate()


def smoke_increment(value: int) -> int:
    return value + 1


def smoke_check_rdd_worker(spark: SparkSession) -> None:
    result = spark.sparkContext.parallelize([1], 1).map(smoke_increment).collect()
    if result != [2]:
        raise RuntimeError(f"Unexpected Spark Core RDD smoke-check result: {result}")


def rdd_partitions(spark: SparkSession) -> int:
    return int(spark.conf.get("spark.sql.shuffle.partitions", "8"))


def to_float(value: Any) -> float | None:
    if value is None:
        return None
    return float(value)


def sql_avg(total: float, count: int) -> float | None:
    if count == 0:
        return None
    return total / count


def nullable_number_sort_value(value: float | None) -> tuple[int, float]:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return (1, 0.0)
    return (0, value)


def delay_range(departure_delay: float) -> str:
    if departure_delay < 15:
        return "low"
    if departure_delay <= 60:
        return "medium"
    return "high"


def derived_cause(row: Any) -> str:
    cancellation_code = row["cancellation_code"]
    if row["cancelled"] == 1 and cancellation_code is not None:
        return f"cancellation:{cancellation_code}"

    causes = [
        ("delay:carrier", to_float(row["carrier_delay"]) or 0.0),
        ("delay:weather", to_float(row["weather_delay"]) or 0.0),
        ("delay:nas", to_float(row["nas_delay"]) or 0.0),
        ("delay:security", to_float(row["security_delay"]) or 0.0),
        ("delay:late_aircraft", to_float(row["late_aircraft_delay"]) or 0.0),
    ]
    cause, value = max(causes, key=lambda item: item[1])
    if value <= 0.0:
        return "unknown"
    return cause


def cancellation_cause(row: Any) -> str:
    cancellation_code = row["cancellation_code"]
    if cancellation_code is None:
        return "cancellation:unknown"
    return f"cancellation:{cancellation_code}"


def all_positive_causes(row: Any) -> list[str]:
    causes = []
    for label, column in (
        ("delay:carrier", "carrier_delay"),
        ("delay:weather", "weather_delay"),
        ("delay:nas", "nas_delay"),
        ("delay:security", "security_delay"),
        ("delay:late_aircraft", "late_aircraft_delay"),
    ):
        value = to_float(row[column]) or 0.0
        if value > 0.0:
            causes.append(label)

    cancellation_code = row["cancellation_code"]
    if row["cancelled"] == 1 and cancellation_code is not None:
        causes.append(f"cancellation:{cancellation_code}")
    return causes


def delay_accumulator(departure_delay: float | None, arrival_delay: float | None) -> tuple[int, float, int, float, int]:
    departure_sum = 0.0 if departure_delay is None else departure_delay
    departure_count = 0 if departure_delay is None else 1
    arrival_sum = 0.0 if arrival_delay is None else arrival_delay
    arrival_count = 0 if arrival_delay is None else 1
    return (1, departure_sum, departure_count, arrival_sum, arrival_count)


def add_delay_accumulators(
    left: tuple[int, float, int, float, int],
    right: tuple[int, float, int, float, int],
) -> tuple[int, float, int, float, int]:
    return (
        left[0] + right[0],
        left[1] + right[1],
        left[2] + right[2],
        left[3] + right[3],
        left[4] + right[4],
    )


def ranged_delay_record(row: Any) -> tuple[tuple[str, int, str], tuple[float | None, float | None, str]] | None:
    departure_delay = to_float(row["departure_delay"])
    if departure_delay is None:
        if row["cancelled"] != 1:
            return None
        key = (row["origin_airport"], int(row["month"]), CANCELLED_NO_DEPARTURE_DELAY_RANGE)
        return key, (None, to_float(row["arrival_delay"]), cancellation_cause(row))

    key = (row["origin_airport"], int(row["month"]), delay_range(departure_delay))
    value = (departure_delay, to_float(row["arrival_delay"]), derived_cause(row))
    return key, value


def all_causes_records(row: Any) -> list[tuple[tuple[tuple[str, int, str], str], int]]:
    departure_delay = to_float(row["departure_delay"])
    if departure_delay is None:
        if row["cancelled"] != 1:
            return []
        key = (row["origin_airport"], int(row["month"]), CANCELLED_NO_DEPARTURE_DELAY_RANGE)
    else:
        key = (row["origin_airport"], int(row["month"]), delay_range(departure_delay))

    return [((key, cause), 1) for cause in all_positive_causes(row)]


def top_three_causes(causes: list[tuple[str, int]]) -> tuple[str | None, int, str | None, int, str | None, int]:
    ordered = sorted(causes, key=lambda item: (-item[1], item[0]))
    padded: list[tuple[str | None, int]] = [(cause, count) for cause, count in ordered[:3]]
    while len(padded) < 3:
        padded.append((None, 0))
    return (
        padded[0][0],
        padded[0][1],
        padded[1][0],
        padded[1][1],
        padded[2][0],
        padded[2][1],
    )


def delay_output_sort_key(
    row: tuple[
        str,
        int,
        str,
        int,
        float | None,
        float | None,
        str | None,
        int,
        str | None,
        int,
        str | None,
        int,
    ],
) -> tuple[str, int, int, str]:
    return row[0], row[1], DELAY_RANGE_SORT_ORDER.get(row[2], 99), row[2]


def all_causes_rows_from_group(
    item: tuple[tuple[str, int, str], list[tuple[str, int]]],
) -> list[tuple[str, int, str, int, str, int]]:
    key, causes = item
    origin_airport, month, range_label = key
    ordered = sorted(causes, key=lambda cause: (-cause[1], cause[0]))
    return [
        (origin_airport, month, range_label, rank, cause, count)
        for rank, (cause, count) in enumerate(ordered, start=1)
    ]


def all_causes_output_sort_key(row: tuple[str, int, str, int, str, int]) -> tuple[str, int, int, str, int, str]:
    return row[0], row[1], DELAY_RANGE_SORT_ORDER.get(row[2], 99), row[2], row[3], row[4]


def delay_report_df(spark: SparkSession, flights: DataFrame) -> DataFrame:
    partitions = rdd_partitions(spark)
    ranged = flights.rdd.map(ranged_delay_record).filter(lambda item: item is not None)

    grouped = ranged.map(
        lambda item: (
            item[0],
            delay_accumulator(item[1][0], item[1][1]),
        )
    ).reduceByKey(add_delay_accumulators, numPartitions=partitions)

    cause_counts = (
        ranged.map(lambda item: ((item[0], item[1][2]), 1))
        .reduceByKey(lambda left, right: left + right, numPartitions=partitions)
        .map(lambda item: (item[0][0], (item[0][1], item[1])))
        .combineByKey(add_to_list, merge_value, merge_lists, numPartitions=partitions)
        .mapValues(top_three_causes)
    )

    rows = (
        grouped.join(cause_counts)
        .map(
            lambda item: (
                item[0][0],
                item[0][1],
                item[0][2],
                item[1][0][0],
                sql_avg(item[1][0][1], item[1][0][2]),
                sql_avg(item[1][0][3], item[1][0][4]),
                item[1][1][0],
                item[1][1][1],
                item[1][1][2],
                item[1][1][3],
                item[1][1][4],
                item[1][1][5],
            )
        )
        .sortBy(delay_output_sort_key, numPartitions=partitions)
    )

    return spark.createDataFrame(rows, DELAY_SCHEMA).select(*DELAY_OUTPUT_COLUMNS)


def delay_all_causes_df(spark: SparkSession, flights: DataFrame) -> DataFrame:
    partitions = rdd_partitions(spark)
    rows = (
        flights.rdd.flatMap(all_causes_records)
        .reduceByKey(lambda left, right: left + right, numPartitions=partitions)
        .map(lambda item: (item[0][0], (item[0][1], item[1])))
        .combineByKey(add_to_list, merge_value, merge_lists, numPartitions=partitions)
        .flatMap(all_causes_rows_from_group)
        .sortBy(all_causes_output_sort_key, numPartitions=partitions)
    )

    return spark.createDataFrame(rows, ALL_CAUSES_SCHEMA).select(*ALL_CAUSES_OUTPUT_COLUMNS)


def stats_accumulator(
    departure_delay: float | None,
    arrival_delay: float | None,
    cancelled: int,
) -> tuple[int, float, int, float, int, int]:
    departure_sum = 0.0 if departure_delay is None else departure_delay
    departure_count = 0 if departure_delay is None else 1
    arrival_sum = 0.0 if arrival_delay is None else arrival_delay
    arrival_count = 0 if arrival_delay is None else 1
    return (1, departure_sum, departure_count, arrival_sum, arrival_count, cancelled)


def add_stats_accumulators(
    left: tuple[int, float, int, float, int, int],
    right: tuple[int, float, int, float, int, int],
) -> tuple[int, float, int, float, int, int]:
    return (
        left[0] + right[0],
        left[1] + right[1],
        left[2] + right[2],
        left[3] + right[3],
        left[4] + right[4],
        left[5] + right[5],
    )


def airline_keyed_stats(row: Any) -> tuple[tuple[str, str], tuple[int, float, int, float, int, int]]:
    return (
        (row["origin_airport"], row["airline_code"]),
        stats_accumulator(
            to_float(row["departure_delay"]),
            to_float(row["arrival_delay"]),
            1 if row["cancelled"] == 1 else 0,
        ),
    )


def airport_keyed_departure(row: Any) -> tuple[str, tuple[float, int]]:
    departure_delay = to_float(row["departure_delay"])
    if departure_delay is None:
        return row["origin_airport"], (0.0, 0)
    return row["origin_airport"], (departure_delay, 1)


def add_departure_accumulators(left: tuple[float, int], right: tuple[float, int]) -> tuple[float, int]:
    return left[0] + right[0], left[1] + right[1]


def airline_stats_row(
    item: tuple[tuple[str, str], tuple[int, float, int, float, int, int]],
) -> tuple[str, tuple[str, int, float | None, float | None, float]]:
    (origin_airport, airline), stats = item
    flight_count, dep_sum, dep_count, arr_sum, arr_count, cancelled_count = stats
    return (
        origin_airport,
        (
            airline,
            flight_count,
            sql_avg(dep_sum, dep_count),
            sql_avg(arr_sum, arr_count),
            cancelled_count / flight_count,
        ),
    )


def add_to_list(value: Any) -> list[Any]:
    return [value]


def merge_value(values: list[Any], value: Any) -> list[Any]:
    values.append(value)
    return values


def merge_lists(left: list[Any], right: list[Any]) -> list[Any]:
    left.extend(right)
    return left


def rank_airlines_for_airport(
    item: tuple[str, tuple[float | None, list[tuple[str, int, float | None, float | None, float]]]],
) -> list[tuple[str, str, int, float | None, float | None, float, float | None, float | None, int]]:
    origin_airport, (airport_avg_departure_delay, airline_rows) = item
    ordered = sorted(
        airline_rows,
        key=lambda row: (nullable_number_sort_value(row[2]), row[0]),
    )

    ranked = []
    previous_delay_key: tuple[int, float] | None = None
    current_rank = 0
    for position, row in enumerate(ordered, start=1):
        airline, flight_count, avg_departure_delay, avg_arrival_delay, cancellation_rate = row
        delay_key = nullable_number_sort_value(avg_departure_delay)
        if delay_key != previous_delay_key:
            current_rank = position
            previous_delay_key = delay_key

        difference = None
        if avg_departure_delay is not None and airport_avg_departure_delay is not None:
            difference = avg_departure_delay - airport_avg_departure_delay

        ranked.append(
            (
                origin_airport,
                airline,
                flight_count,
                avg_departure_delay,
                avg_arrival_delay,
                cancellation_rate,
                airport_avg_departure_delay,
                difference,
                current_rank,
            )
        )
    return ranked


def ranking_output_sort_key(
    row: tuple[str, str, int, float | None, float | None, float, float | None, float | None, int],
) -> tuple[str, int, tuple[int, float], str]:
    return row[0], row[8], nullable_number_sort_value(row[3]), row[1]


def airline_airport_ranking_df(spark: SparkSession, flights: DataFrame) -> DataFrame:
    partitions = rdd_partitions(spark)
    airline_stats = (
        flights.rdd.map(airline_keyed_stats)
        .reduceByKey(add_stats_accumulators, numPartitions=partitions)
        .map(airline_stats_row)
    )

    airport_stats = (
        flights.rdd.map(airport_keyed_departure)
        .reduceByKey(add_departure_accumulators, numPartitions=partitions)
        .mapValues(lambda stats: sql_avg(stats[0], stats[1]))
    )

    airline_lists = airline_stats.combineByKey(add_to_list, merge_value, merge_lists, numPartitions=partitions)

    rows: RDD[tuple[str, str, int, float | None, float | None, float, float | None, float | None, int]] = (
        airport_stats.join(airline_lists)
        .flatMap(rank_airlines_for_airport)
        .sortBy(ranking_output_sort_key, numPartitions=partitions)
    )

    return spark.createDataFrame(rows, RANKING_SCHEMA).select(*RANKING_OUTPUT_COLUMNS)


def write_first_10_csv(df: DataFrame, output_path: str | Path) -> None:
    rows = df.limit(10).toPandas()
    if is_s3_uri(output_path):
        write_text_location(output_path, rows.to_csv(index=False))
        return
    local_path = Path(output_path)
    local_path.parent.mkdir(parents=True, exist_ok=True)
    rows.to_csv(local_path, index=False)


def write_full_csv(rows: Any, output_path: str | Path) -> None:
    clear_path(output_path)
    if is_s3_uri(output_path):
        write_text_location(join_uri(output_path, "part-00000.csv"), rows.to_csv(index=False))
        return
    local_path = Path(output_path)
    local_path.mkdir(parents=True, exist_ok=True)
    rows.to_csv(local_path / "part-00000.csv", index=False)


def run_analysis(
    name: str,
    df: DataFrame,
    full_output_path: str | Path,
    sample_output_path: str | Path,
    *,
    input_read_seconds: float,
    plan_build_seconds: float,
) -> dict[str, Any]:
    started = time.perf_counter()
    status = "success"
    error: str | None = None
    output_rows = 0
    result_collect_seconds: float | str = ""
    full_output_write_seconds: float | str = ""
    sample_output_write_seconds: float | str = ""

    try:
        rows, result_collect_seconds = timed_call(df.toPandas)
        output_rows = len(rows)
        _, full_output_write_seconds = timed_call(lambda: write_full_csv(rows, full_output_path))
        if is_s3_uri(sample_output_path):
            _, sample_output_write_seconds = timed_call(
                lambda: write_text_location(sample_output_path, rows.head(10).to_csv(index=False))
            )
        else:
            def write_local_sample() -> None:
                local_sample_path = Path(sample_output_path)
                local_sample_path.parent.mkdir(parents=True, exist_ok=True)
                rows.head(10).to_csv(local_sample_path, index=False)

            _, sample_output_write_seconds = timed_call(write_local_sample)
    except Exception as exc:
        status = "failed"
        error = error_excerpt(exc)
    finally:
        duration_seconds = round(time.perf_counter() - started, 6)

    metrics: dict[str, Any] = {
        "job_name": name,
        "duration_seconds": duration_seconds,
        "input_read_seconds": input_read_seconds,
        "plan_build_seconds": plan_build_seconds,
        "result_collect_seconds": result_collect_seconds,
        "full_output_write_seconds": full_output_write_seconds,
        "sample_output_write_seconds": sample_output_write_seconds,
        "materialization_mode": MATERIALIZATION_MODE_SMALL_RESULT,
        "output_rows": output_rows,
        "full_output_path": display_runtime_path(full_output_path),
        "sample_output_path": display_runtime_path(sample_output_path),
        "status": status,
    }
    if error is not None:
        metrics["error"] = error
    return metrics


def write_metrics(metrics: dict[str, Any], output_root: str | Path) -> None:
    write_json_location(metrics_file(output_root), metrics)


def error_excerpt(error: Exception | str, max_chars: int = 2000) -> str:
    text = str(error)
    if len(text) <= max_chars:
        return text
    return f"{text[:max_chars]}... [truncated]"


def mark_failed(metrics: dict[str, Any], stage: str, error: Exception | str) -> None:
    metrics["status"] = "failed"
    metrics["stage"] = stage
    metrics["error"] = error_excerpt(error)


def print_metrics(metrics: dict[str, Any], output_root: str | Path) -> None:
    print("# Spark Core Runtime Metrics")
    print(json.dumps(metrics, indent=2, sort_keys=True))
    print(f"Spark Core outputs written to: {display_runtime_path(output_root)}")


def docker_wsl_hint() -> str:
    return (
        "Native PySpark RDD worker startup failed. If this persists on Windows, "
        "run `make run-spark-core`, which uses the Docker-backed stable path on "
        "Windows. Use `make run-spark-core-native` only as a local diagnostics "
        "path. WSL can also be used with `make run-spark-core` from the mounted "
        "repository."
    )


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    config_path = args.config if args.config.is_absolute() else PROJECT_ROOT / args.config
    local_config = load_yaml(config_path)
    paths = local_config.get("paths", {})
    prepared_file_value = paths.get("prepared_file")
    if not prepared_file_value:
        raise ValueError(f"{config_path} does not define paths.prepared_file")

    prepared_file = resolve_local_or_uri(args.input_path or str(prepared_file_value), PROJECT_ROOT)
    output_root = resolve_local_or_uri(args.output_root, PROJECT_ROOT) if args.output_root else spark_core_output_root(local_config)
    spark_config = local_config.get("spark", {})
    run_metrics: dict[str, Any] = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "technology": "spark_core",
        "status": "running",
        "stage": "preflight",
        "input_path": display_runtime_path(prepared_file),
        "spark_master": str(spark_config.get("master", "local[*]")),
        "spark_shuffle_partitions": int(spark_config.get("shuffle_partitions", 8)),
        "pyspark_python": PYSPARK_PYTHON,
        "jobs": [],
    }

    preflight_errors = validate_preconditions(prepared_file)
    if preflight_errors:
        print("# Spark Core preflight failed", file=sys.stderr)
        for error in preflight_errors:
            print(f"- {error}", file=sys.stderr)
        mark_failed(run_metrics, "preflight", "; ".join(preflight_errors))
        write_metrics(run_metrics, output_root)
        print_metrics(run_metrics, output_root)
        return 1

    spark: SparkSession | None = None
    try:
        run_metrics["stage"] = "spark_create"
        spark = build_spark(local_config)

        run_metrics["stage"] = "rdd_worker_smoke"
        smoke_check_rdd_worker(spark)

        run_metrics["stage"] = "input_read"
        input_read_started = time.perf_counter()
        flights = read_prepared_parquet(spark, prepared_file)
        input_read_seconds = rounded_seconds(input_read_started)
        run_metrics["input_read_seconds"] = input_read_seconds

        clear_spark_core_outputs(output_root)
        run_metrics["status"] = "running"
        run_metrics["stage"] = "analysis"
        write_metrics(run_metrics, output_root)

        analyses = [
            (
                "delay_by_airport_month",
                lambda: delay_report_df(spark, flights),
                join_uri(output_root, "delay_by_airport_month", "full"),
                join_uri(output_root, "delay_by_airport_month", "first_10.csv"),
            ),
            (
                "delay_by_airport_month_all_causes",
                lambda: delay_all_causes_df(spark, flights),
                join_uri(output_root, "delay_by_airport_month_all_causes", "full"),
                join_uri(output_root, "delay_by_airport_month_all_causes", "first_10.csv"),
            ),
            (
                "airline_airport_ranking",
                lambda: airline_airport_ranking_df(spark, flights),
                join_uri(output_root, "airline_airport_ranking", "full"),
                join_uri(output_root, "airline_airport_ranking", "first_10.csv"),
            ),
        ]

        for name, build_df, full_path, sample_path in analyses:
            run_metrics["stage"] = f"job:{name}"
            df, plan_build_seconds = timed_call(build_df)
            job_metrics = run_analysis(
                name,
                df,
                full_path,
                sample_path,
                input_read_seconds=input_read_seconds,
                plan_build_seconds=plan_build_seconds,
            )
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
        stage = str(run_metrics.get("stage", "unknown"))
        mark_failed(run_metrics, stage, exc)
        if stage == "rdd_worker_smoke":
            run_metrics["fallback_hint"] = docker_wsl_hint()
            print(f"# {docker_wsl_hint()}", file=sys.stderr)
    finally:
        if spark is not None:
            spark.stop()

    write_metrics(run_metrics, output_root)
    print_metrics(run_metrics, output_root)
    return 0 if run_metrics["status"] == "success" else 1


def smoke_main() -> int:
    args = parse_args()
    config_path = args.config if args.config.is_absolute() else PROJECT_ROOT / args.config
    local_config = load_yaml(config_path)
    spark: SparkSession | None = None
    try:
        spark = build_spark(local_config)
        smoke_check_rdd_worker(spark)
    except Exception as exc:
        print(f"# Spark Core RDD smoke check failed: {exc}", file=sys.stderr)
        print(f"# {docker_wsl_hint()}", file=sys.stderr)
        return 1
    finally:
        if spark is not None:
            spark.stop()
    print("Spark Core RDD smoke check passed")
    return 0


if __name__ == "__main__":
    args = parse_args()
    if args.smoke_rdd:
        raise SystemExit(smoke_main())
    raise SystemExit(main(sys.argv[1:]))
