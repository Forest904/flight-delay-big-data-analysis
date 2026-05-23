from __future__ import annotations

import json
import re
import subprocess
from io import StringIO
from collections import Counter
from datetime import date
from pathlib import Path

import pytest
import pyarrow as pa
import pyarrow.parquet as pq

from src.mapreduce import run_mapreduce
from src.mapreduce.mapreduce_logic import (
    CANONICAL_COLUMNS,
    CANCELLED_NO_DEPARTURE_DELAY_RANGE,
    delay_key_value,
    delay_range,
    delay_row_from_group,
    derived_cause,
    nullable_number_sort_value,
    iter_flight_records,
    ranking_output_sort_key,
    ranking_rows_from_group,
    record_from_row,
    top_three_causes,
)


def canonical_row(**overrides: object) -> list[str]:
    values = {
        "flight_date": "2024-01-01",
        "month": "1",
        "airline_code": "AA",
        "airline_name": "",
        "origin_airport": "ABE",
        "destination_airport": "ATL",
        "departure_delay": "20.0",
        "arrival_delay": "30.0",
        "cancelled": "0",
        "diverted": "0",
        "cancellation_code": "",
        "carrier_delay": "7.0",
        "weather_delay": "7.0",
        "nas_delay": "0.0",
        "security_delay": "0.0",
        "late_aircraft_delay": "0.0",
    }
    values.update({key: str(value) for key, value in overrides.items()})
    return [values[column] for column in CANONICAL_COLUMNS]


def test_delay_range_and_derived_cause_match_reference_rules():
    assert delay_range(-5.0) == "low"
    assert delay_range(15.0) == "medium"
    assert delay_range(60.0) == "medium"
    assert delay_range(61.0) == "high"

    tied = record_from_row(canonical_row(carrier_delay="7", weather_delay="7"))
    assert derived_cause(tied) == "delay:carrier"

    cancelled = record_from_row(canonical_row(cancelled="1", cancellation_code="B"))
    assert derived_cause(cancelled) == "cancellation:B"

    unknown = record_from_row(canonical_row(carrier_delay="0", weather_delay="0", departure_delay="3"))
    assert derived_cause(unknown) == "unknown"


def test_delay_key_value_includes_cancelled_null_departure_bucket():
    cancelled = record_from_row(canonical_row(departure_delay="", arrival_delay="", cancelled="1", cancellation_code="B"))
    pair = delay_key_value(cancelled)

    assert pair == (
        ["ABE", 1, CANCELLED_NO_DEPARTURE_DELAY_RANGE],
        [None, None, "cancellation:B"],
    )

    missing_code = record_from_row(canonical_row(departure_delay="", arrival_delay="", cancelled="1", cancellation_code=""))
    assert delay_key_value(missing_code) == (
        ["ABE", 1, CANCELLED_NO_DEPARTURE_DELAY_RANGE],
        [None, None, "cancellation:unknown"],
    )

    non_cancelled_null = record_from_row(canonical_row(departure_delay="", arrival_delay="", cancelled="0"))
    assert delay_key_value(non_cancelled_null) is None


def test_top_three_causes_use_count_descending_and_label_ascending():
    causes = Counter({"delay:weather": 2, "delay:carrier": 2, "unknown": 1})

    assert top_three_causes(causes) == ("delay:carrier", 2, "delay:weather", 2, "unknown", 1)
    assert top_three_causes(Counter({"unknown": 4})) == ("unknown", 4, None, 0, None, 0)


def test_delay_reducer_row_excludes_null_departure_upstream_and_pads_causes():
    row = delay_row_from_group(
        ["ABE", 1, "medium"],
        [
            [20.0, 30.0, "delay:carrier"],
            [40.0, None, "delay:carrier"],
            [60.0, 55.0, "delay:nas"],
        ],
    )

    assert row == [
        "ABE",
        1,
        "medium",
        3,
        40.0,
        42.5,
        "delay:carrier",
        2,
        "delay:nas",
        1,
        None,
        0,
    ]


