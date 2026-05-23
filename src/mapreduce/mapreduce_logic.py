"""Shared logic for the Hadoop Streaming MapReduce implementation."""

from __future__ import annotations

import csv
import json
import math
import sys
from collections import Counter
from dataclasses import dataclass
from typing import Any, Iterable, Iterator, TextIO


CANONICAL_COLUMNS = [
    "flight_date",
    "month",
    "airline_code",
    "airline_name",
    "origin_airport",
    "destination_airport",
    "departure_delay",
    "arrival_delay",
    "cancelled",
    "diverted",
    "cancellation_code",
    "carrier_delay",
    "weather_delay",
    "nas_delay",
    "security_delay",
    "late_aircraft_delay",
]

DELAY_OUTPUT_COLUMNS = [
    "origin_airport",
    "month",
    "delay_range",
    "flight_count",
    "avg_departure_delay",
    "avg_arrival_delay",
    "top_1_cause",
    "top_1_count",
    "top_2_cause",
    "top_2_count",
    "top_3_cause",
    "top_3_count",
]

ALL_CAUSES_OUTPUT_COLUMNS = [
    "origin_airport",
    "month",
    "delay_range",
    "cause_rank",
    "cause",
    "cause_count",
]

RANKING_OUTPUT_COLUMNS = [
    "origin_airport",
    "airline",
    "flight_count",
    "avg_departure_delay",
    "avg_arrival_delay",
    "cancellation_rate",
    "airport_avg_departure_delay",
    "difference_from_airport_avg_departure_delay",
    "rank_at_airport",
]

CANCELLED_NO_DEPARTURE_DELAY_RANGE = "cancelled_no_departure_delay"
DELAY_RANGE_SORT_ORDER = {
    CANCELLED_NO_DEPARTURE_DELAY_RANGE: 0,
    "low": 1,
    "medium": 2,
    "high": 3,
}


@dataclass(frozen=True)
class FlightRecord:
    month: int
    airline_code: str
    origin_airport: str
    departure_delay: float | None
    arrival_delay: float | None
    cancelled: int
    cancellation_code: str | None
    carrier_delay: float | None
    weather_delay: float | None
    nas_delay: float | None
    security_delay: float | None
    late_aircraft_delay: float | None


@dataclass
class DelayAccumulator:
    flight_count: int = 0
    departure_sum: float = 0.0
    departure_count: int = 0
    arrival_sum: float = 0.0
    arrival_count: int = 0
    cause_counts: Counter[str] | None = None

    def __post_init__(self) -> None:
        if self.cause_counts is None:
            self.cause_counts = Counter()


@dataclass
class AirlineAccumulator:
    flight_count: int = 0
    departure_sum: float = 0.0
    departure_count: int = 0
    arrival_sum: float = 0.0
    arrival_count: int = 0
    cancelled_count: int = 0


def blank_to_none(value: str | None) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text if text else None


def parse_int(value: str | None) -> int | None:
    text = blank_to_none(value)
    if text is None:
        return None
    return int(float(text))


def parse_float(value: str | None) -> float | None:
    text = blank_to_none(value)
    if text is None:
        return None
    number = float(text)
    if math.isnan(number):
        return None
    return number


def is_header_row(row: list[str]) -> bool:
    return row == CANONICAL_COLUMNS or (bool(row) and row[0] == CANONICAL_COLUMNS[0])


def record_from_row(row: list[str]) -> FlightRecord:
    if len(row) != len(CANONICAL_COLUMNS):
        raise ValueError(f"Expected {len(CANONICAL_COLUMNS)} fields, found {len(row)}")
    values = dict(zip(CANONICAL_COLUMNS, row))
    month = parse_int(values["month"])
    cancelled = parse_int(values["cancelled"])
    airline_code = blank_to_none(values["airline_code"])
    origin_airport = blank_to_none(values["origin_airport"])
    if month is None or cancelled is None or airline_code is None or origin_airport is None:
        raise ValueError("Canonical CSV row is missing a required structural field")

    return FlightRecord(
        month=month,
        airline_code=airline_code,
        origin_airport=origin_airport,
        departure_delay=parse_float(values["departure_delay"]),
        arrival_delay=parse_float(values["arrival_delay"]),
        cancelled=cancelled,
        cancellation_code=blank_to_none(values["cancellation_code"]),
        carrier_delay=parse_float(values["carrier_delay"]),
        weather_delay=parse_float(values["weather_delay"]),
        nas_delay=parse_float(values["nas_delay"]),
        security_delay=parse_float(values["security_delay"]),
        late_aircraft_delay=parse_float(values["late_aircraft_delay"]),
    )


def iter_flight_records(stream: TextIO, *, strict: bool = True) -> Iterator[FlightRecord]:
    reader = csv.reader(stream)
    for line_number, row in enumerate(reader, start=1):
        if not row or is_header_row(row):
            continue
        try:
            yield record_from_row(row)
        except ValueError as exc:
            print("reporter:counter:MapReduce,Malformed canonical rows,1", file=sys.stderr)
            print(f"Malformed canonical CSV row {line_number}: {exc}", file=sys.stderr)
            if strict:
                raise


