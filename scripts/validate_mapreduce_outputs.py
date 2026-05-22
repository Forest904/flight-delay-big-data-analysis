"""Validate MapReduce outputs against the Spark SQL reference outputs."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.validation_common import (
    DELAY_COLUMNS,
    PROJECT_ROOT as VALIDATION_ROOT,
    RANKING_COLUMNS,
    TOLERANCE,
    assert_first_10,
    assert_canonical_input_path,
    assert_metrics_success,
    assert_output_row_count,
    assert_same_input_path,
    load_yaml,
    metric_rows,
    read_csv_dir,
    resolve_project_path,
    validate_delay,
    validate_ranking,
)


LOCAL_CONFIG = VALIDATION_ROOT / "config" / "local.yaml"


def output_roots(local_config: dict[str, Any]) -> tuple[Path, Path]:
    paths = local_config.get("paths", {})
    outputs_dir = resolve_project_path(str(paths.get("outputs_dir", "outputs")))
    return outputs_dir / "spark_sql", outputs_dir / "mapreduce"


def main() -> int:
    local_config = load_yaml(LOCAL_CONFIG)
    sql_root, mapreduce_root = output_roots(local_config)

    sql_metrics = assert_metrics_success(sql_root, "spark_sql")
    mapreduce_metrics = assert_metrics_success(mapreduce_root, "mapreduce")
    assert_canonical_input_path(sql_metrics, local_config, "Spark SQL")
    assert_canonical_input_path(mapreduce_metrics, local_config, "MapReduce")
    assert_same_input_path(sql_metrics, mapreduce_metrics, "MapReduce")
    sql_metric_rows = metric_rows(sql_metrics)
    mapreduce_metric_rows = metric_rows(mapreduce_metrics)

    sql_delay = read_csv_dir(sql_root / "delay_by_airport_month" / "full")
    mapreduce_delay = read_csv_dir(mapreduce_root / "delay_by_airport_month" / "full")
    sql_ranking = read_csv_dir(sql_root / "airline_airport_ranking" / "full")
    mapreduce_ranking = read_csv_dir(mapreduce_root / "airline_airport_ranking" / "full")

    assert_output_row_count(mapreduce_delay, mapreduce_metric_rows, "delay_by_airport_month", "MapReduce")
    assert_output_row_count(mapreduce_ranking, mapreduce_metric_rows, "airline_airport_ranking", "MapReduce")
    assert_output_row_count(sql_delay, sql_metric_rows, "delay_by_airport_month", "Spark SQL")
    assert_output_row_count(sql_ranking, sql_metric_rows, "airline_airport_ranking", "Spark SQL")

    assert_first_10(mapreduce_root, "delay_by_airport_month", DELAY_COLUMNS, "mapreduce")
    assert_first_10(mapreduce_root, "airline_airport_ranking", RANKING_COLUMNS, "mapreduce")
    validate_delay(sql_delay, mapreduce_delay, technology="mapreduce", candidate_label="MapReduce")
    validate_ranking(sql_ranking, mapreduce_ranking, technology="mapreduce", candidate_label="MapReduce")

    print("MapReduce output validation passed")
    print(f"delay rows: {len(mapreduce_delay)}; ranking rows: {len(mapreduce_ranking)}")
    print(f"numeric tolerance: {TOLERANCE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
