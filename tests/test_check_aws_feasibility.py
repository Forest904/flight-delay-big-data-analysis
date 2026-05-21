from pathlib import Path

from scripts.check_aws_feasibility import (
    CheckResult,
    choose_instance_type,
    load_env_file,
    parse_budget,
    print_results,
    write_report_files,
)


def test_load_env_file_preserves_existing_values_by_default(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("AWS_DEFAULT_REGION=us-east-1\nAWS_ACCESS_KEY_ID=from_file\n", encoding="utf-8")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "already_set")

    load_env_file(env_file)

    assert "us-east-1" == __import__("os").environ["AWS_DEFAULT_REGION"]
    assert "already_set" == __import__("os").environ["AWS_ACCESS_KEY_ID"]


def test_parse_budget_accepts_plain_or_dollar_values():
    assert parse_budget("50") == 50
    assert parse_budget("$49.50") == 49.5
    assert parse_budget("not money") is None
    assert parse_budget(None) is None


def test_choose_instance_type_uses_configured_fallback_order_first():
    supported = [{"Type": "m5.large", "VCPU": 2, "MemoryGB": 8}, {"Type": "m5.xlarge", "VCPU": 4, "MemoryGB": 16}]

    chosen, reason = choose_instance_type(supported, ["m5.xlarge", "m5.large"])

    assert chosen == "m5.xlarge"
    assert reason == "configured fallback order"


def test_choose_instance_type_falls_back_to_largest_supported():
    supported = [{"Type": "c5.large", "VCPU": 2, "MemoryGB": 4}, {"Type": "r5.xlarge", "VCPU": 4, "MemoryGB": 32}]

    chosen, reason = choose_instance_type(supported, ["m5.xlarge", "m5.large"])

    assert chosen == "r5.xlarge"
    assert reason == "largest EMR-supported type returned by AWS"


def test_write_report_files_creates_json_csv_and_markdown(tmp_path):
    results = [
        CheckResult("service", "s3", "pass", True, "ListBuckets succeeded"),
        CheckResult("logging", "cloudwatch logs", "warn", False, "restricted"),
    ]

    write_report_files(results, tmp_path)

    assert (tmp_path / "aws_feasibility.json").exists()
    assert (tmp_path / "aws_feasibility.csv").exists()
    assert (tmp_path / "aws_feasibility.md").exists()
    assert "cloudwatch logs" in (tmp_path / "aws_feasibility.md").read_text(encoding="utf-8")


def test_print_results_reports_required_failures(capsys):
    results = [CheckResult("service", "emr", "fail", True, "denied")]

    print_results(results)

    assert "AWS feasibility check failed" in capsys.readouterr().out
