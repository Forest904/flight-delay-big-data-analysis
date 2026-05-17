"""Inspect the configured raw flight dataset without loading it into memory."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOCAL_CONFIG = PROJECT_ROOT / "config" / "local.yaml"
COLUMNS_CONFIG = PROJECT_ROOT / "config" / "columns.yaml"
SAMPLE_ROWS = 5

TYPE_ORDER = ("integer", "float", "date", "string")


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)
    if not isinstance(data, dict):
        raise ValueError(f"{path} did not contain a YAML mapping")
    return data


def resolve_project_path(path_value: str) -> Path:
    path = Path(path_value)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path


def is_missing(value: str | None) -> bool:
    return value is None or value.strip() == ""


def infer_value_type(value: str) -> str:
    text = value.strip()
    if re.fullmatch(r"[+-]?\d+", text):
        return "integer"
    if re.fullmatch(r"[+-]?(?:\d+\.\d*|\d*\.\d+)(?:[eE][+-]?\d+)?", text):
        return "float"
    try:
        datetime.fromisoformat(text)
    except ValueError:
        return "string"
    return "date"


def merge_type(current: str | None, new_type: str) -> str:
    if current is None:
        return new_type
    if current == new_type:
        return current
    if {current, new_type} <= {"integer", "float"}:
        return "float"
    return TYPE_ORDER[max(TYPE_ORDER.index(current), TYPE_ORDER.index(new_type))]


def build_column_mapping(header: list[str], columns_config: dict[str, Any]) -> dict[str, str | None]:
    aliases = columns_config.get("aliases", {})
    canonical_columns = columns_config.get("canonical_columns", [])
    header_lookup = {name.lower(): name for name in header}

    mapping: dict[str, str | None] = {}
    for canonical in canonical_columns:
        candidates = aliases.get(canonical, [])
        source = None
        for candidate in candidates:
            source = header_lookup.get(str(candidate).lower())
            if source:
                break
        mapping[canonical] = source
    return mapping


def inspect_dataset(raw_file: Path, columns_config: dict[str, Any]) -> dict[str, Any]:
    with raw_file.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames is None:
            raise ValueError(f"{raw_file} does not have a header row")

        header = list(reader.fieldnames)
        mapping = build_column_mapping(header, columns_config)
        critical_sources = sorted({source for source in mapping.values() if source})

        row_count = 0
        sample_rows: list[dict[str, str]] = []
        null_counts: Counter[str] = Counter()
        inferred_types: dict[str, str | None] = {column: None for column in header}
        non_null_counts: Counter[str] = Counter()

        for row in reader:
            row_count += 1
            if len(sample_rows) < SAMPLE_ROWS:
                sample_rows.append(dict(row))

            for column in header:
                value = row.get(column)
                if is_missing(value):
                    continue
                non_null_counts[column] += 1
                inferred_types[column] = merge_type(inferred_types[column], infer_value_type(value or ""))

            for source in critical_sources:
                if is_missing(row.get(source)):
                    null_counts[source] += 1

    schema = [
        {
            "column": column,
            "inferred_type": inferred_types[column] or "all_null",
            "non_null_count": non_null_counts[column],
        }
        for column in header
    ]
    mapped_null_counts = {
        canonical: {
            "source_column": source,
            "null_count": null_counts[source] if source else None,
            "null_pct": round((null_counts[source] / row_count) * 100, 4)
            if source and row_count
            else None,
        }
        for canonical, source in mapping.items()
    }

    return {
        "raw_file": str(raw_file.relative_to(PROJECT_ROOT)),
        "file_size_bytes": raw_file.stat().st_size,
        "row_count": row_count,
        "column_count": len(header),
        "columns": header,
        "schema": schema,
        "canonical_mapping": mapping,
        "critical_null_counts": mapped_null_counts,
        "sample_rows": sample_rows,
    }


def print_report(result: dict[str, Any]) -> None:
    print("# Raw Dataset Inspection")
    print()
    print(f"Raw file: {result['raw_file']}")
    print(f"File size bytes: {result['file_size_bytes']}")
    print(f"Rows: {result['row_count']}")
    print(f"Columns: {result['column_count']}")
    print()

    print("## Schema")
    print("column,inferred_type,non_null_count")
    for column in result["schema"]:
        print(f"{column['column']},{column['inferred_type']},{column['non_null_count']}")
    print()

    print("## Canonical Mapping")
    print("canonical_column,source_column")
    for canonical, source in result["canonical_mapping"].items():
        print(f"{canonical},{source or 'MISSING'}")
    print()

    print("## Critical Null Counts")
    print("canonical_column,source_column,null_count,null_pct")
    for canonical, detail in result["critical_null_counts"].items():
        print(
            f"{canonical},{detail['source_column'] or 'MISSING'},"
            f"{detail['null_count'] if detail['null_count'] is not None else 'N/A'},"
            f"{detail['null_pct'] if detail['null_pct'] is not None else 'N/A'}"
        )
    print()

    print("## Sample Rows")
    print(json.dumps(result["sample_rows"], indent=2))


def main() -> int:
    local_config = load_yaml(LOCAL_CONFIG)
    columns_config = load_yaml(COLUMNS_CONFIG)

    raw_file_value = local_config.get("paths", {}).get("raw_file")
    if not raw_file_value:
        raise ValueError(f"{LOCAL_CONFIG} does not define paths.raw_file")

    raw_file = resolve_project_path(str(raw_file_value))
    if not raw_file.exists():
        raise FileNotFoundError(
            f"Configured raw dataset was not found: {raw_file}. "
            "Place the Kaggle CSV there or update config/local.yaml."
        )

    result = inspect_dataset(raw_file, columns_config)
    print_report(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
