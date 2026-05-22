"""Small URI helpers shared by local and EMR runtime paths."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


def is_s3_uri(value: str | Path | None) -> bool:
    return str(value or "").lower().startswith("s3://")


def parse_s3_uri(uri: str) -> tuple[str, str]:
    parsed = urlparse(uri)
    if parsed.scheme != "s3" or not parsed.netloc:
        raise ValueError(f"Not a valid S3 URI: {uri}")
    return parsed.netloc, parsed.path.lstrip("/")


def join_uri(base: str | Path, *parts: str) -> str:
    base_text = str(base).replace("\\", "/")
    cleaned_parts = [part.strip("/").replace("\\", "/") for part in parts if str(part).strip("/")]
    if is_s3_uri(base_text):
        return "/".join([base_text.rstrip("/"), *cleaned_parts])
    return str(Path(base_text, *cleaned_parts))


def ensure_trailing_slash(uri: str) -> str:
    return uri if uri.endswith("/") else f"{uri}/"


def resolve_local_or_uri(value: str | Path, project_root: Path) -> str:
    text = str(value)
    if is_s3_uri(text):
        return text
    path = Path(text)
    if not path.is_absolute():
        path = project_root / path
    return str(path)


def display_location(value: str | Path, project_root: Path) -> str:
    text = str(value)
    if is_s3_uri(text):
        return text
    path = Path(text)
    try:
        return path.relative_to(project_root).as_posix()
    except ValueError:
        return path.as_posix()


def location_exists(value: str | Path) -> bool:
    if is_s3_uri(value):
        return True
    return Path(value).exists()


def write_text_location(value: str | Path, text: str) -> None:
    location = str(value)
    if is_s3_uri(location):
        import boto3

        bucket, key = parse_s3_uri(location)
        boto3.client("s3").put_object(Bucket=bucket, Key=key, Body=text.encode("utf-8"))
        return

    path = Path(location)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json_location(value: str | Path, payload: dict[str, Any]) -> None:
    write_text_location(value, json.dumps(payload, indent=2, sort_keys=True) + "\n")
