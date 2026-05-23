"""Run the Spark SQL reference analyses for the flight delay project."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from pyspark.sql import DataFrame, SparkSession


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.common.prepared_data import read_prepared_parquet
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
from src.preparation.prepare_spark import ensure_java_17


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

DELAY_RANGE_SQL = """
CASE
    WHEN departure_delay < 15 THEN 'low'
    WHEN departure_delay >= 15 AND departure_delay <= 60 THEN 'medium'
    WHEN departure_delay > 60 THEN 'high'
END
"""

DERIVED_CAUSE_SQL = """
CASE
    WHEN cancelled = 1 AND cancellation_code IS NOT NULL
        THEN concat('cancellation:', cancellation_code)
    WHEN greatest(
        coalesce(carrier_delay, 0.0),
        coalesce(weather_delay, 0.0),
        coalesce(nas_delay, 0.0),
        coalesce(security_delay, 0.0),
        coalesce(late_aircraft_delay, 0.0)
    ) <= 0.0
        THEN 'unknown'
    WHEN coalesce(carrier_delay, 0.0) >= coalesce(weather_delay, 0.0)
        AND coalesce(carrier_delay, 0.0) >= coalesce(nas_delay, 0.0)
        AND coalesce(carrier_delay, 0.0) >= coalesce(security_delay, 0.0)
        AND coalesce(carrier_delay, 0.0) >= coalesce(late_aircraft_delay, 0.0)
        THEN 'delay:carrier'
    WHEN coalesce(weather_delay, 0.0) >= coalesce(nas_delay, 0.0)
        AND coalesce(weather_delay, 0.0) >= coalesce(security_delay, 0.0)
        AND coalesce(weather_delay, 0.0) >= coalesce(late_aircraft_delay, 0.0)
        THEN 'delay:weather'
    WHEN coalesce(nas_delay, 0.0) >= coalesce(security_delay, 0.0)
        AND coalesce(nas_delay, 0.0) >= coalesce(late_aircraft_delay, 0.0)
        THEN 'delay:nas'
    WHEN coalesce(security_delay, 0.0) >= coalesce(late_aircraft_delay, 0.0)
        THEN 'delay:security'
    ELSE 'delay:late_aircraft'
