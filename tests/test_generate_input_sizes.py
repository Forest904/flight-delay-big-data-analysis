import pytest

import src.preparation.generate_input_sizes as generate_input_sizes
from src.common.runtime import configure_pyspark_python, ensure_java_17
from src.preparation.generate_input_sizes import (
    DEFAULT_SEED,
    benchmark_inputs_for_manifest,
    deterministic_hash_limit,
    high_cardinality_stress_dataset,
    expected_reuse_fields,
    generate_manifest,
    replication_plan,
    selected_cardinality_stress_specs,
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


def test_selected_size_specs_filters_large_labels_when_requested():
    specs = selected_size_specs(include_large=True, large_labels={"14m"})

    assert [(spec.label, spec.records) for spec in specs] == [
        ("100k", 100_000),
        ("500k", 500_000),
        ("1m", 1_000_000),
        ("3m", 3_000_000),
        ("14m", 14_000_000),
    ]


def test_selected_size_specs_rejects_unknown_large_label():
    with pytest.raises(ValueError, match="Unknown large input label"):
        selected_size_specs(include_large=True, large_labels={"56m"})


def test_selected_cardinality_stress_specs_are_opt_in():
    assert selected_cardinality_stress_specs(False) == []
    assert [(spec.label, spec.source_label, spec.variant_factor) for spec in selected_cardinality_stress_specs(True)] == [
        ("1m_hc8", "1m", 8)
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


def test_high_cardinality_stress_dataset_suffixes_keys_without_changing_numeric_values():
    spark = SparkSession.builder.master("local[2]").appName("test-high-cardinality-stress-dataset").getOrCreate()
    try:
        df = spark.range(0, 3).selectExpr(
            "CASE id WHEN 0 THEN 'AA' WHEN 1 THEN 'DL' ELSE 'UA' END as airline_code",
            "CASE id WHEN 1 THEN NULL WHEN 0 THEN 'American' ELSE 'United' END as airline_name",
            "CASE id WHEN 0 THEN 'JFK' WHEN 1 THEN 'LAX' ELSE 'SFO' END as origin_airport",
            "CASE id WHEN 0 THEN cast(10.0 as double) WHEN 1 THEN cast(-3.0 as double) ELSE cast(NULL as double) END as departure_delay",
            "cast(id + 1 as int) as month",
        )

        first = high_cardinality_stress_dataset(df, 8, DEFAULT_SEED)
        second = high_cardinality_stress_dataset(df, 8, DEFAULT_SEED)
        rows = first.orderBy("month").collect()

        assert first.schema == df.schema
        assert first.count() == df.count()
        assert first.exceptAll(second).count() == 0
        assert second.exceptAll(first).count() == 0
        assert [row["departure_delay"] for row in rows] == [10.0, -3.0, None]
        assert all("_HC0" in row["airline_code"] for row in rows)
        assert all("_HC0" in row["origin_airport"] for row in rows)
        assert rows[1]["airline_name"] is None
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


def test_generate_manifest_records_input_kinds_and_cardinality_stress_metadata(tmp_path, monkeypatch):
    monkeypatch.setattr(generate_input_sizes, "DEFAULT_SIZE_SPECS", (("2r", 2),))
    monkeypatch.setattr(generate_input_sizes, "LARGE_SIZE_SPECS", (("5r", 5),))
    monkeypatch.setattr(generate_input_sizes, "DEFAULT_CARDINALITY_STRESS_SPECS", (("2r_hc2", "2r", 2),))
    spark = SparkSession.builder.master("local[2]").appName("test-generate-manifest-cardinality-stress").getOrCreate()
    try:
        prepared_path = tmp_path / "prepared.parquet"
        generated_dir = tmp_path / "generated"
        config_path = tmp_path / "local.yaml"
        spark.range(0, 3).selectExpr(
            "concat('2024-01-0', cast(id + 1 as string)) as flight_date",
            "cast(1 as int) as month",
            "CASE id WHEN 0 THEN 'AA' WHEN 1 THEN 'DL' ELSE 'UA' END as airline_code",
            "CASE id WHEN 1 THEN NULL WHEN 0 THEN 'American' ELSE 'United' END as airline_name",
            "CASE id WHEN 0 THEN 'JFK' WHEN 1 THEN 'LAX' ELSE 'SFO' END as origin_airport",
            "CASE id WHEN 0 THEN cast(10.0 as double) WHEN 1 THEN cast(-3.0 as double) ELSE cast(NULL as double) END as departure_delay",
        ).write.parquet(str(prepared_path))
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

    manifest = generate_manifest(
        config_path,
        DEFAULT_SEED,
        force=True,
        include_large=True,
        large_labels={"5r"},
        include_cardinality_stress=True,
    )
    by_label = {entry["label"]: entry for entry in manifest["datasets"]}

    assert by_label["full"]["input_kind"] == "original_prepared"
    assert by_label["full"]["synthetic_input"] is False
    assert by_label["2r"]["input_kind"] == "deterministic_subset"
    assert by_label["2r"]["synthetic_input"] is False
    assert by_label["5r"]["input_kind"] == "row_volume_replication"
    assert by_label["5r"]["synthetic_input"] is True
    assert by_label["2r_hc2"]["input_kind"] == "high_cardinality_stress"
    assert by_label["2r_hc2"]["synthetic_input"] is True
    assert by_label["2r_hc2"]["source_input_label"] == "2r"
    assert by_label["2r_hc2"]["variant_factor"] == 2
    assert by_label["2r_hc2"]["variant_columns"] == ["origin_airport", "airline_code", "airline_name"]
    assert by_label["2r_hc2"]["row_count_policy"] == "same_as_source"
    assert by_label["2r_hc2"]["actual_records"] == by_label["2r"]["actual_records"]


def test_generate_manifest_requires_force_for_changed_cardinality_stress_metadata(tmp_path, monkeypatch):
    monkeypatch.setattr(generate_input_sizes, "DEFAULT_SIZE_SPECS", (("2r", 2),))
    monkeypatch.setattr(generate_input_sizes, "DEFAULT_CARDINALITY_STRESS_SPECS", (("2r_hc", "2r", 2),))
    spark = SparkSession.builder.master("local[2]").appName("test-cardinality-stress-reuse-conflict").getOrCreate()
    try:
        prepared_path = tmp_path / "prepared.parquet"
        generated_dir = tmp_path / "generated"
        config_path = tmp_path / "local.yaml"
        spark.range(0, 3).selectExpr(
            "CASE id WHEN 0 THEN 'AA' WHEN 1 THEN 'DL' ELSE 'UA' END as airline_code",
            "CASE id WHEN 1 THEN NULL WHEN 0 THEN 'American' ELSE 'United' END as airline_name",
            "CASE id WHEN 0 THEN 'JFK' WHEN 1 THEN 'LAX' ELSE 'SFO' END as origin_airport",
            "CASE id WHEN 0 THEN cast(10.0 as double) WHEN 1 THEN cast(-3.0 as double) ELSE cast(NULL as double) END as departure_delay",
        ).write.parquet(str(prepared_path))
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

    generated_manifest = generate_manifest(
        config_path,
        DEFAULT_SEED,
        force=True,
        include_large=False,
        include_cardinality_stress=True,
    )
    write_manifest(generated_manifest, generated_dir)
    monkeypatch.setattr(generate_input_sizes, "DEFAULT_CARDINALITY_STRESS_SPECS", (("2r_hc", "2r", 3),))

    with pytest.raises(ValueError, match="metadata differs"):
        generate_manifest(
            config_path,
            DEFAULT_SEED,
            force=False,
            include_large=False,
            include_cardinality_stress=True,
        )


def test_makefile_wires_large_label_filter():
    makefile = generate_input_sizes.PROJECT_ROOT.joinpath("Makefile").read_text(encoding="utf-8")

    assert "LARGE_LABEL" in makefile
    assert "--large-label $(label)" in makefile
    assert "GENERATE_CARDINALITY_STRESS" in makefile
    assert "--include-cardinality-stress" in makefile
