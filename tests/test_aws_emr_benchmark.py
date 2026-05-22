from pathlib import Path

from scripts import aws_emr_benchmark
from src.common.uri import join_uri, parse_s3_uri


def minimal_config() -> dict:
    return {
        "environment": "aws-emr",
        "paths": {"results_dir": "experiments/results/aws-emr", "generated_dir": "data/generated"},
        "aws": {"region": "us-east-1"},
        "s3": {"bucket_env": "AWS_FLIGHT_DELAY_BUCKET", "prefix": "flight-delay"},
        "spark": {"shuffle_partitions": 24},
        "benchmark": {
            "canonical_run_id": "m4-emr-final-2",
            "execution_setting": "Amazon EMR test",
            "technologies": ["spark_sql", "spark_core"],
            "input_sizes": [
                {
                    "label": "100k",
                    "records": 100000,
                    "local_path": "data/generated/flights_100k.parquet",
                    "s3_path": "flight-delay/data/generated/flights_100k.parquet/",
                    "repetitions": 3,
                },
                {
                    "label": "14m",
                    "records": 14000000,
                    "local_path": "data/generated/flights_14m.parquet",
                    "s3_path": "flight-delay/data/generated/flights_14m.parquet/",
                    "repetitions": 1,
                    "max_repetitions": 3,
                },
            ],
        },
        "emr": {
            "release_label": "emr-7.13.0",
            "applications": ["Spark"],
            "cluster_profile": {"primary_nodes": 1, "core_nodes": 2, "instance_type": "m5.xlarge", "idle_timeout_seconds": 600},
            "iam_role_candidates": {
                "service_role": ["EMR_DefaultRole"],
                "ec2_instance_profile": ["EMR_EC2_DefaultRole"],
            },
        },
    }


def test_s3_uri_helpers_keep_s3_layout_intact():
    assert join_uri("s3://bucket/flight-delay", "results", "runs", "run") == "s3://bucket/flight-delay/results/runs/run"
    assert parse_s3_uri("s3://bucket/flight-delay/data/") == ("bucket", "flight-delay/data/")


def test_context_uses_bucket_env_and_results_dir(monkeypatch):
    monkeypatch.setenv("AWS_FLIGHT_DELAY_BUCKET", "flight-delay-test")

    context = aws_emr_benchmark.context_from_config(minimal_config())

    assert context.bucket == "flight-delay-test"
    assert context.prefix == "flight-delay"
    assert context.results_dir == aws_emr_benchmark.PROJECT_ROOT / "experiments" / "results" / "aws-emr"


def test_expand_benchmark_steps_applies_repetition_policy(monkeypatch):
    monkeypatch.setenv("AWS_FLIGHT_DELAY_BUCKET", "flight-delay-test")
    context = aws_emr_benchmark.context_from_config(minimal_config())
    manifest = {
        "datasets": [
            {"label": "100k", "actual_records": 100000, "validation_status": "success"},
            {"label": "14m", "actual_records": 14000000, "validation_status": "success"},
        ]
    }

    steps = aws_emr_benchmark.expand_benchmark_steps(context, "run123", manifest)

    assert len(steps) == 8
    assert sum(1 for step in steps if step.input_label == "100k") == 6
    assert sum(1 for step in steps if step.input_label == "14m") == 2
    assert steps[0].input_s3_uri == "s3://flight-delay-test/flight-delay/data/generated/flights_100k.parquet"
    assert steps[0].output_root_s3_uri.endswith("/outputs/100k/spark_sql/rep1/spark_sql")


def test_14m_repetitions_are_capped_by_max(monkeypatch):
    monkeypatch.setenv("AWS_EMR_14M_REPETITIONS", "5")

    entry = {"label": "14m", "repetitions": 1, "max_repetitions": 3}

    assert aws_emr_benchmark.repetition_count(entry) == 3


def test_build_spark_step_uses_spark_submit_and_output_root():
    step = aws_emr_benchmark.BenchmarkStep(
        input_label="100k",
        records=100000,
        technology="spark_core",
        repetition=1,
        input_s3_uri="s3://bucket/flight-delay/data/generated/flights_100k.parquet",
        output_root_s3_uri="s3://bucket/flight-delay/results/runs/run/outputs/100k/spark_core/rep1/spark_core",
    )

    spec = aws_emr_benchmark.build_spark_step(
        step,
        run_id="run",
        source_uri="s3://bucket/flight-delay/code/runs/run/source.zip",
        runtime_config_uri="s3://bucket/flight-delay/code/runs/run/aws_emr_runtime.yaml",
    )

    command = " ".join(spec["HadoopJarStep"]["Args"])
    assert spec["HadoopJarStep"]["Jar"] == "command-runner.jar"
    assert "spark-submit --master yarn" in command
    assert "src/spark_core/run_spark_core.py" in command
    assert "--input-path s3://bucket/flight-delay/data/generated/flights_100k.parquet" in command
    assert "--output-root s3://bucket/flight-delay/results/runs/run/outputs/100k/spark_core/rep1/spark_core" in command


