from pathlib import Path

import pytest

import src.hive.run_hive as run_hive


def test_build_ddl_sql_replaces_exactly_one_location(monkeypatch, tmp_path):
    ddl_path = tmp_path / "ddl.sql"
    ddl_path.write_text(
        """
CREATE EXTERNAL TABLE flight_delay.flights_2024_clean (
  id INT
)
STORED AS PARQUET
LOCATION 'file:///workspace/data/prepared/flights_2024_clean.parquet';
""".lstrip(),
        encoding="utf-8",
    )
    monkeypatch.setattr(run_hive, "DDL_FILE", ddl_path)

    input_path = run_hive.PROJECT_ROOT / "data" / "generated" / "flights_100k.parquet"
    ddl = run_hive.build_ddl_sql(input_path)

    assert "LOCATION 'file:///workspace/data/generated/flights_100k.parquet'" in ddl
    assert "data/prepared/flights_2024_clean.parquet" not in ddl


def test_build_ddl_sql_errors_when_location_count_is_not_one(monkeypatch, tmp_path):
    ddl_path = tmp_path / "ddl.sql"
    ddl_path.write_text(
        """
CREATE EXTERNAL TABLE one (id INT)
LOCATION 'file:///workspace/data/one.parquet';
CREATE EXTERNAL TABLE two (id INT)
LOCATION 'file:///workspace/data/two.parquet';
""".lstrip(),
        encoding="utf-8",
    )
    monkeypatch.setattr(run_hive, "DDL_FILE", ddl_path)

    with pytest.raises(ValueError, match="Expected exactly one LOCATION clause"):
        run_hive.build_ddl_sql(run_hive.PROJECT_ROOT / "data" / "generated" / "flights_100k.parquet")
