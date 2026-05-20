from pathlib import Path

from scripts import generate_environment_summary


def test_dockerfile_base_image_reads_from_line(tmp_path):
    dockerfile = tmp_path / "Dockerfile.hive"
    dockerfile.write_text("# syntax=docker/dockerfile:1.6\nFROM apache/hive:4.0.1\n", encoding="utf-8")

    assert generate_environment_summary.dockerfile_base_image(dockerfile) == "apache/hive:4.0.1"


def test_collect_runtime_records_keeps_missing_commands_as_values(monkeypatch):
    def fake_run_command(command, timeout_seconds=20):
        if command[:2] == ["docker", "--version"]:
            return "unavailable (docker missing)"
        if command[:2] == ["docker", "compose"]:
            return "unavailable (compose missing)"
        if command[0] == "java":
            return 'openjdk version "17.0.19"'
        return "available"

    monkeypatch.setattr(generate_environment_summary, "run_command", fake_run_command)
    monkeypatch.setattr(generate_environment_summary, "dockerfile_base_image", lambda path: "apache/hive:4.0.1")
    records = []

    generate_environment_summary.collect_runtime_records(records)

    by_item = {record["item"]: record["value"] for record in records}
    assert by_item["docker_version"] == "unavailable (docker missing)"
    assert by_item["docker_compose_version"] == "unavailable (compose missing)"
    assert by_item["hive_base_image"] == "apache/hive:4.0.1"


def test_write_environment_summary_writes_csv_md_and_json(tmp_path):
    records = [
        {"category": "host", "item": "cpu_model", "value": "Test CPU", "source": "test"},
    ]

    paths = generate_environment_summary.write_environment_summary(tmp_path, records)

    assert {path.name for path in paths} == {
        "environment_summary.csv",
        "environment_summary.md",
        "environment_summary.json",
    }
    assert "Test CPU" in tmp_path.joinpath("environment_summary.md").read_text(encoding="utf-8")
