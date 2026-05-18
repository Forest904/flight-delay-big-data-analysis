"""Runtime helpers that do not import PySpark."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


def run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, capture_output=True, text=True, check=False)


def java_major_version(java_command: Path | str) -> int | None:
    result = run_command([str(java_command), "-version"])
    output = result.stderr or result.stdout
    if result.returncode != 0:
        return None
    match = re.search(r'version "([^"]+)"', output)
    if not match:
        return None
    version_text = match.group(1)
    if version_text.startswith("1."):
        return int(version_text.split(".")[1])
    return int(version_text.split(".")[0])


def java_executable(java_home: Path) -> Path:
    executable = "java.exe" if os.name == "nt" else "java"
    return java_home / "bin" / executable


def candidate_java_homes() -> list[Path]:
    candidates: list[Path] = []
    java_home = os.environ.get("JAVA_HOME")
    if java_home:
        candidates.append(Path(java_home))

    if os.name == "nt":
        roots = [
            Path("C:/Program Files/Eclipse Adoptium"),
            Path("C:/Program Files/Java"),
            Path("C:/Program Files/Microsoft"),
            Path.home() / "AppData/Local/Programs/Eclipse Adoptium",
        ]
        for root in roots:
            if root.exists():
                candidates.extend(sorted(root.glob("jdk-*"), reverse=True))

    return candidates


def ensure_java_17() -> None:
    active_java = shutil.which("java")
    if active_java and (java_major_version(active_java) or 0) >= 17:
        return

    for java_home in candidate_java_homes():
        executable = java_executable(java_home)
        if executable.exists() and (java_major_version(executable) or 0) >= 17:
            os.environ["JAVA_HOME"] = str(java_home)
            os.environ["PATH"] = str(java_home / "bin") + os.pathsep + os.environ.get("PATH", "")
            return

    active_detail = active_java or "not found"
    raise RuntimeError(
        "PySpark requires Java 17 or newer for this project, but the active Java "
        f"runtime is {active_detail}. Install Java 17+ or set JAVA_HOME to a JDK 17+ directory."
    )


def configure_pyspark_python(python_executable: str | Path | None = None) -> str:
    executable = str(Path(python_executable or sys.executable).resolve())
    if os.name == "nt":
        short_executable = windows_short_path(executable)
        if short_executable is not None:
            executable = short_executable
    os.environ["PYSPARK_PYTHON"] = executable
    os.environ["PYSPARK_DRIVER_PYTHON"] = executable
    return executable


def windows_short_path(path: str) -> str | None:
    try:
        import ctypes
        from ctypes import wintypes
    except ImportError:
        return None

    get_short_path_name = ctypes.windll.kernel32.GetShortPathNameW
    get_short_path_name.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD]
    get_short_path_name.restype = wintypes.DWORD

    required = get_short_path_name(path, None, 0)
    if required == 0:
        return None
    buffer = ctypes.create_unicode_buffer(required)
    result = get_short_path_name(path, buffer, required)
    if result == 0:
        return None
    short_path = buffer.value
    return short_path or None
