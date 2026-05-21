"""Mapper for the MapReduce delay-by-airport-month analysis."""

from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from src.mapreduce.mapreduce_logic import (
        delay_range,
        derived_cause,
        emit_pair,
        iter_flight_records,
    )
except ModuleNotFoundError:  # pragma: no cover - Hadoop Streaming localized file fallback
    from mapreduce_logic import delay_range, derived_cause, emit_pair, iter_flight_records


def main() -> int:
    for record in iter_flight_records(sys.stdin):
        if record.departure_delay is None:
            continue
        emit_pair(
            [record.origin_airport, record.month, delay_range(record.departure_delay)],
            [record.departure_delay, record.arrival_delay, derived_cause(record)],
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