def json_key(values: Iterable[Any]) -> str:
    return json.dumps(list(values), ensure_ascii=True, separators=(",", ":"))


def parse_json_key(value: str) -> list[Any]:
    decoded = json.loads(value)
    if not isinstance(decoded, list):
        raise ValueError(f"Reducer key is not a JSON list: {value}")
    return decoded


def emit_pair(key: Iterable[Any], value: Any, stream: TextIO = sys.stdout) -> None:
    print(f"{json_key(key)}\t{json.dumps(value, ensure_ascii=True, separators=(',', ':'))}", file=stream)


def iter_key_values(stream: TextIO) -> Iterator[tuple[str, Any]]:
    for line in stream:
        text = line.rstrip("\n")
        if not text:
            continue
        key, payload = text.split("\t", 1)
        yield key, json.loads(payload)


def grouped_key_values(stream: TextIO) -> Iterator[tuple[str, list[Any]]]:
    current_key: str | None = None
    values: list[Any] = []
    for key, value in iter_key_values(stream):
        if current_key is None:
            current_key = key
        if key != current_key:
            yield current_key, values
            current_key = key
            values = []
        values.append(value)
    if current_key is not None:
        yield current_key, values


def sql_avg(total: float, count: int) -> float | None:
    if count == 0:
        return None
    return total / count


def nullable_number_sort_value(value: float | None) -> tuple[int, float]:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return (1, 0.0)
    return (0, value)


def delay_range(departure_delay: float) -> str:
    if departure_delay < 15:
        return "low"
    if departure_delay <= 60:
        return "medium"
    return "high"


def derived_cause(record: FlightRecord) -> str:
    if record.cancelled == 1 and record.cancellation_code is not None:
        return f"cancellation:{record.cancellation_code}"

    causes = [
        ("delay:carrier", record.carrier_delay or 0.0),
        ("delay:weather", record.weather_delay or 0.0),
        ("delay:nas", record.nas_delay or 0.0),
        ("delay:security", record.security_delay or 0.0),
        ("delay:late_aircraft", record.late_aircraft_delay or 0.0),
    ]
    cause, value = max(causes, key=lambda item: item[1])
    if value <= 0.0:
        return "unknown"
    return cause


def cancellation_cause(record: FlightRecord) -> str:
    if record.cancellation_code is None:
        return "cancellation:unknown"
    return f"cancellation:{record.cancellation_code}"


def all_positive_causes(record: FlightRecord) -> list[str]:
    causes = []
    for label, value in (
        ("delay:carrier", record.carrier_delay),
        ("delay:weather", record.weather_delay),
        ("delay:nas", record.nas_delay),
        ("delay:security", record.security_delay),
        ("delay:late_aircraft", record.late_aircraft_delay),
    ):
        if (value or 0.0) > 0.0:
            causes.append(label)

    if record.cancelled == 1 and record.cancellation_code is not None:
        causes.append(f"cancellation:{record.cancellation_code}")
    return causes


def delay_key_value(record: FlightRecord) -> tuple[list[Any], list[Any]] | None:
    if record.departure_delay is None:
        if record.cancelled != 1:
            return None
        return (
            [record.origin_airport, record.month, CANCELLED_NO_DEPARTURE_DELAY_RANGE],
            [None, record.arrival_delay, cancellation_cause(record)],
        )
    return (
        [record.origin_airport, record.month, delay_range(record.departure_delay)],
        [record.departure_delay, record.arrival_delay, derived_cause(record)],
    )


def all_causes_key_values(record: FlightRecord) -> list[tuple[list[Any], str]]:
    if record.departure_delay is None:
        if record.cancelled != 1:
            return []
        key = [record.origin_airport, record.month, CANCELLED_NO_DEPARTURE_DELAY_RANGE]
    else:
        key = [record.origin_airport, record.month, delay_range(record.departure_delay)]
    return [(key, cause) for cause in all_positive_causes(record)]


def add_delay_value(accumulator: DelayAccumulator, value: list[Any]) -> None:
    departure_delay = parse_float(str(value[0])) if value[0] is not None else None
    arrival_delay = parse_float(str(value[1])) if value[1] is not None else None
    cause = str(value[2])
    accumulator.flight_count += 1
    if departure_delay is not None:
        accumulator.departure_sum += departure_delay
        accumulator.departure_count += 1
    if arrival_delay is not None:
        accumulator.arrival_sum += arrival_delay
        accumulator.arrival_count += 1
    assert accumulator.cause_counts is not None
    accumulator.cause_counts[cause] += 1


def top_three_causes(cause_counts: Counter[str]) -> tuple[str | None, int, str | None, int, str | None, int]:
    ordered = sorted(cause_counts.items(), key=lambda item: (-item[1], item[0]))
    padded: list[tuple[str | None, int]] = [(cause, count) for cause, count in ordered[:3]]
    while len(padded) < 3:
        padded.append((None, 0))
    return (
        padded[0][0],
        padded[0][1],
        padded[1][0],
        padded[1][1],
        padded[2][0],
        padded[2][1],
    )


