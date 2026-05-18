"""Prepare the canonical cleaned flight dataset with PySpark."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from pyspark import StorageLevel
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.column import Column


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.common.prepared_data import has_windows_winutils

LOCAL_CONFIG = PROJECT_ROOT / "config" / "local.yaml"
COLUMNS_CONFIG = PROJECT_ROOT / "config" / "columns.yaml"
METRICS_FILE_NAME = "preparation_metrics.json"

STRING_COLUMNS = {
    "airline_code",
    "airline_name",
    "origin_airport",
    "destination_airport",
    "cancellation_code",
}
INTEGER_COLUMNS = {"month", "cancelled", "diverted"}
DOUBLE_COLUMNS = {
    "departure_delay",
    "arrival_delay",
    "carrier_delay",
    "weather_delay",
    "nas_delay",
    "security_delay",
    "late_aircraft_delay",
}
REQUIRED_STRUCTURAL_COLUMNS = {
    "flight_date",
    "month",
    "airline_code",
    "origin_airport",
    "destination_airport",
    "cancelled",
    "diverted",
}


def run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, capture_output=True, text=True, check=False)


def java_major_version(java_command: Path | str) -> int | None:
    result = run_command([str(java_command), "-version"])
    output = result.stderr or result.stdout
    if result.returncode != 0:
        return None
    match = re.search(r'version "([^"]+)"', output)
    if not match:
        return None
    version_text = match.group(1)
    if version_text.startswith("1."):
        return int(version_text.split(".")[1])
    return int(version_text.split(".")[0])


def java_executable(java_home: Path) -> Path:
    executable = "java.exe" if os.name == "nt" else "java"
    return java_home / "bin" / executable


def candidate_java_homes() -> list[Path]:
    candidates: list[Path] = []
    java_home = os.environ.get("JAVA_HOME")
    if java_home:
        candidates.append(Path(java_home))

    if os.name == "nt":
        roots = [
            Path("C:/Program Files/Eclipse Adoptium"),
            Path("C:/Program Files/Java"),
            Path("C:/Program Files/Microsoft"),
            Path.home() / "AppData/Local/Programs/Eclipse Adoptium",
        ]
        for root in roots:
            if root.exists():
                candidates.extend(sorted(root.glob("jdk-*"), reverse=True))

    return candidates


def ensure_java_17() -> None:
    active_java = shutil.which("java")
    if active_java and (java_major_version(active_java) or 0) >= 17:
        return

    for java_home in candidate_java_homes():
        executable = java_executable(java_home)
        if executable.exists() and (java_major_version(executable) or 0) >= 17:
            os.environ["JAVA_HOME"] = str(java_home)
            os.environ["PATH"] = str(java_home / "bin") + os.pathsep + os.environ.get("PATH", "")
            return

    active_detail = active_java or "not found"
    raise RuntimeError(
        "PySpark requires Java 17 or newer for this project, but the active Java "
        f"runtime is {active_detail}. Install Java 17+ or set JAVA_HOME to a JDK 17+ directory."
    )


def clear_output_path(path: Path) -> None:
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()


def temporary_output_path(path: Path) -> Path:
    return path.parent / f".{path.name}.tmp"


def backup_output_path(path: Path) -> Path:
    return path.parent / f".{path.name}.bak"


def replace_output_from_temp(temp_path: Path, final_path: Path) -> None:
    backup_path = backup_output_path(final_path)
    clear_output_path(backup_path)

    if final_path.exists():
        shutil.move(str(final_path), str(backup_path))

    try:
        shutil.move(str(temp_path), str(final_path))
    except Exception:
        clear_output_path(final_path)
        if backup_path.exists():
            shutil.move(str(backup_path), str(final_path))
        raise
    else:
        clear_output_path(backup_path)


def write_parquet_with_pyarrow(df: DataFrame, output_path: Path, columns: list[str], batch_size: int = 100_000) -> None:
    import pyarrow as pa
    import pyarrow.parquet as pq

    arrow_schema = pa.schema(
        [
            pa.field("flight_date", pa.date32()),
            pa.field("month", pa.int32()),
            pa.field("airline_code", pa.string()),
            pa.field("airline_name", pa.string()),
            pa.field("origin_airport", pa.string()),
            pa.field("destination_airport", pa.string()),
            pa.field("departure_delay", pa.float64()),
            pa.field("arrival_delay", pa.float64()),
            pa.field("cancelled", pa.int32()),
            pa.field("diverted", pa.int32()),
            pa.field("cancellation_code", pa.string()),
            pa.field("carrier_delay", pa.float64()),
            pa.field("weather_delay", pa.float64()),
            pa.field("nas_delay", pa.float64()),
            pa.field("security_delay", pa.float64()),
            pa.field("late_aircraft_delay", pa.float64()),
        ]
    )

    clear_output_path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)
    part_file = output_path / "part-00000.parquet"

    writer: pq.ParquetWriter | None = None
    batch: dict[str, list[Any]] = {column: [] for column in columns}
    rows_in_batch = 0

    def flush_batch() -> None:
        nonlocal writer, batch, rows_in_batch
        if rows_in_batch == 0:
            return
        table = pa.table(batch, schema=arrow_schema)
        if writer is None:
            writer = pq.ParquetWriter(part_file, arrow_schema, compression="snappy")
        writer.write_table(table)
        batch = {column: [] for column in columns}
        rows_in_batch = 0

    try:
        for row in df.select(*columns).toLocalIterator():
            values = row.asDict(recursive=False)
            for column in columns:
                batch[column].append(values[column])
            rows_in_batch += 1
            if rows_in_batch >= batch_size:
                flush_batch()
        flush_batch()
    finally:
        if writer is not None:
            writer.close()
    (output_path / "_SUCCESS").touch()


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


def build_column_mapping(header: list[str], columns_config: dict[str, Any]) -> dict[str, str | None]:
    aliases = columns_config.get("aliases", {})
    canonical_columns = columns_config.get("canonical_columns", [])
    header_lookup = {name.lower(): name for name in header}

    mapping: dict[str, str | None] = {}
    for canonical in canonical_columns:
        source = None
        for candidate in aliases.get(canonical, []):
            source = header_lookup.get(str(candidate).lower())
            if source:
                break
        mapping[canonical] = source
    return mapping


def clean_string(column: Column) -> Column:
    trimmed = F.trim(column.cast("string"))
    return F.when(trimmed == "", F.lit(None)).otherwise(trimmed)


def canonical_expression(canonical: str, source: str | None) -> Column:
    if source is None:
        if canonical == "airline_name":
            return F.lit(None).cast("string").alias(canonical)
        raise ValueError(f"No source column found for required canonical column: {canonical}")

    source_column = clean_string(F.col(source))
    if canonical == "flight_date":
        return F.to_date(source_column).alias(canonical)
    if canonical in STRING_COLUMNS:
        return source_column.alias(canonical)
    if canonical in INTEGER_COLUMNS:
        return source_column.cast("integer").alias(canonical)
    if canonical in DOUBLE_COLUMNS:
        return source_column.cast("double").alias(canonical)
    raise ValueError(f"No type rule configured for canonical column: {canonical}")


def canonicalize(raw_df: DataFrame, columns_config: dict[str, Any]) -> tuple[DataFrame, dict[str, str | None]]:
    canonical_columns = columns_config.get("canonical_columns", [])
    if not isinstance(canonical_columns, list) or not canonical_columns:
        raise ValueError(f"{COLUMNS_CONFIG} must define a non-empty canonical_columns list")

    mapping = build_column_mapping(raw_df.columns, columns_config)
    expressions = [canonical_expression(str(column), mapping[str(column)]) for column in canonical_columns]
    return raw_df.select(*expressions), mapping


def structural_valid_condition() -> Column:
    required_not_null = [
        F.col(column).isNotNull()
        for column in REQUIRED_STRUCTURAL_COLUMNS
        if column not in {"cancelled", "diverted"}
    ]
    valid_flags = [F.col("cancelled").isin(0, 1), F.col("diverted").isin(0, 1)]

    condition = required_not_null[0]
    for next_condition in required_not_null[1:] + valid_flags:
        condition = condition & next_condition
    return condition


def null_count_expressions(columns: list[str]) -> list[Column]:
    return [
        F.sum(F.when(F.col(column).isNull(), F.lit(1)).otherwise(F.lit(0))).cast("long").alias(column)
        for column in columns
    ]


def one_row_metrics(df: DataFrame, expressions: list[Column]) -> dict[str, int | float | None]:
    row = df.agg(*expressions).first()
    if row is None:
        return {}
    return {key: row[key] for key in row.asDict()}


def count_nulls(df: DataFrame, columns: list[str]) -> dict[str, int]:
    result = one_row_metrics(df, null_count_expressions(columns))
    return {key: int(value or 0) for key, value in result.items()}


def count_invalid_rules(df: DataFrame) -> dict[str, int]:
    expressions = [
        F.sum(F.when(F.col("flight_date").isNull(), 1).otherwise(0)).cast("long").alias("missing_flight_date"),
        F.sum(F.when(F.col("month").isNull(), 1).otherwise(0)).cast("long").alias("missing_month"),
        F.sum(F.when(F.col("airline_code").isNull(), 1).otherwise(0)).cast("long").alias("missing_airline_code"),
        F.sum(F.when(F.col("origin_airport").isNull(), 1).otherwise(0)).cast("long").alias("missing_origin_airport"),
        F.sum(F.when(F.col("destination_airport").isNull(), 1).otherwise(0)).cast("long").alias("missing_destination_airport"),
        F.sum(F.when(~F.col("cancelled").isin(0, 1) | F.col("cancelled").isNull(), 1).otherwise(0))
        .cast("long")
        .alias("invalid_cancelled"),
        F.sum(F.when(~F.col("diverted").isin(0, 1) | F.col("diverted").isNull(), 1).otherwise(0))
        .cast("long")
        .alias("invalid_diverted"),
    ]
    result = one_row_metrics(df, expressions)
    return {key: int(value or 0) for key, value in result.items()}


def count_output_summary(df: DataFrame) -> dict[str, int]:
    expressions = [
        F.sum(F.when(F.col("cancelled") == 1, 1).otherwise(0)).cast("long").alias("cancelled_rows"),
        F.sum(F.when(F.col("diverted") == 1, 1).otherwise(0)).cast("long").alias("diverted_rows"),
        F.sum(F.when(F.col("departure_delay") < 0, 1).otherwise(0))
        .cast("long")
        .alias("negative_departure_delay_rows"),
        F.sum(F.when(F.col("arrival_delay") < 0, 1).otherwise(0)).cast("long").alias("negative_arrival_delay_rows"),
    ]
    result = one_row_metrics(df, expressions)
    return {key: int(value or 0) for key, value in result.items()}


def build_spark(local_config: dict[str, Any]) -> SparkSession:
    spark_config = local_config.get("spark", {})
    master = str(spark_config.get("master", "local[*]"))
    app_name = str(spark_config.get("app_name", "flight-delay-preparation"))
    shuffle_partitions = str(spark_config.get("shuffle_partitions", 8))

    return (
        SparkSession.builder.master(master)
        .appName(f"{app_name}-prepare")
        .config("spark.sql.shuffle.partitions", shuffle_partitions)
        .getOrCreate()
    )


def print_metrics(metrics: dict[str, Any]) -> None:
    print("# Preparation Metrics")
    print(json.dumps(metrics, indent=2, sort_keys=True))


def main() -> int:
    ensure_java_17()

    local_config = load_yaml(LOCAL_CONFIG)
    columns_config = load_yaml(COLUMNS_CONFIG)

    paths = local_config.get("paths", {})
    raw_file_value = paths.get("raw_file")
    prepared_file_value = paths.get("prepared_file")
    if not raw_file_value:
        raise ValueError(f"{LOCAL_CONFIG} does not define paths.raw_file")
    if not prepared_file_value:
        raise ValueError(f"{LOCAL_CONFIG} does not define paths.prepared_file")

    raw_file = resolve_project_path(str(raw_file_value))
    prepared_file = resolve_project_path(str(prepared_file_value))
    metrics_file = prepared_file.parent / METRICS_FILE_NAME

    if not raw_file.exists():
        raise FileNotFoundError(
            f"Configured raw dataset was not found: {raw_file}. "
            "Place the Kaggle CSV there or update config/local.yaml."
        )
    prepared_file.parent.mkdir(parents=True, exist_ok=True)

    spark = build_spark(local_config)
    try:
        raw_df = (
            spark.read.option("header", "true")
            .option("mode", "PERMISSIVE")
            .option("encoding", "UTF-8")
            .csv(str(raw_file))
        )
        input_rows = raw_df.count()

        canonical_df, mapping = canonicalize(raw_df, columns_config)
        canonical_df.persist(StorageLevel.DISK_ONLY)
        canonical_columns = [str(column) for column in columns_config["canonical_columns"]]
        null_counts_before = count_nulls(canonical_df, canonical_columns)
        invalid_rule_counts = count_invalid_rules(canonical_df)

        clean_df = canonical_df.where(structural_valid_condition())
        clean_df.persist(StorageLevel.DISK_ONLY)
        output_rows = clean_df.count()
        null_counts_after = count_nulls(clean_df, canonical_columns)
        output_summary = count_output_summary(clean_df)

        temp_prepared_file = temporary_output_path(prepared_file)
        clear_output_path(temp_prepared_file)
        if has_windows_winutils():
            clean_df.write.mode("error").parquet(str(temp_prepared_file))
            output_writer = "spark"
        else:
            write_parquet_with_pyarrow(clean_df, temp_prepared_file, canonical_columns)
            output_writer = "pyarrow_windows_local"
        replace_output_from_temp(temp_prepared_file, prepared_file)

        removed_rows = input_rows - output_rows
        metrics: dict[str, Any] = {
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "raw_file": str(raw_file.relative_to(PROJECT_ROOT)),
            "prepared_file": str(prepared_file.relative_to(PROJECT_ROOT)),
            "input_rows": input_rows,
            "output_rows": output_rows,
            "output_shape": "parquet_directory",
            "output_writer": output_writer,
            "removed_rows": removed_rows,
            "removed_row_percentage": round((removed_rows / input_rows) * 100, 6) if input_rows else 0,
            "canonical_mapping": mapping,
            "null_counts_before_cleaning": null_counts_before,
            "null_counts_after_cleaning": null_counts_after,
            "delay_null_counts_after_cleaning": {
                "departure_delay": null_counts_after["departure_delay"],
                "arrival_delay": null_counts_after["arrival_delay"],
            },
            "structural_invalid_rule_counts": invalid_rule_counts,
            **output_summary,
        }

        with metrics_file.open("w", encoding="utf-8") as file:
            json.dump(metrics, file, indent=2, sort_keys=True)
            file.write("\n")

        print_metrics(metrics)
        print(f"Prepared Parquet written to: {prepared_file.relative_to(PROJECT_ROOT)}")
        print(f"Preparation metrics written to: {metrics_file.relative_to(PROJECT_ROOT)}")
    finally:
        spark.stop()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
