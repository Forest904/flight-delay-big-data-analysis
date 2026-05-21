"""Mapper for the MapReduce airline-airport ranking analysis."""

from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from src.mapreduce.mapreduce_logic import emit_pair, iter_flight_records
except ModuleNotFoundError:  # pragma: no cover - Hadoop Streaming localized file fallback
    from mapreduce_logic import emit_pair, iter_flight_records


def main() -> int:
    for record in iter_flight_records(sys.stdin):
        emit_pair(
            [record.origin_airport],
            [record.airline_code, record.departure_delay, record.arrival_delay, record.cancelled],
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