def delay_row_from_group(key: list[Any], values: list[Any]) -> list[Any]:
    origin_airport, month, range_label = key
    accumulator = DelayAccumulator()
    for value in values:
        add_delay_value(accumulator, value)
    assert accumulator.cause_counts is not None
    top_1_cause, top_1_count, top_2_cause, top_2_count, top_3_cause, top_3_count = top_three_causes(
        accumulator.cause_counts
    )
    return [
        origin_airport,
        int(month),
        range_label,
        accumulator.flight_count,
        sql_avg(accumulator.departure_sum, accumulator.departure_count),
        sql_avg(accumulator.arrival_sum, accumulator.arrival_count),
        top_1_cause,
        top_1_count,
        top_2_cause,
        top_2_count,
        top_3_cause,
        top_3_count,
    ]


def all_causes_rows_from_group(key: list[Any], values: list[Any]) -> list[list[Any]]:
    origin_airport, month, range_label = key
    cause_counts = Counter(str(value) for value in values)
    ordered = sorted(cause_counts.items(), key=lambda item: (-item[1], item[0]))
    return [
        [origin_airport, int(month), range_label, rank, cause, count]
        for rank, (cause, count) in enumerate(ordered, start=1)
    ]


def add_airline_value(accumulator: AirlineAccumulator, value: list[Any]) -> None:
    departure_delay = parse_float(str(value[0])) if value[0] is not None else None
    arrival_delay = parse_float(str(value[1])) if value[1] is not None else None
    cancelled = int(value[2])
    accumulator.flight_count += 1
    if departure_delay is not None:
        accumulator.departure_sum += departure_delay
        accumulator.departure_count += 1
    if arrival_delay is not None:
        accumulator.arrival_sum += arrival_delay
        accumulator.arrival_count += 1
    if cancelled == 1:
        accumulator.cancelled_count += 1


def ranking_rows_from_group(origin_airport: str, values: list[Any]) -> list[list[Any]]:
    airline_stats: dict[str, AirlineAccumulator] = {}
    airport_departure_sum = 0.0
    airport_departure_count = 0

    for value in values:
        airline = str(value[0])
        stats_value = value[1:]
        accumulator = airline_stats.setdefault(airline, AirlineAccumulator())
        add_airline_value(accumulator, stats_value)
        departure_delay = parse_float(str(stats_value[0])) if stats_value[0] is not None else None
        if departure_delay is not None:
            airport_departure_sum += departure_delay
            airport_departure_count += 1

    airport_avg_departure_delay = sql_avg(airport_departure_sum, airport_departure_count)
    base_rows: list[tuple[str, int, float | None, float | None, float]] = []
    for airline, accumulator in airline_stats.items():
        avg_departure_delay = sql_avg(accumulator.departure_sum, accumulator.departure_count)
        avg_arrival_delay = sql_avg(accumulator.arrival_sum, accumulator.arrival_count)
        cancellation_rate = accumulator.cancelled_count / accumulator.flight_count
        base_rows.append(
            (
                airline,
                accumulator.flight_count,
                avg_departure_delay,
                avg_arrival_delay,
                cancellation_rate,
            )
        )

    ordered = sorted(base_rows, key=lambda row: (nullable_number_sort_value(row[2]), row[0]))
    ranked_rows: list[list[Any]] = []
    previous_delay_key: tuple[int, float] | None = None
    current_rank = 0
    for position, row in enumerate(ordered, start=1):
        airline, flight_count, avg_departure_delay, avg_arrival_delay, cancellation_rate = row
        delay_key = nullable_number_sort_value(avg_departure_delay)
        if delay_key != previous_delay_key:
            current_rank = position
            previous_delay_key = delay_key

        difference = None
        if avg_departure_delay is not None and airport_avg_departure_delay is not None:
            difference = avg_departure_delay - airport_avg_departure_delay

        ranked_rows.append(
            [
                origin_airport,
                airline,
                flight_count,
                avg_departure_delay,
                avg_arrival_delay,
                cancellation_rate,
                airport_avg_departure_delay,
                difference,
                current_rank,
            ]
        )
    return ranked_rows


def delay_output_sort_key(row: list[Any]) -> tuple[str, int, int, str]:
    return str(row[0]), int(row[1]), DELAY_RANGE_SORT_ORDER.get(str(row[2]), 99), str(row[2])


def all_causes_output_sort_key(row: list[Any]) -> tuple[str, int, int, str, int, str]:
    return str(row[0]), int(row[1]), DELAY_RANGE_SORT_ORDER.get(str(row[2]), 99), str(row[2]), int(row[3]), str(row[4])


def ranking_output_sort_key(row: list[Any]) -> tuple[str, int, tuple[int, float], str]:
    return str(row[0]), int(row[8]), nullable_number_sort_value(row[3]), str(row[1])


def row_as_json(row: list[Any], stream: TextIO = sys.stdout) -> None:
    print(json.dumps(row, ensure_ascii=True, separators=(",", ":")), file=stream)
