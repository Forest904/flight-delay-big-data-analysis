"""Build the draft final report PDF with Pandoc.

The report source stays in Markdown so the evaluator-facing document can be
reviewed in Git. Pandoc and the selected PDF engine are external tools by
design; this script only provides a stable cross-platform entrypoint.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "report"
SOURCE = REPORT_DIR / "draft_final_report.md"
OUTPUT = REPORT_DIR / "draft_final_report.pdf"
DEFAULT_ENGINE = "xelatex"


def candidate_executable_paths(name: str) -> list[Path]:
    if os.name != "nt":
        return []

    executable = name if name.lower().endswith(".exe") else f"{name}.exe"
    candidates: list[Path] = []
    for env_var in ("LOCALAPPDATA", "ProgramFiles", "ProgramFiles(x86)"):
        base = os.environ.get(env_var)
        if not base:
            continue
        candidates.append(Path(base) / "Pandoc" / executable)
        candidates.append(Path(base) / "MiKTeX" / "miktex" / "bin" / "x64" / executable)
    return candidates


def require_executable(name: str, install_hint: str) -> str:
    path = shutil.which(name)
    if path:
        return path
    for candidate in candidate_executable_paths(name):
        if candidate.exists():
            return str(candidate)
    print(f"error: required executable '{name}' was not found on PATH.", file=sys.stderr)
    print(install_hint, file=sys.stderr)
    return ""


def main() -> int:
    if not SOURCE.exists():
        print(f"error: missing report source: {SOURCE}", file=sys.stderr)
        return 1

    engine = os.environ.get("PDF_ENGINE", DEFAULT_ENGINE)
    pandoc = require_executable(
        "pandoc",
        "Install Pandoc and rerun `make report`. On Windows, restart the shell "
        "after installation so pandoc.exe is visible on PATH.",
    )
    pdf_engine = require_executable(
        engine,
        f"Install a PDF engine that provides `{engine}`, or rerun with "
        "`PDF_ENGINE=<engine-name> make report`.",
    )
    if not pandoc or not pdf_engine:
        return 1

    command = [
        pandoc,
        str(SOURCE.name),
        "--from",
        "gfm+yaml_metadata_block",
        "--to",
        "pdf",
        "--pdf-engine",
        engine,
        "--standalone",
        "--toc",
        "--number-sections",
        "-V",
        "geometry:margin=1in",
        "-V",
        "colorlinks=true",
        "-o",
        str(OUTPUT.name),
    ]

    try:
        subprocess.run(command, cwd=REPORT_DIR, check=True)
    except subprocess.CalledProcessError as exc:
        print(f"error: pandoc failed with exit code {exc.returncode}.", file=sys.stderr)
        return exc.returncode

    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