END
"""


def ranged_flights_cte() -> str:
    return f"""
        ranged AS (
            SELECT
                origin_airport,
                month,
                departure_delay,
                arrival_delay,
                cancelled,
                cancellation_code,
                carrier_delay,
                weather_delay,
                nas_delay,
                security_delay,
                late_aircraft_delay,
                {DELAY_RANGE_SQL} AS delay_range,
                {DERIVED_CAUSE_SQL} AS derived_cause
            FROM flights
            WHERE departure_delay IS NOT NULL
            UNION ALL
            SELECT
                origin_airport,
                month,
                departure_delay,
                arrival_delay,
                cancelled,
                cancellation_code,
                carrier_delay,
                weather_delay,
                nas_delay,
                security_delay,
                late_aircraft_delay,
                'cancelled_no_departure_delay' AS delay_range,
                concat('cancellation:', coalesce(cancellation_code, 'unknown')) AS derived_cause
            FROM flights
            WHERE cancelled = 1 AND departure_delay IS NULL
        )
    """


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)
    if not isinstance(data, dict):
        raise ValueError(f"{path} did not contain a YAML mapping")
    return data


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-path",
        help="Prepared Parquet input to analyze. Defaults to the selected config paths.prepared_file.",
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG, help="YAML config path.")
    parser.add_argument(
        "--output-root",
        help="Technology output root. Defaults to <config paths.outputs_dir>/spark_sql.",
    )
    return parser.parse_args(argv)


def resolve_project_path(path_value: str) -> Path:
    path = Path(path_value)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path


def spark_sql_output_root(local_config: dict[str, Any]) -> str:
    paths = local_config.get("paths", {})
    outputs_dir = resolve_local_or_uri(str(paths.get("outputs_dir", "outputs")), PROJECT_ROOT)
    return join_uri(outputs_dir, "spark_sql")


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


def clear_spark_sql_outputs(output_root: str | Path) -> None:
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
        .appName(f"{app_name}-spark-sql")
        .config("spark.sql.shuffle.partitions", shuffle_partitions)
    )
    if spark_config.get("driver_host"):
        builder = builder.config("spark.driver.host", str(spark_config["driver_host"]))
    if spark_config.get("driver_bind_address"):
        builder = builder.config("spark.driver.bindAddress", str(spark_config["driver_bind_address"]))
    return builder.getOrCreate()


def delay_report_query(spark: SparkSession) -> DataFrame:
    return spark.sql(
        f"""
        WITH {ranged_flights_cte()},
        grouped AS (
            SELECT
                origin_airport,
                month,
                delay_range,
                count(*) AS flight_count,
                avg(departure_delay) AS avg_departure_delay,
                avg(arrival_delay) AS avg_arrival_delay
            FROM ranged
            GROUP BY origin_airport, month, delay_range
        ),
        cause_counts AS (
            SELECT
                origin_airport,
                month,
                delay_range,
                derived_cause,
                count(*) AS cause_count
            FROM ranged
            GROUP BY origin_airport, month, delay_range, derived_cause
        ),
        top_cause_groups AS (
            SELECT
                origin_airport,
                month,
                delay_range,
                sort_array(
                    collect_list(
                        named_struct(
                            'sort_count', -cause_count,
                            'cause', derived_cause,
                            'cause_count', cause_count
                        )
                    )
                ) AS causes
            FROM cause_counts
            GROUP BY origin_airport, month, delay_range
        ),
        top_causes AS (
            SELECT
                origin_airport,
                month,
                delay_range,
                get(causes, 0).cause AS top_1_cause,
                coalesce(get(causes, 0).cause_count, 0) AS top_1_count,
                get(causes, 1).cause AS top_2_cause,
                coalesce(get(causes, 1).cause_count, 0) AS top_2_count,
                get(causes, 2).cause AS top_3_cause,
                coalesce(get(causes, 2).cause_count, 0) AS top_3_count
            FROM top_cause_groups
        )
        SELECT
            grouped.origin_airport,
            grouped.month,
            grouped.delay_range,
            grouped.flight_count,
            grouped.avg_departure_delay,
            grouped.avg_arrival_delay,
            top_causes.top_1_cause,
            coalesce(top_causes.top_1_count, 0) AS top_1_count,
            top_causes.top_2_cause,
            coalesce(top_causes.top_2_count, 0) AS top_2_count,
            top_causes.top_3_cause,
            coalesce(top_causes.top_3_count, 0) AS top_3_count
        FROM grouped
        LEFT JOIN top_causes
            ON grouped.origin_airport = top_causes.origin_airport
            AND grouped.month = top_causes.month
            AND grouped.delay_range = top_causes.delay_range
        ORDER BY
            grouped.origin_airport,
            grouped.month,
            CASE grouped.delay_range
                WHEN 'cancelled_no_departure_delay' THEN 0
                WHEN 'low' THEN 1
                WHEN 'medium' THEN 2
                WHEN 'high' THEN 3
                ELSE 4
            END,
            grouped.delay_range
        """
    ).select(*DELAY_OUTPUT_COLUMNS)


def delay_all_causes_query(spark: SparkSession) -> DataFrame:
    return spark.sql(
        f"""
        WITH {ranged_flights_cte()},
        cause_events AS (
            SELECT origin_airport, month, delay_range, 'delay:carrier' AS cause
            FROM ranged
            WHERE coalesce(carrier_delay, 0.0) > 0.0
            UNION ALL
            SELECT origin_airport, month, delay_range, 'delay:weather' AS cause
            FROM ranged
            WHERE coalesce(weather_delay, 0.0) > 0.0
            UNION ALL
            SELECT origin_airport, month, delay_range, 'delay:nas' AS cause
            FROM ranged
            WHERE coalesce(nas_delay, 0.0) > 0.0
            UNION ALL
            SELECT origin_airport, month, delay_range, 'delay:security' AS cause
            FROM ranged
            WHERE coalesce(security_delay, 0.0) > 0.0
            UNION ALL
            SELECT origin_airport, month, delay_range, 'delay:late_aircraft' AS cause
            FROM ranged
            WHERE coalesce(late_aircraft_delay, 0.0) > 0.0
            UNION ALL
            SELECT origin_airport, month, delay_range, concat('cancellation:', cancellation_code) AS cause
            FROM ranged
            WHERE cancelled = 1 AND cancellation_code IS NOT NULL
        ),
        cause_counts AS (
            SELECT
                origin_airport,
                month,
                delay_range,
                cause,
                count(*) AS cause_count
            FROM cause_events
            GROUP BY origin_airport, month, delay_range, cause
        ),
        ranked_groups AS (
            SELECT
                origin_airport,
                month,
                delay_range,
                sort_array(
                    collect_list(
                        named_struct(
                            'sort_count', -cause_count,
                            'cause', cause,
                            'cause_count', cause_count
                        )
                    )
                ) AS causes
            FROM cause_counts
            GROUP BY origin_airport, month, delay_range
        ),
        ranked AS (
            SELECT
                origin_airport,
                month,
                delay_range,
                rank_index + 1 AS cause_rank,
                cause_record.cause AS cause,
                cause_record.cause_count AS cause_count
            FROM ranked_groups
            LATERAL VIEW posexplode(causes) exploded AS rank_index, cause_record
        )
        SELECT
            origin_airport,
            month,
            delay_range,
            cause_rank,
            cause,
            cause_count
        FROM ranked
        ORDER BY
            origin_airport,
            month,
            CASE delay_range
                WHEN 'cancelled_no_departure_delay' THEN 0
                WHEN 'low' THEN 1
                WHEN 'medium' THEN 2
                WHEN 'high' THEN 3
                ELSE 4
            END,
            delay_range,
            cause_rank,
            cause
        """
    ).select(*ALL_CAUSES_OUTPUT_COLUMNS)


def airline_airport_ranking_query(spark: SparkSession) -> DataFrame:
    return spark.sql(
        """
        WITH airline_stats AS (
            SELECT
                origin_airport,
                airline_code AS airline,
                count(*) AS flight_count,
                avg(departure_delay) AS avg_departure_delay,
                avg(arrival_delay) AS avg_arrival_delay,
                sum(CASE WHEN cancelled = 1 THEN 1 ELSE 0 END) / count(*) AS cancellation_rate
            FROM flights
            GROUP BY origin_airport, airline_code
        ),
        airport_stats AS (
            SELECT
                origin_airport,
                avg(departure_delay) AS airport_avg_departure_delay
            FROM flights
            GROUP BY origin_airport
        ),
        ranked AS (
            SELECT
                airline_stats.origin_airport,
                airline_stats.airline,
                airline_stats.flight_count,
                airline_stats.avg_departure_delay,
                airline_stats.avg_arrival_delay,
                airline_stats.cancellation_rate,
                airport_stats.airport_avg_departure_delay,
                airline_stats.avg_departure_delay - airport_stats.airport_avg_departure_delay
                AS difference_from_airport_avg_departure_delay,
                rank() OVER (
                    PARTITION BY airline_stats.origin_airport
                    ORDER BY airline_stats.avg_departure_delay ASC NULLS LAST
                ) AS rank_at_airport
            FROM airline_stats
            INNER JOIN airport_stats
                ON airline_stats.origin_airport = airport_stats.origin_airport
        )
        SELECT
            origin_airport,
            airline,
            flight_count,
            avg_departure_delay,
            avg_arrival_delay,
            cancellation_rate,
            airport_avg_departure_delay,
            difference_from_airport_avg_departure_delay,
            rank_at_airport
        FROM ranked
        ORDER BY origin_airport, rank_at_airport, avg_departure_delay ASC NULLS LAST, airline
        """
    ).select(*RANKING_OUTPUT_COLUMNS)


def write_first_10_csv(rows: Any, output_path: str | Path) -> None:
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
        _, sample_output_write_seconds = timed_call(lambda: write_first_10_csv(rows.head(10), sample_output_path))
    except Exception as exc:
        status = "failed"
        error = str(exc)
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


def print_metrics(metrics: dict[str, Any], output_root: str | Path) -> None:
    print("# Spark SQL Runtime Metrics")
    print(json.dumps(metrics, indent=2, sort_keys=True))
    print(f"Spark SQL outputs written to: {display_runtime_path(output_root)}")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    ensure_java_17()

    config_path = args.config if args.config.is_absolute() else PROJECT_ROOT / args.config
    local_config = load_yaml(config_path)
    paths = local_config.get("paths", {})
    prepared_file_value = paths.get("prepared_file")
    if not prepared_file_value:
        raise ValueError(f"{config_path} does not define paths.prepared_file")

    prepared_file = resolve_local_or_uri(args.input_path or str(prepared_file_value), PROJECT_ROOT)
    output_root = resolve_local_or_uri(args.output_root, PROJECT_ROOT) if args.output_root else spark_sql_output_root(local_config)
    spark_config = local_config.get("spark", {})
    run_metrics: dict[str, Any] = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "technology": "spark_sql",
        "status": "running",
        "stage": "preflight",
        "input_path": display_runtime_path(prepared_file),
        "spark_master": str(spark_config.get("master", "local[*]")),
        "spark_shuffle_partitions": int(spark_config.get("shuffle_partitions", 8)),
        "jobs": [],
    }

    preflight_errors = validate_preconditions(prepared_file)
    if preflight_errors:
        print("# Spark SQL preflight failed", file=sys.stderr)
        for error in preflight_errors:
            print(f"- {error}", file=sys.stderr)
        run_metrics["status"] = "failed"
        run_metrics["error"] = "; ".join(preflight_errors)
        write_metrics(run_metrics, output_root)
        print_metrics(run_metrics, output_root)
        return 1

    clear_spark_sql_outputs(output_root)
    spark: SparkSession | None = None

    try:
        run_metrics["stage"] = "spark_create"
        spark = build_spark(local_config)

        run_metrics["stage"] = "input_read"
        input_read_started = time.perf_counter()
        flights = read_prepared_parquet(spark, prepared_file)
        flights.createOrReplaceTempView("flights")
        input_read_seconds = rounded_seconds(input_read_started)
        run_metrics["input_read_seconds"] = input_read_seconds

        analyses = [
            (
                "delay_by_airport_month",
                lambda: delay_report_query(spark),
                join_uri(output_root, "delay_by_airport_month", "full"),
                join_uri(output_root, "delay_by_airport_month", "first_10.csv"),
            ),
            (
                "delay_by_airport_month_all_causes",
                lambda: delay_all_causes_query(spark),
                join_uri(output_root, "delay_by_airport_month_all_causes", "full"),
                join_uri(output_root, "delay_by_airport_month_all_causes", "first_10.csv"),
            ),
            (
                "airline_airport_ranking",
                lambda: airline_airport_ranking_query(spark),
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
            if job_metrics["status"] != "success":
                run_metrics["status"] = "failed"
                run_metrics["error"] = job_metrics.get("error")
                break
        else:
            run_metrics["status"] = "success"
            run_metrics["stage"] = "complete"
    except Exception as exc:
        run_metrics["status"] = "failed"
        run_metrics["error"] = str(exc)
    finally:
        if spark is not None:
            spark.stop()

    write_metrics(run_metrics, output_root)
    print_metrics(run_metrics, output_root)
    return 0 if run_metrics["status"] == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())