def test_delay_reducer_row_allows_cancelled_bucket_null_departure_average():
    row = delay_row_from_group(
        ["ABE", 1, CANCELLED_NO_DEPARTURE_DELAY_RANGE],
        [
            [None, None, "cancellation:B"],
            [None, None, "cancellation:A"],
            [None, None, "cancellation:A"],
        ],
    )

    assert row == [
        "ABE",
        1,
        CANCELLED_NO_DEPARTURE_DELAY_RANGE,
        3,
        None,
        None,
        "cancellation:A",
        2,
        "cancellation:B",
        1,
        None,
        0,
    ]


def test_ranking_reducer_uses_rank_ties_and_nulls_last():
    rows = ranking_rows_from_group(
        "ABE",
        [
            ["AA", 10.0, 12.0, 0],
            ["AA", 20.0, 18.0, 1],
            ["BB", 10.0, 22.0, 0],
            ["CC", 10.0, 20.0, 0],
            ["DD", None, 5.0, 0],
        ],
    )

    rows.sort(key=ranking_output_sort_key)
    assert [row[1] for row in rows] == ["BB", "CC", "AA", "DD"]
    assert [row[8] for row in rows] == [1, 1, 3, 4]
    assert rows[0][6] == 12.5
    assert rows[2][7] == 2.5
    assert nullable_number_sort_value(None) > nullable_number_sort_value(99.0)


def test_canonical_csv_export_from_parquet_reuses_matching_manifest(tmp_path, monkeypatch):
    parquet_dir = tmp_path / "flights_2.parquet"
    parquet_dir.mkdir()
    table = pa.table(
        {
            "flight_date": pa.array([date(2024, 1, 1), date(2024, 1, 2)], type=pa.date32()),
            "month": pa.array([1, 1], type=pa.int32()),
            "airline_code": ["AA", "BB"],
            "airline_name": [None, None],
            "origin_airport": ["ABE", "ATL"],
            "destination_airport": ["ATL", "ABE"],
            "departure_delay": pa.array([10.0, None], type=pa.float64()),
            "arrival_delay": pa.array([12.0, 3.0], type=pa.float64()),
            "cancelled": pa.array([0, 0], type=pa.int32()),
            "diverted": pa.array([0, 0], type=pa.int32()),
            "cancellation_code": [None, None],
            "carrier_delay": pa.array([0.0, None], type=pa.float64()),
            "weather_delay": pa.array([0.0, None], type=pa.float64()),
            "nas_delay": pa.array([0.0, None], type=pa.float64()),
            "security_delay": pa.array([0.0, None], type=pa.float64()),
            "late_aircraft_delay": pa.array([0.0, None], type=pa.float64()),
        }
    )
    pq.write_table(table, parquet_dir / "part-00000.parquet")
    monkeypatch.setattr(run_mapreduce, "EXPORT_ROOT", tmp_path / "mapreduce_csv")

    first = run_mapreduce.export_parquet_to_canonical_csv(parquet_dir)
    second = run_mapreduce.export_parquet_to_canonical_csv(parquet_dir)

    assert first.row_count == 2
    assert first.reused is False
    assert second.reused is True
    assert second.row_count == 2
    lines = first.csv_path.read_text(encoding="utf-8").splitlines()
    assert lines[0] == ",".join(CANONICAL_COLUMNS)
    assert "2024-01-01" in lines[1]
    manifest = json.loads(first.manifest_path.read_text(encoding="utf-8"))
    assert manifest["csv_size_bytes"] == first.csv_path.stat().st_size
    assert manifest["csv_sha256"] == run_mapreduce.file_sha256(first.csv_path)


def test_canonical_csv_export_regenerates_when_cached_csv_is_tampered(tmp_path, monkeypatch):
    parquet_dir = tmp_path / "flights_2.parquet"
    parquet_dir.mkdir()
    table = pa.table({column: [canonical_row()[index]] for index, column in enumerate(CANONICAL_COLUMNS)})
    nested = parquet_dir / "nested"
    nested.mkdir()
    pq.write_table(table, nested / "part-00000.parquet")
    monkeypatch.setattr(run_mapreduce, "EXPORT_ROOT", tmp_path / "mapreduce_csv")

    first = run_mapreduce.export_parquet_to_canonical_csv(parquet_dir)
    first.csv_path.write_text("bad\n", encoding="utf-8")
    second = run_mapreduce.export_parquet_to_canonical_csv(parquet_dir)

    assert second.reused is False
    assert second.csv_path.read_text(encoding="utf-8").startswith(",".join(CANONICAL_COLUMNS))


