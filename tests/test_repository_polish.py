from pathlib import Path

import pytest

from scripts.clean_generated_artifacts import (
    ALLOWLISTED_DIRS,
    clean_directory,
    clean_generated_artifacts,
    resolve_allowlisted_dirs,
)


def create_project_tree(root: Path) -> None:
    for relative_path in ALLOWLISTED_DIRS:
        directory = root / relative_path
        directory.mkdir(parents=True, exist_ok=True)
        (directory / ".gitkeep").write_text("", encoding="utf-8")
    (root / "data" / "raw").mkdir(parents=True, exist_ok=True)
    (root / "data" / "raw" / ".gitkeep").write_text("", encoding="utf-8")
    (root / "report" / "tables").mkdir(parents=True, exist_ok=True)
    (root / "report" / "tables" / "benchmark_summary.md").write_text("evidence\n", encoding="utf-8")


def test_clean_generated_artifacts_removes_only_allowlisted_runtime_files(tmp_path):
    create_project_tree(tmp_path)
    prepared_file = tmp_path / "data" / "prepared" / "flights_2024_clean.parquet"
    generated_dir = tmp_path / "data" / "generated" / "flights_100k.parquet"
    output_file = tmp_path / "outputs" / "spark_sql" / "runtime_metrics.json"
    benchmark_log = tmp_path / "experiments" / "results" / "local" / "logs" / "run" / "stdout.log"
    raw_file = tmp_path / "data" / "raw" / "flight_data_2024.csv"
    report_table = tmp_path / "report" / "tables" / "benchmark_summary.md"

    prepared_file.write_text("prepared\n", encoding="utf-8")
    generated_dir.mkdir()
    (generated_dir / "part-00000.parquet").write_text("generated\n", encoding="utf-8")
    output_file.write_text("metrics\n", encoding="utf-8")
    benchmark_log.parent.mkdir(parents=True)
    benchmark_log.write_text("log\n", encoding="utf-8")
    raw_file.write_text("raw\n", encoding="utf-8")

    removed = clean_generated_artifacts(project_root=tmp_path)

    assert prepared_file in removed
    assert generated_dir in removed
    assert output_file in removed
    assert benchmark_log.parent.parent in removed
    assert not prepared_file.exists()
    assert not generated_dir.exists()
    assert not output_file.exists()
    assert not benchmark_log.exists()
    assert raw_file.exists()
    assert report_table.exists()
    assert (tmp_path / "data" / "prepared" / ".gitkeep").exists()
    assert (tmp_path / "outputs" / "spark_sql" / ".gitkeep").exists()


def test_clean_directory_rejects_paths_outside_allowlist(tmp_path):
    create_project_tree(tmp_path)
    allowlisted_dirs = resolve_allowlisted_dirs(tmp_path)

    with pytest.raises(ValueError, match="Refusing to clean non-allowlisted directory"):
        clean_directory(tmp_path / "data" / "raw", allowlisted_dirs=allowlisted_dirs)


def test_readme_is_ascii_and_documents_reproducibility_interfaces():
    readme = Path("README.md").read_text(encoding="utf-8")

    assert readme.isascii()
    assert "â" not in readme
    assert "|-- README.md" in readme
    assert "`-- raw/" in readme
    assert ".\\.venv\\Scripts\\python.exe -m pytest -q" in readme
    assert "make run-all-local" in readme
    assert "make clean" in readme
    assert "## Final Submission Checklist" in readme


def test_makefile_targets_are_implemented_not_placeholders():
    makefile = Path("Makefile").read_text(encoding="utf-8")

    assert "validate-spark-sql:" in makefile
    assert "validate-spark-core:" in makefile
    assert "validate-hive:" in makefile
    assert "run-all-local: run-spark-sql run-spark-core run-hive validate-spark-sql validate-spark-core validate-hive" in makefile
    assert "$(VENV_PYTHON) scripts/clean_generated_artifacts.py" in makefile
    assert "is not implemented yet" not in makefile
