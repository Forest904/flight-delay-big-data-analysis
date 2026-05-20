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
    "top_delay_or_cancellation_cause",
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

DELAY_SCHEMA = StructType(
    [
        StructField("origin_airport", StringType(), False),
        StructField("month", IntegerType(), False),
        StructField("delay_range", StringType(), False),
        StructField("flight_count", LongType(), False),
        StructField("avg_departure_delay", DoubleType(), True),
        StructField("avg_arrival_delay", DoubleType(), True),
        StructField("top_delay_or_cancellation_cause", StringType(), False),
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
        type=Path,
        help="Prepared Parquet input to analyze. Defaults to the selected config paths.prepared_file.",
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG, help="YAML config path.")
    return parser.parse_args(argv)


def resolve_project_path(path_value: str) -> Path:
    path = Path(path_value)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path


def spark_core_output_root(local_config: dict[str, Any]) -> Path:
    paths = local_config.get("paths", {})
    outputs_dir = resolve_project_path(str(paths.get("outputs_dir", "outputs")))
    return outputs_dir / "spark_core"


def metrics_file(output_root: Path) -> Path:
    return output_root / "runtime_metrics.json"


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def clear_path(path: Path) -> None:
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()


def clear_spark_core_outputs(output_root: Path) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    for child in output_root.iterdir():
        if child.name == ".gitkeep":
            continue
        clear_path(child)


def validate_preconditions(prepared_file: Path) -> list[str]:
    errors: list[str] = []
    if not prepared_file.exists():
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


def delay_accumulator(departure_delay: float, arrival_delay: float | None) -> tuple[int, float, int, float, int]:
    arrival_sum = 0.0 if arrival_delay is None else arrival_delay
    arrival_count = 0 if arrival_delay is None else 1
    return (1, departure_delay, 1, arrival_sum, arrival_count)


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


def ranged_delay_record(row: Any) -> tuple[tuple[str, int, str], tuple[float, float | None, str]] | None:
    departure_delay = to_float(row["departure_delay"])
    if departure_delay is None:
        return None

    key = (row["origin_airport"], int(row["month"]), delay_range(departure_delay))
    value = (departure_delay, to_float(row["arrival_delay"]), derived_cause(row))
    return key, value


def best_cause(left: tuple[str, int], right: tuple[str, int]) -> tuple[str, int]:
    left_cause, left_count = left
    right_cause, right_count = right
    if right_count > left_count:
        return right
    if right_count == left_count and right_cause < left_cause:
        return right
    return left


def delay_output_sort_key(row: tuple[str, int, str, int, float | None, float | None, str]) -> tuple[str, int, str]:
    return row[0], row[1], row[2]


def delay_report_df(spark: SparkSession, flights: DataFrame) -> DataFrame:
    partitions = rdd_partitions(spark)
    ranged = flights.rdd.map(ranged_delay_record).filter(lambda item: item is not None)

    grouped = ranged.map(
        lambda item: (
            item[0],
            delay_accumulator(item[1][0], item[1][1]),
        )
    ).reduceByKey(add_delay_accumulators, numPartitions=partitions)

    top_causes = (
        ranged.map(lambda item: ((item[0], item[1][2]), 1))
        .reduceByKey(lambda left, right: left + right, numPartitions=partitions)
        .map(lambda item: (item[0][0], (item[0][1], item[1])))
        .reduceByKey(best_cause, numPartitions=partitions)
    )

    rows = (
        grouped.join(top_causes)
        .map(
            lambda item: (
                item[0][0],
                item[0][1],
                item[0][2],
                item[1][0][0],
                sql_avg(item[1][0][1], item[1][0][2]),
                sql_avg(item[1][0][3], item[1][0][4]),
                item[1][1][0],
            )
        )
        .sortBy(delay_output_sort_key, numPartitions=partitions)
    )

    return spark.createDataFrame(rows, DELAY_SCHEMA).select(*DELAY_OUTPUT_COLUMNS)


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


def write_first_10_csv(df: DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows = df.limit(10).toPandas()
    rows.to_csv(output_path, index=False)


def write_full_csv(rows: Any, output_path: Path) -> None:
    clear_path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)
    rows.to_csv(output_path / "part-00000.csv", index=False)


def run_analysis(
    name: str,
    df: DataFrame,
    full_output_path: Path,
    sample_output_path: Path,
) -> dict[str, Any]:
    started = time.perf_counter()
    status = "success"
    error: str | None = None
    output_rows = 0

    try:
        rows = df.toPandas()
        output_rows = len(rows)
        write_full_csv(rows, full_output_path)
        sample_output_path.parent.mkdir(parents=True, exist_ok=True)
        rows.head(10).to_csv(sample_output_path, index=False)
    except Exception as exc:
        status = "failed"
        error = error_excerpt(exc)
    finally:
        duration_seconds = round(time.perf_counter() - started, 6)

    metrics: dict[str, Any] = {
        "job_name": name,
        "duration_seconds": duration_seconds,
        "output_rows": output_rows,
        "full_output_path": display_path(full_output_path),
        "sample_output_path": display_path(sample_output_path),
        "status": status,
    }
    if error is not None:
        metrics["error"] = error
    return metrics


def write_metrics(metrics: dict[str, Any], output_root: Path) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    with metrics_file(output_root).open("w", encoding="utf-8") as file:
        json.dump(metrics, file, indent=2, sort_keys=True)
        file.write("\n")


def error_excerpt(error: Exception | str, max_chars: int = 2000) -> str:
    text = str(error)
    if len(text) <= max_chars:
        return text
    return f"{text[:max_chars]}... [truncated]"


def mark_failed(metrics: dict[str, Any], stage: str, error: Exception | str) -> None:
    metrics["status"] = "failed"
    metrics["stage"] = stage
    metrics["error"] = error_excerpt(error)


def print_metrics(metrics: dict[str, Any], output_root: Path) -> None:
    print("# Spark Core Runtime Metrics")
    print(json.dumps(metrics, indent=2, sort_keys=True))
    print(f"Spark Core outputs written to: {display_path(output_root)}")


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

    prepared_file = args.input_path if args.input_path is not None else Path(str(prepared_file_value))
    if not prepared_file.is_absolute():
        prepared_file = PROJECT_ROOT / prepared_file
    output_root = spark_core_output_root(local_config)
    spark_config = local_config.get("spark", {})
    run_metrics: dict[str, Any] = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "technology": "spark_core",
        "status": "running",
        "stage": "preflight",
        "input_path": display_path(prepared_file),
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
        flights = read_prepared_parquet(spark, prepared_file)

        clear_spark_core_outputs(output_root)
        run_metrics["status"] = "running"
        run_metrics["stage"] = "analysis"
        write_metrics(run_metrics, output_root)

        analyses = [
            (
                "delay_by_airport_month",
                delay_report_df(spark, flights),
                output_root / "delay_by_airport_month" / "full",
                output_root / "delay_by_airport_month" / "first_10.csv",
            ),
            (
                "airline_airport_ranking",
                airline_airport_ranking_df(spark, flights),
                output_root / "airline_airport_ranking" / "full",
                output_root / "airline_airport_ranking" / "first_10.csv",
            ),
        ]

        for name, df, full_path, sample_path in analyses:
            run_metrics["stage"] = f"job:{name}"
            job_metrics = run_analysis(name, df, full_path, sample_path)
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
