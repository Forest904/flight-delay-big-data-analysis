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
from pyspark import StorageLevel
from pyspark.sql import DataFrame, SparkSession


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.common.prepared_data import has_windows_winutils, read_prepared_parquet
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


def spark_sql_output_root(local_config: dict[str, Any]) -> Path:
    paths = local_config.get("paths", {})
    outputs_dir = resolve_project_path(str(paths.get("outputs_dir", "outputs")))
    return outputs_dir / "spark_sql"


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


def clear_spark_sql_outputs(output_root: Path) -> None:
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
    if not has_windows_winutils():
        errors.append(
            "Spark SQL CSV output on Windows requires Hadoop `winutils.exe`. "
            "Install Hadoop native tools and set HADOOP_HOME or hadoop.home.dir so "
            "`bin\\winutils.exe` is discoverable, then retry `make run-spark-sql`."
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
        """
        WITH ranged AS (
            SELECT
                origin_airport,
                month,
                departure_delay,
                arrival_delay,
                CASE
                    WHEN departure_delay < 15 THEN 'low'
                    WHEN departure_delay >= 15 AND departure_delay <= 60 THEN 'medium'
                    WHEN departure_delay > 60 THEN 'high'
                END AS delay_range,
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
                END AS derived_cause
            FROM flights
            WHERE departure_delay IS NOT NULL
        ),
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
        ranked_causes AS (
            SELECT
                origin_airport,
                month,
                delay_range,
                derived_cause,
                cause_count,
                row_number() OVER (
                    PARTITION BY origin_airport, month, delay_range
                    ORDER BY cause_count DESC, derived_cause ASC
                ) AS cause_rank
            FROM cause_counts
        ),
        top_causes AS (
            SELECT
                origin_airport,
                month,
                delay_range,
                max(CASE WHEN cause_rank = 1 THEN derived_cause END) AS top_1_cause,
                coalesce(max(CASE WHEN cause_rank = 1 THEN cause_count END), 0) AS top_1_count,
                max(CASE WHEN cause_rank = 2 THEN derived_cause END) AS top_2_cause,
                coalesce(max(CASE WHEN cause_rank = 2 THEN cause_count END), 0) AS top_2_count,
                max(CASE WHEN cause_rank = 3 THEN derived_cause END) AS top_3_cause,
                coalesce(max(CASE WHEN cause_rank = 3 THEN cause_count END), 0) AS top_3_count
            FROM ranked_causes
            WHERE cause_rank <= 3
            GROUP BY origin_airport, month, delay_range
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
        ORDER BY grouped.origin_airport, grouped.month, grouped.delay_range
        """
    ).select(*DELAY_OUTPUT_COLUMNS)


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


def write_first_10_csv(df: DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows = df.limit(10).toPandas()
    rows.to_csv(output_path, index=False)


def write_full_csv(df: DataFrame, output_path: Path) -> None:
    clear_path(output_path)
    (
        df.write.mode("error")
        .option("header", "true")
        .csv(str(output_path))
    )


def run_analysis(
    name: str,
    df: DataFrame,
    full_output_path: Path,
    sample_output_path: Path,
) -> dict[str, Any]:
    started = time.perf_counter()
    persisted = df.persist(StorageLevel.MEMORY_AND_DISK)
    status = "success"
    error: str | None = None
    output_rows = 0

    try:
        output_rows = persisted.count()
        write_full_csv(persisted, full_output_path)
        write_first_10_csv(persisted, sample_output_path)
    except Exception as exc:
        status = "failed"
        error = str(exc)
    finally:
        duration_seconds = round(time.perf_counter() - started, 6)
        persisted.unpersist()

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


def print_metrics(metrics: dict[str, Any], output_root: Path) -> None:
    print("# Spark SQL Runtime Metrics")
    print(json.dumps(metrics, indent=2, sort_keys=True))
    print(f"Spark SQL outputs written to: {display_path(output_root)}")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    ensure_java_17()

    config_path = args.config if args.config.is_absolute() else PROJECT_ROOT / args.config
    local_config = load_yaml(config_path)
    paths = local_config.get("paths", {})
    prepared_file_value = paths.get("prepared_file")
    if not prepared_file_value:
        raise ValueError(f"{config_path} does not define paths.prepared_file")

    prepared_file = args.input_path if args.input_path is not None else Path(str(prepared_file_value))
    if not prepared_file.is_absolute():
        prepared_file = PROJECT_ROOT / prepared_file
    output_root = spark_sql_output_root(local_config)
    spark_config = local_config.get("spark", {})
    run_metrics: dict[str, Any] = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "technology": "spark_sql",
        "status": "running",
        "stage": "preflight",
        "input_path": display_path(prepared_file),
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
        flights = read_prepared_parquet(spark, prepared_file)
        flights.createOrReplaceTempView("flights")

        analyses = [
            (
                "delay_by_airport_month",
                delay_report_query(spark),
                output_root / "delay_by_airport_month" / "full",
                output_root / "delay_by_airport_month" / "first_10.csv",
            ),
            (
                "airline_airport_ranking",
                airline_airport_ranking_query(spark),
                output_root / "airline_airport_ranking" / "full",
                output_root / "airline_airport_ranking" / "first_10.csv",
            ),
        ]

        for name, df, full_path, sample_path in analyses:
            run_metrics["stage"] = f"job:{name}"
            job_metrics = run_analysis(name, df, full_path, sample_path)
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
