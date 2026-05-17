"""Environment smoke checks for the flight delay big-data project."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


EXPECTED_PYTHON = (3, 12)
EXPECTED_PYSPARK = "4.1.1"


def run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, capture_output=True, text=True, check=False)


def print_ok(label: str, detail: str) -> None:
    print(f"[OK] {label}: {detail}")


def print_fail(label: str, detail: str) -> None:
    print(f"[FAIL] {label}: {detail}")


def java_command() -> str | None:
    java_home = os.environ.get("JAVA_HOME")
    if java_home:
        candidate = Path(java_home) / "bin" / ("java.exe" if os.name == "nt" else "java")
        if candidate.exists():
            return str(candidate)
    return shutil.which("java")


def check_python() -> bool:
    version = sys.version_info
    detail = f"{version.major}.{version.minor}.{version.micro}"
    if (version.major, version.minor) == EXPECTED_PYTHON:
        print_ok("Python", detail)
        return True
    print_fail("Python", f"expected 3.12.x, found {detail}")
    return False


def check_pyspark_import() -> bool:
    try:
        import pyspark
    except Exception as exc:  # pragma: no cover - smoke-check diagnostics
        print_fail("PySpark import", str(exc))
        return False

    if pyspark.__version__ == EXPECTED_PYSPARK:
        print_ok("PySpark", pyspark.__version__)
        return True
    print_fail("PySpark", f"expected {EXPECTED_PYSPARK}, found {pyspark.__version__}")
    return False


def check_spark_session() -> bool:
    try:
        from pyspark.sql import SparkSession

        spark = (
            SparkSession.builder.master("local[*]")
            .appName("flight-delay-check-env")
            .getOrCreate()
        )
        version = spark.version
        spark.stop()
    except Exception as exc:  # pragma: no cover - smoke-check diagnostics
        print_fail("SparkSession", str(exc))
        return False

    if version == EXPECTED_PYSPARK:
        print_ok("SparkSession", version)
        return True
    print_fail("SparkSession", f"expected {EXPECTED_PYSPARK}, found {version}")
    return False


def check_java() -> bool:
    command = java_command()
    if not command:
        print_fail("Java", "java was not found on PATH or JAVA_HOME")
        return False

    result = run_command([command, "-version"])
    output = (result.stderr or result.stdout).strip()
    match = re.search(r'version "(\d+)(?:\.\d+)*', output)
    if result.returncode != 0 or not match:
        print_fail("Java", output or "unable to read java -version")
        return False

    major = int(match.group(1))
    first_line = output.splitlines()[0]
    if major >= 17:
        print_ok("Java", first_line)
        return True
    print_fail("Java", f"expected Java 17+, found {first_line}")
    return False


def check_make() -> bool:
    command = shutil.which("make")
    if not command:
        print_fail("Make", "make was not found on PATH")
        return False

    result = run_command([command, "--version"])
    first_line = (result.stdout or result.stderr).splitlines()[0]
    if result.returncode == 0:
        print_ok("Make", first_line)
        return True
    print_fail("Make", first_line or "make --version failed")
    return False


def check_docker() -> bool:
    command = shutil.which("docker")
    if not command:
        print_fail("Docker CLI", "docker was not found on PATH")
        return False

    docker_version = run_command([command, "--version"])
    if docker_version.returncode != 0:
        print_fail("Docker CLI", docker_version.stderr.strip() or docker_version.stdout.strip())
        return False
    print_ok("Docker CLI", docker_version.stdout.strip())

    compose_version = run_command([command, "compose", "version"])
    if compose_version.returncode != 0:
        print_fail("Docker Compose", compose_version.stderr.strip() or compose_version.stdout.strip())
        return False
    print_ok("Docker Compose", compose_version.stdout.strip())

    docker_info = run_command([command, "info", "--format", "{{.ServerVersion}}"])
    if docker_info.returncode != 0:
        print_fail(
            "Docker daemon",
            "Docker Desktop is installed, but the daemon is not reachable. Start Docker Desktop and retry.",
        )
        return False
    print_ok("Docker daemon", docker_info.stdout.strip())
    return True


def main() -> int:
    checks = [
        check_python(),
        check_pyspark_import(),
        check_java(),
        check_make(),
        check_docker(),
        check_spark_session(),
    ]
    if all(checks):
        print("Environment check passed.")
        return 0
    print("Environment check failed.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
