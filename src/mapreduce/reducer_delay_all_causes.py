"""Reducer for the MapReduce all-positive delay causes analysis."""

from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from src.mapreduce.mapreduce_logic import (
        all_causes_rows_from_group,
        grouped_key_values,
        parse_json_key,
        row_as_json,
    )
except ModuleNotFoundError:  # pragma: no cover - Hadoop Streaming localized file fallback
    from mapreduce_logic import all_causes_rows_from_group, grouped_key_values, parse_json_key, row_as_json


def main() -> int:
    for key, values in grouped_key_values(sys.stdin):
        for row in all_causes_rows_from_group(parse_json_key(key), values):
            row_as_json(row)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
