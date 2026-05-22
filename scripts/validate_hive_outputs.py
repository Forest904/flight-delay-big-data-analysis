"""Validate Hive outputs against the Spark SQL reference outputs."""

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
    return outputs_dir / "spark_sql", outputs_dir / "hive"


def main() -> int:
    local_config = load_yaml(LOCAL_CONFIG)
    sql_root, hive_root = output_roots(local_config)

    sql_metrics = assert_metrics_success(sql_root, "spark_sql")
    hive_metrics = assert_metrics_success(hive_root, "hive")
    assert_canonical_input_path(sql_metrics, local_config, "Spark SQL")
    assert_canonical_input_path(hive_metrics, local_config, "Hive")
    assert_same_input_path(sql_metrics, hive_metrics, "Hive")
    sql_metric_rows = metric_rows(sql_metrics)
    hive_metric_rows = metric_rows(hive_metrics)

    sql_delay = read_csv_dir(sql_root / "delay_by_airport_month" / "full")
    hive_delay = read_csv_dir(hive_root / "delay_by_airport_month" / "full")
    sql_ranking = read_csv_dir(sql_root / "airline_airport_ranking" / "full")
    hive_ranking = read_csv_dir(hive_root / "airline_airport_ranking" / "full")

    assert_output_row_count(hive_delay, hive_metric_rows, "delay_by_airport_month", "Hive")
    assert_output_row_count(hive_ranking, hive_metric_rows, "airline_airport_ranking", "Hive")
    assert_output_row_count(sql_delay, sql_metric_rows, "delay_by_airport_month", "Spark SQL")
    assert_output_row_count(sql_ranking, sql_metric_rows, "airline_airport_ranking", "Spark SQL")

    assert_first_10(hive_root, "delay_by_airport_month", DELAY_COLUMNS, "hive")
    assert_first_10(hive_root, "airline_airport_ranking", RANKING_COLUMNS, "hive")
    validate_delay(sql_delay, hive_delay, technology="hive", candidate_label="Hive")
    validate_ranking(sql_ranking, hive_ranking, technology="hive", candidate_label="Hive")

    print("Hive output validation passed")
    print(f"delay rows: {len(hive_delay)}; ranking rows: {len(hive_ranking)}")
    print(f"numeric tolerance: {TOLERANCE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
