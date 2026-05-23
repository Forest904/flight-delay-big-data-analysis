"""Mapper for the MapReduce delay-by-airport-month analysis."""

from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from src.mapreduce.mapreduce_logic import (
        delay_key_value,
        emit_pair,
        iter_flight_records,
    )
except ModuleNotFoundError:  # pragma: no cover - Hadoop Streaming localized file fallback
    from mapreduce_logic import delay_key_value, emit_pair, iter_flight_records


def main() -> int:
    for record in iter_flight_records(sys.stdin):
        pair = delay_key_value(record)
        if pair is None:
            continue
        emit_pair(*pair)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
