"""Safely remove generated local artifacts while preserving inputs and evidence."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PRESERVED_NAMES = {".gitkeep"}
ALLOWLISTED_DIRS = (
    Path("data/prepared"),
    Path("data/generated"),
    Path("outputs/spark_sql"),
    Path("outputs/spark_core"),
    Path("outputs/hive"),
    Path("outputs/mapreduce"),
    Path("experiments/results/local"),
    Path("experiments/results/docker-simulation"),
)


def resolve_project_root(project_root: Path | str | None = None) -> Path:
    root = Path(project_root) if project_root is not None else PROJECT_ROOT
    return root.resolve()


def resolve_allowlisted_dirs(project_root: Path | str | None = None) -> list[Path]:
    root = resolve_project_root(project_root)
    return [(root / relative_path).resolve() for relative_path in ALLOWLISTED_DIRS]


def ensure_allowlisted(target: Path, allowlisted_dirs: list[Path]) -> None:
    resolved_target = target.resolve()
    if resolved_target not in allowlisted_dirs:
        raise ValueError(f"Refusing to clean non-allowlisted directory: {resolved_target}")


def clean_directory(target: Path, *, dry_run: bool = False, allowlisted_dirs: list[Path] | None = None) -> list[Path]:
    allowed = allowlisted_dirs or resolve_allowlisted_dirs()
    ensure_allowlisted(target, allowed)

    removed: list[Path] = []
    if not target.exists():
        return removed

    for child in sorted(target.iterdir(), key=lambda path: path.name):
        if child.name in PRESERVED_NAMES:
            continue
        removed.append(child)
        if dry_run:
            continue
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()
    return removed


def clean_generated_artifacts(*, project_root: Path | str | None = None, dry_run: bool = False) -> list[Path]:
    root = resolve_project_root(project_root)
    allowlisted_dirs = resolve_allowlisted_dirs(root)
    removed: list[Path] = []
    for target in allowlisted_dirs:
        removed.extend(clean_directory(target, dry_run=dry_run, allowlisted_dirs=allowlisted_dirs))
    return removed


def relative_display(path: Path, project_root: Path) -> str:
    try:
        return path.relative_to(project_root).as_posix()
    except ValueError:
        return path.as_posix()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Remove generated data, outputs, and benchmark runtime artifacts.")
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT, help="Project root to clean.")
    parser.add_argument("--dry-run", action="store_true", help="Print paths that would be removed without deleting them.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = resolve_project_root(args.project_root)
    removed = clean_generated_artifacts(project_root=project_root, dry_run=args.dry_run)
    action = "would remove" if args.dry_run else "removed"
    if not removed:
        print("No generated artifacts to clean.")
        return 0
    for path in removed:
        print(f"{action}: {relative_display(path, project_root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
