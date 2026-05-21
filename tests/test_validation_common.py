import pytest

from scripts import validation_common


def test_assert_same_input_path_accepts_container_file_uri():
    validation_common.assert_same_input_path(
        {"input_path": "data/generated/flights_100k.parquet"},
        {"input_path": "file:///workspace/data/generated/flights_100k.parquet"},
        "MapReduce",
    )


def test_assert_same_input_path_fails_on_mismatch():
    with pytest.raises(AssertionError, match="input_path differ"):
        validation_common.assert_same_input_path(
            {"input_path": "data/generated/flights_1m.parquet"},
            {"input_path": "data/generated/flights_100k.parquet"},
            "MapReduce",
        )
