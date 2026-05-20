"""Generate controlled Parquet input sizes for scalability benchmarks."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DEFAULT_CONFIG = PROJECT_ROOT / "config" / "local.yaml"
DEFAULT_SEED = 20_240_520
MANIFEST_FILE_NAME = "input_size_manifest.json"

DEFAULT_SIZE_SPECS: tuple[tuple[str, int], ...] = (
    ("100k", 100_000),
    ("500k", 500_000),
    ("1m", 1_000_000),
    ("3m", 3_000_000),
)
LARGE_SIZE_SPECS: tuple[tuple[str, int], ...] = (
    ("14m", 14_000_000),
    ("28m", 28_000_000),
)


@dataclass(frozen=True)
class SizeSpec:
    label: str
    records: int


@dataclass(frozen=True)
class ReplicationPlan:
    full_repetitions: int
    remainder_records: int


def selected_size_specs(include_large: bool) -> list[SizeSpec]:
    specs = [SizeSpec(label, records) for label, records in DEFAULT_SIZE_SPECS]
    if include_large:
        specs.extend(SizeSpec(label, records) for label, records in LARGE_SIZE_SPECS)
    return specs


def replication_plan(target_records: int, base_records: int) -> ReplicationPlan:
    if target_records < 0:
        raise ValueError("target_records must be non-negative")
    if base_records <= 0:
        raise ValueError("base_records must be positive")
    return ReplicationPlan(
        full_repetitions=target_records // base_records,
        remainder_records=target_records % base_records,
    )


def validate_manifest_entry(entry: dict[str, Any]) -> None:
    target_records = int(entry["target_records"])
    actual_records = int(entry["actual_records"])
    if target_records != actual_records:
        raise ValueError(
            f"{entry.get('label', 'unknown')} expected {target_records} records "
            f"but validation counted {actual_records}"
        )
    if entry.get("schema_matches_source") is not True:
        raise ValueError(f"{entry.get('label', 'unknown')} schema does not match source schema")
    if entry.get("validation_status") != "success":
        raise ValueError(f"{entry.get('label', 'unknown')} validation did not succeed")


def successful_manifest_labels(manifest: dict[str, Any]) -> set[str]:
    datasets = manifest.get("datasets", [])
    if not isinstance(datasets, list):
        return set()
    return {
        str(entry.get("label"))
        for entry in datasets
        if isinstance(entry, dict) and entry.get("validation_status") == "success"
    }


def benchmark_inputs_for_manifest(local_config: dict[str, Any], manifest: dict[str, Any]) -> list[dict[str, Any]]:
    input_sizes = local_config.get("benchmark", {}).get("input_sizes", [])
    if not isinstance(input_sizes, list):
        return []
    manifest_labels = successful_manifest_labels(manifest)
    selected: list[dict[str, Any]] = []
    for entry in input_sizes:
        if not isinstance(entry, dict):
            continue
        label = str(entry.get("label"))
        if not entry.get("optional", False) or label in manifest_labels:
            selected.append(entry)
    return selected


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


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def load_previous_manifest(generated_dir: Path) -> dict[str, Any] | None:
    manifest_path = generated_dir / MANIFEST_FILE_NAME
    if not manifest_path.exists():
        return None
    with manifest_path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise ValueError(f"{display_path(manifest_path)} did not contain a JSON object")
    return data


def previous_manifest_entries_by_label(manifest: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    if manifest is None:
        return {}
    datasets = manifest.get("datasets", [])
    if not isinstance(datasets, list):
        return {}
    return {
        str(entry.get("label")): entry
        for entry in datasets
        if isinstance(entry, dict) and entry.get("label") is not None
    }


def expected_reuse_fields(
    *,
    label: str,
    path: Path,
    target_records: int,
    method: str,
    seed: int | None,
    source_path: Path,
    replication: ReplicationPlan | None,
) -> dict[str, Any]:
    fields: dict[str, Any] = {
        "label": label,
        "path": display_path(path),
        "target_records": target_records,
        "method": method,
        "seed": seed,
        "source_path": display_path(source_path),
    }
    if replication is not None:
        fields["replication"] = {
            "full_repetitions": replication.full_repetitions,
            "remainder_records": replication.remainder_records,
        }
    return fields


def assert_reusable_previous_entry(previous_entry: dict[str, Any] | None, expected: dict[str, Any]) -> None:
    label = expected["label"]
    if previous_entry is None:
        raise ValueError(
            f"{label} already exists but no previous manifest entry was found. "
            "Re-run with --force to replace it."
        )
    mismatches = [
        key
        for key, expected_value in expected.items()
        if previous_entry.get(key) != expected_value
    ]
    if mismatches:
        mismatch_text = ", ".join(mismatches)
        raise ValueError(
            f"{label} already exists but its previous manifest metadata differs "
            f"for: {mismatch_text}. Re-run with --force to replace it."
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


def build_spark(local_config: dict[str, Any]):
    from pyspark.sql import SparkSession

    spark_config = local_config.get("spark", {})
    master = str(spark_config.get("master", "local[*]"))
    app_name = str(spark_config.get("app_name", "flight-delay-big-data-analysis-local"))
    shuffle_partitions = str(spark_config.get("shuffle_partitions", 8))

    return (
        SparkSession.builder.master(master)
        .appName(f"{app_name}-generate-input-sizes")
        .config("spark.sql.shuffle.partitions", shuffle_partitions)
        .getOrCreate()
    )


def stable_row_key_expression(columns: list[str]):
    from pyspark.sql import functions as F

    normalized_columns = [
        F.coalesce(F.col(column).cast("string"), F.lit("__M7_NULL__"))
        for column in columns
    ]
    return F.xxhash64(*normalized_columns)


def deterministic_hash_limit(df, records: int, base_records: int, seed: int):
    from pyspark.sql import functions as F
    from pyspark.sql import Window

    if records > base_records:
        raise ValueError("deterministic_hash_limit cannot select more rows than the source dataset contains")

    if records == base_records:
        return df.select(*df.columns)

    row_key_column = "_m7_row_key"
    sort_hash_column = "_m7_sort_hash"
    partitions = int(df.sparkSession.conf.get("spark.sql.shuffle.partitions", "8"))
    keyed = (
        df.withColumn(row_key_column, stable_row_key_expression(list(df.columns)))
        .withColumn(sort_hash_column, F.xxhash64(F.lit(seed), F.col(row_key_column)))
    )
    ordered = keyed.repartitionByRange(partitions, F.col(sort_hash_column), F.col(row_key_column))
    ranked = ordered.withColumn(
        "_m7_rank",
        F.row_number().over(Window.orderBy(F.col(sort_hash_column), F.col(row_key_column))),
    )
    return ranked.where(F.col("_m7_rank") <= records).select(*df.columns)


def replicated_dataset(df, target_records: int, base_records: int, seed: int):
    plan = replication_plan(target_records, base_records)
    if plan.full_repetitions == 0:
        return deterministic_hash_limit(df, plan.remainder_records, base_records, seed)

    output = df
    for _ in range(plan.full_repetitions - 1):
        output = output.unionByName(df)

    if plan.remainder_records:
        output = output.unionByName(deterministic_hash_limit(df, plan.remainder_records, base_records, seed))
    return output.select(*df.columns)


def write_dataset(df, output_path: Path, force: bool) -> str:
    from src.common.prepared_data import has_windows_winutils
    from src.preparation.prepare_spark import write_parquet_with_pyarrow

    if output_path.exists() and not force:
        raise FileExistsError(f"{display_path(output_path)} already exists. Re-run with --force to replace it.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = temporary_output_path(output_path)
    clear_output_path(temp_path)

    if has_windows_winutils():
        df.write.mode("error").parquet(str(temp_path))
        writer = "spark"
    else:
        write_parquet_with_pyarrow(df, temp_path, list(df.columns))
        writer = "pyarrow_windows_local"

    replace_output_from_temp(temp_path, output_path)
    return writer


def validate_dataset(spark, path: Path, source_schema, target_records: int) -> tuple[int, bool]:
    from src.common.prepared_data import read_prepared_parquet

    df = read_prepared_parquet(spark, path)
    actual_records = df.count()
    schema_matches_source = df.schema == source_schema
    if actual_records != target_records:
        raise ValueError(
            f"{display_path(path)} expected {target_records} records but validation counted {actual_records}"
        )
    if not schema_matches_source:
        raise ValueError(f"{display_path(path)} schema does not match the prepared source schema")
    return actual_records, schema_matches_source


def manifest_entry(
    *,
    label: str,
    path: Path,
    target_records: int,
    actual_records: int,
    method: str,
    seed: int | None,
    source_path: Path,
    schema_matches_source: bool,
    validation_status: str,
    writer: str | None = None,
    replication: ReplicationPlan | None = None,
    generated: bool = False,
    reused_from_manifest: bool = False,
) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "label": label,
        "path": display_path(path),
        "target_records": target_records,
        "actual_records": actual_records,
        "method": method,
        "seed": seed,
        "source_path": display_path(source_path),
        "schema_matches_source": schema_matches_source,
        "validation_status": validation_status,
        "generated": generated,
        "reused_from_manifest": reused_from_manifest,
    }
    if writer is not None:
        entry["writer"] = writer
    if replication is not None:
        entry["replication"] = {
            "full_repetitions": replication.full_repetitions,
            "remainder_records": replication.remainder_records,
        }
    return entry


def generate_manifest(config_path: Path, seed: int, force: bool, include_large: bool) -> dict[str, Any]:
    from src.common.prepared_data import read_prepared_parquet
    from src.common.runtime import ensure_java_17

    ensure_java_17()
    local_config = load_yaml(config_path)
    paths = local_config.get("paths", {})
    prepared_value = paths.get("prepared_file")
    generated_value = paths.get("generated_dir")
    if not prepared_value:
        raise ValueError(f"{display_path(config_path)} does not define paths.prepared_file")
    if not generated_value:
        raise ValueError(f"{display_path(config_path)} does not define paths.generated_dir")

    prepared_path = resolve_project_path(str(prepared_value))
    generated_dir = resolve_project_path(str(generated_value))
    if not prepared_path.exists():
        raise FileNotFoundError(
            f"Prepared dataset was not found: {display_path(prepared_path)}. Run `make prepare` first."
        )

    generated_dir.mkdir(parents=True, exist_ok=True)
    previous_entries = previous_manifest_entries_by_label(load_previous_manifest(generated_dir))
    spark = build_spark(local_config)
    entries: list[dict[str, Any]] = []
    try:
        source_df = read_prepared_parquet(spark, prepared_path)
        source_schema = source_df.schema
        base_records = source_df.count()

        full_entry = manifest_entry(
            label="full",
            path=prepared_path,
            target_records=base_records,
            actual_records=base_records,
            method="prepared_reference",
            seed=None,
            source_path=prepared_path,
            schema_matches_source=True,
            validation_status="success",
            generated=False,
            reused_from_manifest=False,
        )
        validate_manifest_entry(full_entry)
        entries.append(full_entry)

        for spec in selected_size_specs(include_large):
            output_path = generated_dir / f"flights_{spec.label}.parquet"
            if spec.records <= base_records:
                method = "deterministic_hash_limit"
                plan = None
            else:
                plan = replication_plan(spec.records, base_records)
                method = "controlled_replication"

            if output_path.exists() and not force:
                expected = expected_reuse_fields(
                    label=spec.label,
                    path=output_path,
                    target_records=spec.records,
                    method=method,
                    seed=seed,
                    source_path=prepared_path,
                    replication=plan,
                )
                assert_reusable_previous_entry(previous_entries.get(spec.label), expected)
                writer = "existing_validated"
                generated = False
                reused_from_manifest = True
            else:
                if spec.records <= base_records:
                    dataset = deterministic_hash_limit(source_df, spec.records, base_records, seed)
                else:
                    dataset = replicated_dataset(source_df, spec.records, base_records, seed)
                writer = write_dataset(dataset, output_path, force=force)
                generated = True
                reused_from_manifest = False

            actual_records, schema_matches_source = validate_dataset(
                spark,
                output_path,
                source_schema,
                spec.records,
            )
            entry = manifest_entry(
                label=spec.label,
                path=output_path,
                target_records=spec.records,
                actual_records=actual_records,
                method=method,
                seed=seed,
                source_path=prepared_path,
                schema_matches_source=schema_matches_source,
                validation_status="success",
                writer=writer,
                replication=plan,
                generated=generated,
                reused_from_manifest=reused_from_manifest,
            )
            validate_manifest_entry(entry)
            entries.append(entry)
    finally:
        spark.stop()

    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "config_path": display_path(config_path),
        "source_path": display_path(prepared_path),
        "seed": seed,
        "include_large": include_large,
        "datasets": entries,
    }


def write_manifest(manifest: dict[str, Any], generated_dir: Path) -> Path:
    manifest_path = generated_dir / MANIFEST_FILE_NAME
    with manifest_path.open("w", encoding="utf-8") as file:
        json.dump(manifest, file, indent=2, sort_keys=True)
        file.write("\n")
    return manifest_path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG, help="Local YAML config path.")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help="Seed for deterministic hash-limited subsets.")
    parser.add_argument("--force", action="store_true", help="Replace existing generated datasets.")
    parser.add_argument("--include-large", action="store_true", help="Also generate optional 14M and 28M datasets.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    config_path = args.config
    if not config_path.is_absolute():
        config_path = PROJECT_ROOT / config_path

    local_config = load_yaml(config_path)
    generated_dir = resolve_project_path(str(local_config.get("paths", {}).get("generated_dir", "data/generated")))
    manifest = generate_manifest(
        config_path=config_path,
        seed=args.seed,
        force=args.force,
        include_large=args.include_large,
    )
    manifest_path = write_manifest(manifest, generated_dir)

    print("# Input Size Manifest")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    print(f"Input-size manifest written to: {display_path(manifest_path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
