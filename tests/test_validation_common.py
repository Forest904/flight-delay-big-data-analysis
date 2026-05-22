import pytest

from scripts import validation_common


def test_assert_same_input_path_accepts_container_file_uri():
    validation_common.assert_same_input_path(
        {"input_path": "data/generated/flights_100k.parquet"},
        {"input_path": "file:///workspace/data/generated/flights_100k.parquet"},
        "MapReduce",
    )


def test_comparable_input_path_accepts_absolute_project_path():
    absolute = validation_common.PROJECT_ROOT / "data" / "prepared" / "flights_2024_clean.parquet"

    assert validation_common.comparable_input_path(absolute) == "data/prepared/flights_2024_clean.parquet"


def test_assert_same_input_path_fails_on_mismatch():
    with pytest.raises(AssertionError, match="input_path differ"):
        validation_common.assert_same_input_path(
            {"input_path": "data/generated/flights_1m.parquet"},
            {"input_path": "data/generated/flights_100k.parquet"},
            "MapReduce",
        )


def test_assert_canonical_input_path_accepts_prepared_dataset():
    validation_common.assert_canonical_input_path(
        {"input_path": "file:///workspace/data/prepared/flights_2024_clean.parquet"},
        {"paths": {"prepared_file": "data/prepared/flights_2024_clean.parquet"}},
        "Spark SQL",
    )


def test_assert_canonical_input_path_fails_on_drift():
    with pytest.raises(AssertionError, match="canonical validation input"):
        validation_common.assert_canonical_input_path(
            {"input_path": "data/generated/flights_14m.parquet"},
            {"paths": {"prepared_file": "data/prepared/flights_2024_clean.parquet"}},
            "Spark SQL",
        )