def test_normalize_step_rows_matches_benchmark_csv_schema():
    step = aws_emr_benchmark.BenchmarkStep(
        input_label="100k",
        records=100000,
        technology="spark_sql",
        repetition=2,
        input_s3_uri="s3://bucket/input",
        output_root_s3_uri="s3://bucket/output/spark_sql",
    )

    rows = aws_emr_benchmark.normalize_step_rows(
        step,
        run_id="run",
        timestamp_utc="2026-05-22T12:00:00+00:00",
        execution_setting="Amazon EMR",
        metrics={
            "status": "success",
            "stage": "complete",
            "jobs": [
                {
                    "job_name": "delay_by_airport_month",
                    "duration_seconds": 1.5,
                    "output_rows": 12,
                    "status": "success",
                }
            ],
        },
        step_state="COMPLETED",
    )

    assert list(rows[0].keys()) == aws_emr_benchmark.BENCHMARK_COLUMNS
    assert rows[0]["environment"] == "aws-emr"
    assert rows[0]["repetition"] == 2


def test_normalize_step_rows_uses_configured_aws_environment_label():
    step = aws_emr_benchmark.BenchmarkStep(
        input_label="1m",
        records=1000000,
        technology="spark_sql",
        repetition=1,
        input_s3_uri="s3://bucket/input",
        output_root_s3_uri="s3://bucket/output/spark_sql",
    )

    rows = aws_emr_benchmark.normalize_step_rows(
        step,
        run_id="m5-emr-3core-1m-full",
        timestamp_utc="2026-05-22T12:00:00+00:00",
        execution_setting="Amazon EMR larger",
        environment="aws-emr-larger",
        metrics=None,
        step_state="COMPLETED",
    )

    assert rows[0]["environment"] == "aws-emr-larger"


def test_dependency_step_uses_pinned_dependencies():
    config = minimal_config()
    config["aws"]["dependencies"] = ["PyYAML==6.0.3", "pandas==2.3.3"]

    spec = aws_emr_benchmark.dependency_step(config)
    command = " ".join(spec["HadoopJarStep"]["Args"])

    assert "PyYAML==6.0.3" in command
    assert "pandas==2.3.3" in command
    assert "pip freeze" in command


def test_create_cluster_dry_run_includes_idle_auto_termination(monkeypatch, capsys):
    monkeypatch.setenv("AWS_FLIGHT_DELAY_BUCKET", "flight-delay-test")
    context = aws_emr_benchmark.context_from_config(minimal_config())

    cluster_id = aws_emr_benchmark.create_cluster(context, "run123", dry_run=True)
    output = capsys.readouterr().out

    assert cluster_id == "dry-run-run123"
    assert '"AutoTerminationPolicy"' in output
    assert '"IdleTimeout": 600' in output


def test_create_cluster_dry_run_can_use_three_core_nodes(monkeypatch, capsys):
    config = minimal_config()
    config["environment"] = "aws-emr-larger"
    config["emr"]["cluster_profile"]["core_nodes"] = 3
    monkeypatch.setenv("AWS_FLIGHT_DELAY_BUCKET", "flight-delay-test")
    context = aws_emr_benchmark.context_from_config(config)

    aws_emr_benchmark.create_cluster(context, "m5-emr-3core-1m-full", dry_run=True)
    output = capsys.readouterr().out

    assert '"InstanceRole": "CORE"' in output
    assert '"InstanceCount": 3' in output
    assert '"Value": "aws-emr-larger"' in output


