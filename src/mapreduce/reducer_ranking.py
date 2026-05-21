"""Reducer for the MapReduce airline-airport ranking analysis."""

from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from src.mapreduce.mapreduce_logic import grouped_key_values, parse_json_key, ranking_rows_from_group, row_as_json
except ModuleNotFoundError:  # pragma: no cover - Hadoop Streaming localized file fallback
    from mapreduce_logic import grouped_key_values, parse_json_key, ranking_rows_from_group, row_as_json


def main() -> int:
    for key, values in grouped_key_values(sys.stdin):
        origin_airport = str(parse_json_key(key)[0])
        for row in ranking_rows_from_group(origin_airport, values):
            row_as_json(row)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
