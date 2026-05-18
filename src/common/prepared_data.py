"""Helpers for reading prepared Parquet data across local platform quirks."""

from __future__ import annotations

import os
from pathlib import Path

from pyspark.sql import DataFrame, SparkSession


def has_windows_winutils() -> bool:
    if os.name != "nt":
        return True

    for env_name in ("HADOOP_HOME", "hadoop.home.dir"):
        value = os.environ.get(env_name)
        if not value:
            continue
        if (Path(value) / "bin" / "winutils.exe").exists():
            return True
    return False


def prepared_parquet_read_paths(prepared_path: str | Path) -> list[str]:
    path = Path(prepared_path)
    if os.name == "nt" and not has_windows_winutils() and path.is_dir():
        part_files = sorted(path.glob("*.parquet"))
        if not part_files:
            raise FileNotFoundError(f"No Parquet part files found under prepared dataset directory: {path}")
        return [str(part_file) for part_file in part_files]
    return [str(path)]


def read_prepared_parquet(spark: SparkSession, prepared_path: str | Path) -> DataFrame:
    return spark.read.parquet(*prepared_parquet_read_paths(prepared_path))
