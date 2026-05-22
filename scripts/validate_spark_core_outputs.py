"""Validate Spark Core outputs against the Spark SQL reference outputs."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.validation_common import (
    PROJECT_ROOT as VALIDATION_ROOT,
    TOLERANCE,
    assert_metrics_success,
    assert_canonical_input_path,
    assert_same_input_path,
    assert_output_row_count,
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
    return outputs_dir / "spark_sql", outputs_dir / "spark_core"


def main() -> int:
    local_config = load_yaml(LOCAL_CONFIG)
    sql_root, core_root = output_roots(local_config)

    sql_metrics = assert_metrics_success(sql_root, "spark_sql")
    core_metrics = assert_metrics_success(core_root, "spark_core")
    assert_canonical_input_path(sql_metrics, local_config, "Spark SQL")
    assert_canonical_input_path(core_metrics, local_config, "Spark Core")
    assert_same_input_path(sql_metrics, core_metrics, "Spark Core")
    sql_metric_rows = metric_rows(sql_metrics)
    core_metric_rows = metric_rows(core_metrics)

    sql_delay = read_csv_dir(sql_root / "delay_by_airport_month" / "full")
    core_delay = read_csv_dir(core_root / "delay_by_airport_month" / "full")
    sql_ranking = read_csv_dir(sql_root / "airline_airport_ranking" / "full")
    core_ranking = read_csv_dir(core_root / "airline_airport_ranking" / "full")

    assert_output_row_count(core_delay, core_metric_rows, "delay_by_airport_month", "Spark Core")
    assert_output_row_count(core_ranking, core_metric_rows, "airline_airport_ranking", "Spark Core")
    assert_output_row_count(sql_delay, sql_metric_rows, "delay_by_airport_month", "Spark SQL")
    assert_output_row_count(sql_ranking, sql_metric_rows, "airline_airport_ranking", "Spark SQL")

    validate_delay(sql_delay, core_delay, technology="core", candidate_label="Spark Core")
    validate_ranking(sql_ranking, core_ranking, technology="core", candidate_label="Spark Core")

    print("Spark Core output validation passed")
    print(f"delay rows: {len(core_delay)}; ranking rows: {len(core_ranking)}")
    print(f"numeric tolerance: {TOLERANCE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