def test_m5_larger_config_expands_to_twelve_benchmark_steps(monkeypatch):
    monkeypatch.setenv("AWS_FLIGHT_DELAY_BUCKET", "flight-delay-test")
    config = aws_emr_benchmark.load_yaml(Path("config/aws_emr_m5_larger.yaml"))
    context = aws_emr_benchmark.context_from_config(config)
    manifest = {
        "datasets": [
            {"label": "1m", "actual_records": 1000000, "validation_status": "success"},
        ]
    }

    steps = aws_emr_benchmark.expand_benchmark_steps(context, "m5-emr-3core-1m-full", manifest)

    assert len(steps) == 12
    assert {step.input_label for step in steps} == {"1m", "full"}
    assert sum(1 for step in steps if step.input_label == "1m") == 6
    assert sum(1 for step in steps if step.input_label == "full") == 6


def test_s3_input_prefix_validation_requires_parquet_objects(monkeypatch):
    class FakePaginator:
        def paginate(self, **_kwargs):
            return [{"Contents": [{"Key": "flight-delay/data/generated/flights_100k.parquet/part-00000.parquet"}]}]

    class FakeClient:
        def get_paginator(self, name):
            assert name == "list_objects_v2"
            return FakePaginator()

    class FakeSession:
        def client(self, name):
            assert name == "s3"
            return FakeClient()

    monkeypatch.setenv("AWS_FLIGHT_DELAY_BUCKET", "flight-delay-test")
    monkeypatch.setattr(aws_emr_benchmark, "boto3_session", lambda _ctx: FakeSession())
    context = aws_emr_benchmark.context_from_config(minimal_config())

    assert aws_emr_benchmark.s3_prefix_contains_parquet(
        context,
        "s3://flight-delay-test/flight-delay/data/generated/flights_100k.parquet",
    )


def test_missing_metrics_json_fails_clearly(monkeypatch):
    monkeypatch.setenv("AWS_FLIGHT_DELAY_BUCKET", "flight-delay-test")
    context = aws_emr_benchmark.context_from_config(minimal_config())
    monkeypatch.setattr(aws_emr_benchmark, "read_s3_json", lambda _ctx, _uri: None)

    try:
        aws_emr_benchmark.require_s3_json(context, "s3://bucket/results/runtime_metrics.json")
    except RuntimeError as exc:
        assert "Missing required runtime metrics JSON" in str(exc)
    else:
        raise AssertionError("require_s3_json should fail for missing metrics")


def test_run_manifest_records_audit_fields(monkeypatch, tmp_path):
    monkeypatch.setenv("AWS_FLIGHT_DELAY_BUCKET", "flight-delay-test")
    config_path = tmp_path / "aws_emr.yaml"
    config_path.write_text("environment: aws-emr\n", encoding="utf-8")
    context = aws_emr_benchmark.context_from_config(minimal_config())
    code_upload = aws_emr_benchmark.CodeUpload(
        source_uri="s3://bucket/code/source.zip",
        runtime_config_uri="s3://bucket/code/aws_emr_runtime.yaml",
        source_sha256="source-sha",
        runtime_config_sha256="config-sha",
    )

    manifest = aws_emr_benchmark.run_manifest(
        context,
        run_id="m4-emr-final-2",
        run_kind="full",
        code_upload=code_upload,
        config_path=config_path,
        cluster_id="j-123",
        status="success",
    )

    assert manifest["is_canonical_full_run"] is True
    assert manifest["aws"]["cluster_id"] == "j-123"
    assert manifest["artifacts"]["source_bundle_sha256"] == "source-sha"
    assert manifest["artifacts"]["config_sha256"] == aws_emr_benchmark.sha256_file(config_path)


def test_list_active_project_clusters_filters_by_tags(monkeypatch):
    class FakePaginator:
        def paginate(self, **_kwargs):
            return [{"Clusters": [{"Id": "j-keep"}, {"Id": "j-ignore"}]}]

    class FakeClient:
        def get_paginator(self, name):
            assert name == "list_clusters"
            return FakePaginator()

        def describe_cluster(self, ClusterId):
            tags = (
                [{"Key": "Project", "Value": "flight-delay-big-data-analysis"}, {"Key": "Environment", "Value": "aws-emr"}]
                if ClusterId == "j-keep"
                else [{"Key": "Project", "Value": "other"}]
            )
            return {"Cluster": {"Tags": tags}}

    class FakeSession:
        def client(self, name):
            assert name == "emr"
            return FakeClient()

    monkeypatch.setenv("AWS_FLIGHT_DELAY_BUCKET", "flight-delay-test")
    monkeypatch.setattr(aws_emr_benchmark, "boto3_session", lambda _ctx: FakeSession())
    context = aws_emr_benchmark.context_from_config(minimal_config())

    assert aws_emr_benchmark.list_active_project_clusters(context) == ["j-keep"]
