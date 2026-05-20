import pytest

import src.preparation.generate_input_sizes as generate_input_sizes
from src.common.runtime import configure_pyspark_python, ensure_java_17
from src.preparation.generate_input_sizes import (
    DEFAULT_SEED,
    benchmark_inputs_for_manifest,
    deterministic_hash_limit,
    expected_reuse_fields,
    generate_manifest,
    replication_plan,
    selected_size_specs,
    write_manifest,
    assert_reusable_previous_entry,
    validate_manifest_entry,
)

ensure_java_17()
configure_pyspark_python()

from pyspark.sql import SparkSession


def test_selected_size_specs_excludes_large_by_default():
    specs = selected_size_specs(include_large=False)

    assert [(spec.label, spec.records) for spec in specs] == [
        ("100k", 100_000),
        ("500k", 500_000),
        ("1m", 1_000_000),
        ("3m", 3_000_000),
    ]


def test_selected_size_specs_includes_large_when_requested():
    specs = selected_size_specs(include_large=True)

    assert [(spec.label, spec.records) for spec in specs] == [
        ("100k", 100_000),
        ("500k", 500_000),
        ("1m", 1_000_000),
        ("3m", 3_000_000),
        ("14m", 14_000_000),
        ("28m", 28_000_000),
    ]


def test_replication_plan_for_optional_large_inputs():
    base_records = 7_079_081

    assert replication_plan(14_000_000, base_records).full_repetitions == 1
    assert replication_plan(14_000_000, base_records).remainder_records == 6_920_919
    assert replication_plan(28_000_000, base_records).full_repetitions == 3
    assert replication_plan(28_000_000, base_records).remainder_records == 6_762_757


def test_validate_manifest_entry_accepts_valid_entry():
    validate_manifest_entry(
        {
            "label": "100k",
            "target_records": 100_000,
            "actual_records": 100_000,
            "schema_matches_source": True,
            "validation_status": "success",
            "seed": DEFAULT_SEED,
        }
    )


def test_validate_manifest_entry_rejects_row_count_mismatch():
    with pytest.raises(ValueError, match="expected 100000 records"):
        validate_manifest_entry(
            {
                "label": "100k",
                "target_records": 100_000,
                "actual_records": 99_999,
                "schema_matches_source": True,
                "validation_status": "success",
            }
        )


def test_validate_manifest_entry_rejects_schema_mismatch():
    with pytest.raises(ValueError, match="schema does not match"):
        validate_manifest_entry(
            {
                "label": "100k",
                "target_records": 100_000,
                "actual_records": 100_000,
                "schema_matches_source": False,
                "validation_status": "success",
            }
        )


def test_previous_manifest_reuse_accepts_matching_metadata(tmp_path):
    output_path = tmp_path / "flights_100k.parquet"
    source_path = tmp_path / "source.parquet"
    expected = expected_reuse_fields(
        label="100k",
        path=output_path,
        target_records=100_000,
        method="deterministic_hash_limit",
        seed=DEFAULT_SEED,
        source_path=source_path,
        replication=None,
    )

    assert_reusable_previous_entry(dict(expected), expected)


def test_previous_manifest_reuse_rejects_seed_mismatch(tmp_path):
    output_path = tmp_path / "flights_100k.parquet"
    source_path = tmp_path / "source.parquet"
    expected = expected_reuse_fields(
        label="100k",
        path=output_path,
        target_records=100_000,
        method="deterministic_hash_limit",
        seed=DEFAULT_SEED,
        source_path=source_path,
        replication=None,
    )
    previous = dict(expected)
    previous["seed"] = DEFAULT_SEED + 1

    with pytest.raises(ValueError, match="metadata differs"):
        assert_reusable_previous_entry(previous, expected)


def test_benchmark_inputs_for_manifest_skips_missing_optional_inputs():
    local_config = {
        "benchmark": {
            "input_sizes": [
                {"label": "100k", "path": "data/generated/flights_100k.parquet"},
                {"label": "14m", "path": "data/generated/flights_14m.parquet", "optional": True},
            ]
        }
    }
    manifest = {"datasets": [{"label": "100k", "validation_status": "success"}]}

    assert [entry["label"] for entry in benchmark_inputs_for_manifest(local_config, manifest)] == ["100k"]