def test_parquet_part_files_are_discovered_recursively(tmp_path):
    nested = tmp_path / "dataset.parquet" / "a" / "b"
    nested.mkdir(parents=True)
    part = nested / "part-00000.parquet"
    part.write_bytes(b"not really parquet")

    assert run_mapreduce.parquet_part_files(tmp_path / "dataset.parquet") == [part]


def test_input_slug_includes_stable_hash_to_avoid_same_name_collisions(tmp_path):
    one = tmp_path / "one" / "flights.parquet"
    two = tmp_path / "two" / "flights.parquet"

    assert re.fullmatch(r"flights-[0-9a-f]{10}", run_mapreduce.input_slug(one))
    assert run_mapreduce.input_slug(one) != run_mapreduce.input_slug(two)


def test_iter_flight_records_is_strict_by_default_and_can_skip_for_diagnostics():
    bad_stream = StringIO(",".join(CANONICAL_COLUMNS) + "\nnot,enough,fields\n")

    with pytest.raises(ValueError):
        list(iter_flight_records(bad_stream))

    assert list(iter_flight_records(StringIO("not,enough,fields\n"), strict=False)) == []


def test_hadoop_streaming_command_uses_localized_files_file_uris_and_reducers():
    job = run_mapreduce.mapreduce_jobs()[0]
    command = run_mapreduce.hadoop_streaming_command(
        job,
        run_mapreduce.PROJECT_ROOT
        / "data"
        / "generated"
        / "mapreduce_csv"
        / "flights_100k-1234567890"
        / "part-00000.csv",
        run_mapreduce.PROJECT_ROOT / "outputs" / "mapreduce" / ".tmp_hadoop" / job.name,
        reducers=3,
    )

    assert "mapreduce-runner" in command
    assert "/opt/hadoop-streaming.jar" in command
    assert "mapreduce.job.reduces=3" in command
    assert "-files" in command
    assert "-cmdenv" in command
    assert "PYTHONPATH=/workspace:/workspace/src/mapreduce" in command
    files_arg = command[command.index("-files") + 1]
    assert f"file:///workspace/{job.mapper.relative_to(run_mapreduce.PROJECT_ROOT).as_posix()}" in files_arg
    assert f"file:///workspace/{job.reducer.relative_to(run_mapreduce.PROJECT_ROOT).as_posix()}" in files_arg
    assert "file:///workspace/src/mapreduce/mapreduce_logic.py" in files_arg
    assert f"python3 {job.mapper.name}" in command
    assert f"python3 {job.reducer.name}" in command
    assert "file:///workspace/data/generated/mapreduce_csv/flights_100k-1234567890/part-00000.csv" in command


def test_container_file_uri_rejects_paths_outside_repository(tmp_path):
    with pytest.raises(ValueError, match="inside the repository"):
        run_mapreduce.container_file_uri(tmp_path / "outside.csv")


def test_validate_preconditions_reports_runner_dependency_failures(monkeypatch):
    calls: list[list[str]] = []

    def fake_run_command(command: list[str], timeout_seconds: int | None = None) -> subprocess.CompletedProcess[str]:
        calls.append(command)
        if command[-1] == "version":
            return subprocess.CompletedProcess(command, 0, stdout="Docker Compose version v2\n", stderr="")
        return subprocess.CompletedProcess(command, 1, stdout="", stderr="missing hadoop streaming jar")

    monkeypatch.setattr(run_mapreduce, "run_command", fake_run_command)

    errors = run_mapreduce.validate_preconditions(
        run_mapreduce.PROJECT_ROOT / "README.md",
        run_mapreduce.PROJECT_ROOT / "outputs" / "mapreduce",
    )

    assert any("missing hadoop streaming jar" in error for error in errors)
