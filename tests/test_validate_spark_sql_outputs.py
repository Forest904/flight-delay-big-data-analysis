from pathlib import Path

import pytest

from scripts import validate_spark_sql_outputs


def test_validation_input_path_prefers_metrics_input_path():
    path = validate_spark_sql_outputs.validation_input_path(
        {"input_path": "data/generated/flights_1m.parquet"},
        {"paths": {"prepared_file": "data/prepared/flights_2024_clean.parquet"}},
        Path("outputs/spark_sql/runtime_metrics.json"),
    )

    assert path == validate_spark_sql_outputs.PROJECT_ROOT / "data" / "generated" / "flights_1m.parquet"


def test_validation_input_path_falls_back_to_config_prepared_file():
    path = validate_spark_sql_outputs.validation_input_path(
        {},
        {"paths": {"prepared_file": "data/prepared/flights_2024_clean.parquet"}},
        Path("outputs/spark_sql/runtime_metrics.json"),
    )

    assert path == validate_spark_sql_outputs.PROJECT_ROOT / "data" / "prepared" / "flights_2024_clean.parquet"


def test_validation_input_path_requires_a_source_path():
    with pytest.raises(ValueError, match="does not define input_path"):
        validate_spark_sql_outputs.validation_input_path(
            {},
            {"paths": {}},
            Path("outputs/spark_sql/runtime_metrics.json"),
        )