def test_benchmark_inputs_for_manifest_includes_present_optional_inputs():
    local_config = {
        "benchmark": {
            "input_sizes": [
                {"label": "100k", "path": "data/generated/flights_100k.parquet"},
                {"label": "14m", "path": "data/generated/flights_14m.parquet", "optional": True},
            ]
        }
    }
    manifest = {
        "datasets": [
            {"label": "100k", "validation_status": "success"},
            {"label": "14m", "validation_status": "success"},
        ]
    }

    assert [entry["label"] for entry in benchmark_inputs_for_manifest(local_config, manifest)] == ["100k", "14m"]


def test_deterministic_hash_limit_selects_stable_rows():
    spark = SparkSession.builder.master("local[2]").appName("test-deterministic-hash-limit").getOrCreate()
    try:
        df = spark.range(0, 4).selectExpr(
            "concat('2024-01-0', cast(id + 1 as string)) as flight_date",
            "concat('C', cast(id as string)) as airline_code",
            "concat('A', cast(id as string)) as origin_airport",
            "CASE WHEN id = 2 THEN NULL ELSE cast(id as double) END as departure_delay",
        )

        first = deterministic_hash_limit(df, 2, 4, DEFAULT_SEED)
        second = deterministic_hash_limit(df, 2, 4, DEFAULT_SEED)

        assert first.count() == 2
        assert first.exceptAll(second).count() == 0
        assert second.exceptAll(first).count() == 0
        assert first.columns == df.columns
    finally:
        spark.stop()


def test_generate_manifest_reuses_matching_previous_manifest(tmp_path, monkeypatch):
    monkeypatch.setattr(generate_input_sizes, "DEFAULT_SIZE_SPECS", (("2r", 2),))
    spark = SparkSession.builder.master("local[2]").appName("test-generate-manifest-reuse").getOrCreate()
    try:
        prepared_path = tmp_path / "prepared.parquet"
        generated_dir = tmp_path / "generated"
        config_path = tmp_path / "local.yaml"
        spark.range(0, 3).selectExpr("cast(id as int) as id", "concat('C', cast(id as string)) as code").write.parquet(
            str(prepared_path)
        )
        config_path.write_text(
            f"""
paths:
  prepared_file: {prepared_path.as_posix()}
  generated_dir: {generated_dir.as_posix()}
spark:
  master: local[2]
  app_name: test-generate-input-sizes
  shuffle_partitions: 2
""".lstrip(),
            encoding="utf-8",
        )
    finally:
        spark.stop()

    generated_manifest = generate_manifest(config_path, DEFAULT_SEED, force=True, include_large=False)
    write_manifest(generated_manifest, generated_dir)

    reused_manifest = generate_manifest(config_path, DEFAULT_SEED, force=False, include_large=False)
    reused_entry = next(entry for entry in reused_manifest["datasets"] if entry["label"] == "2r")

    assert reused_entry["generated"] is False
    assert reused_entry["reused_from_manifest"] is True
    assert reused_entry["writer"] == "existing_validated"


def test_generate_manifest_requires_force_for_existing_seed_conflict(tmp_path, monkeypatch):
    monkeypatch.setattr(generate_input_sizes, "DEFAULT_SIZE_SPECS", (("2r", 2),))
    spark = SparkSession.builder.master("local[2]").appName("test-generate-manifest-seed-conflict").getOrCreate()
    try:
        prepared_path = tmp_path / "prepared.parquet"
        generated_dir = tmp_path / "generated"
        config_path = tmp_path / "local.yaml"
        spark.range(0, 3).selectExpr("cast(id as int) as id", "concat('C', cast(id as string)) as code").write.parquet(
            str(prepared_path)
        )
        config_path.write_text(
            f"""
paths:
  prepared_file: {prepared_path.as_posix()}
  generated_dir: {generated_dir.as_posix()}
spark:
  master: local[2]
  app_name: test-generate-input-sizes
  shuffle_partitions: 2
""".lstrip(),
            encoding="utf-8",
        )
    finally:
        spark.stop()

    generated_manifest = generate_manifest(config_path, DEFAULT_SEED, force=True, include_large=False)
    write_manifest(generated_manifest, generated_dir)

    with pytest.raises(ValueError, match="Re-run with --force"):
        generate_manifest(config_path, DEFAULT_SEED + 1, force=False, include_large=False)
