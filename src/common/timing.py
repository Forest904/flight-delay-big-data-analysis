"""Small helpers for comparable runtime phase metrics."""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import TypeVar


MATERIALIZATION_MODE_SMALL_RESULT = "small_result_collect_once"

T = TypeVar("T")


def rounded_seconds(started: float) -> float:
    return round(time.perf_counter() - started, 6)


def timed_call(function: Callable[[], T]) -> tuple[T, float]:
    started = time.perf_counter()
    result = function()
    return result, rounded_seconds(started)
