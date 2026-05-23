import csv
import re
from datetime import datetime, timezone
from pathlib import Path

import pytest

import experiments.run_benchmarks as run_benchmarks
from experiments.run_benchmarks import BenchmarkInput


def test_benchmark_csv_schema_is_stable(tmp_path):
    row = {
        "run_id": "20260520T120000Z",
        "repetition": 1,
        "technology": "spark_sql",
        "job_name": "delay_by_airport_month",
        "input_label": "100k",
        "records": 100000,
        "environment": "local",
        "execution_setting": "local",
        "duration_seconds": 1.25,
        "input_read_seconds": 0.1,
        "plan_build_seconds": 0.2,
        "result_collect_seconds": 0.3,
        "full_output_write_seconds": 0.4,
        "sample_output_write_seconds": 0.5,
        "materialization_mode": "small_result_collect_once",
        "output_rows": 10,
        "status": "success",
        "timestamp_utc": "2026-05-20T12:00:00+00:00",
        "input_path": "data/generated/flights_100k.parquet",
        "metrics_path": "outputs/spark_sql/runtime_metrics.json",
        "error": "",
        "stage": "complete",
    }
    output_path = tmp_path / "benchmark_20260520T120000123456Z.csv"

    run_benchmarks.write_benchmark_csv(output_path, [row])

    with output_path.open(newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        header = next(reader)

    assert header == run_benchmarks.BENCHMARK_COLUMNS
    assert re.fullmatch(r"benchmark_\d{8}T\d{12}Z\.csv", output_path.name)


def test_selected_benchmark_inputs_skip_optional_by_default(tmp_path):
    local_config = {
        "benchmark": {
            "input_sizes": [
                {"label": "100k", "records": 100000, "path": "data/generated/flights_100k.parquet"},
                {
                    "label": "14m",
                    "records": 14000000,
                    "path": "data/generated/flights_14m.parquet",
                    "optional": True,
                },
            ]
        }
    }
    manifest = {
        "datasets": [
            {
                "label": "100k",
                "actual_records": 100000,
                "path": "data/generated/flights_100k.parquet",
                "validation_status": "success",
            },
            {
                "label": "500k",
                "actual_records": 500000,
                "path": "data/generated/flights_500k.parquet",
                "validation_status": "success",
            },
            {
                "label": "1m",
                "actual_records": 1000000,
                "path": "data/generated/flights_1m.parquet",
                "validation_status": "success",
            },
            {
                "label": "14m",
                "actual_records": 14000000,
                "path": "data/generated/flights_14m.parquet",
                "validation_status": "success",
            },
        ]
    }

    selected = run_benchmarks.selected_benchmark_inputs(local_config, manifest, project_root=tmp_path)

    assert [item.label for item in selected] == ["100k"]


def test_parse_args_defaults_to_three_repetitions():
    args = run_benchmarks.parse_args([])

    assert args.repetitions == 3


def test_selected_benchmark_inputs_fail_when_required_manifest_entry_is_missing(tmp_path):
    local_config = {
        "benchmark": {
            "input_sizes": [
                {"label": "100k", "records": 100000, "path": "data/generated/flights_100k.parquet"},
                {"label": "500k", "records": 500000, "path": "data/generated/flights_500k.parquet"},
            ]
        }
    }
    manifest = {
        "datasets": [
            {
                "label": "100k",
                "actual_records": 100000,
                "path": "data/generated/flights_100k.parquet",
                "validation_status": "success",
            }
        ]
    }

    with pytest.raises(ValueError, match="Missing required benchmark input"):
        run_benchmarks.selected_benchmark_inputs(local_config, manifest, project_root=tmp_path)


def test_selected_benchmark_inputs_include_optional_when_requested(tmp_path):
    local_config = {
        "benchmark": {
            "input_sizes": [
                {"label": "100k", "records": 100000, "path": "data/generated/flights_100k.parquet"},
                {
                    "label": "14m",
                    "records": 14000000,
                    "path": "data/generated/flights_14m.parquet",
                    "optional": True,
                },
            ]
        }
    }
    manifest = {
        "datasets": [
            {
                "label": "100k",
                "actual_records": 100000,
                "path": "data/generated/flights_100k.parquet",
                "validation_status": "success",
            },
            {
                "label": "500k",
                "actual_records": 500000,
                "path": "data/generated/flights_500k.parquet",
                "validation_status": "success",
            },
            {
                "label": "1m",
                "actual_records": 1000000,
                "path": "data/generated/flights_1m.parquet",
                "validation_status": "success",
            },
            {
                "label": "14m",
                "actual_records": 14000000,
                "path": "data/generated/flights_14m.parquet",
                "validation_status": "success",
            },
        ]
    }

    selected = run_benchmarks.selected_benchmark_inputs(
        local_config,
        manifest,
        include_optional=True,
        project_root=tmp_path,
    )

    assert [item.label for item in selected] == ["100k", "14m"]


def test_selected_benchmark_inputs_carry_manifest_input_metadata(tmp_path):
    local_config = {
        "benchmark": {
            "input_sizes": [
                {
                    "label": "1m_hc8",
                    "records": 1000000,
                    "path": "data/generated/flights_1m_hc8.parquet",
                    "optional": True,
                },
            ]
        }
    }
    manifest = {
        "datasets": [
            {
                "label": "1m_hc8",
                "actual_records": 1000000,
                "path": "data/generated/flights_1m_hc8.parquet",
                "input_kind": "high_cardinality_stress",
                "synthetic_input": True,
                "source_input_label": "1m",
                "variant_factor": 8,
                "validation_status": "success",
            }
        ]
    }

    selected = run_benchmarks.selected_benchmark_inputs(
        local_config,
        manifest,
        labels=["1m_hc8"],
        project_root=tmp_path,
    )

    assert selected[0].input_kind == "high_cardinality_stress"
    assert selected[0].synthetic_input is True
    assert selected[0].source_input_label == "1m"
    assert selected[0].stress_variant_factor == 8


def test_normalize_metrics_rows_expands_successful_jobs():
    rows = run_benchmarks.normalize_metrics_rows(
        run_id="20260520T120000Z",
        repetition=1,
        technology="spark_sql",
        benchmark_input=BenchmarkInput("100k", 100000, Path("data/generated/flights_100k.parquet")),
        environment="local",
        execution_setting="local",
        timestamp_utc="2026-05-20T12:00:00+00:00",
        metrics_path=Path("outputs/spark_sql/runtime_metrics.json"),
        metrics={
            "status": "success",
            "stage": "complete",
            "input_read_seconds": 0.1,
            "jobs": [
                {
                    "job_name": "delay_by_airport_month",
                    "duration_seconds": 2.5,
                    "input_read_seconds": 0.1,
                    "plan_build_seconds": 0.2,
                    "result_collect_seconds": 2.0,
                    "full_output_write_seconds": 0.2,
                    "sample_output_write_seconds": 0.1,
                    "materialization_mode": "small_result_collect_once",
                    "output_rows": 42,
                    "status": "success",
                }
            ],
            "input_path": "data/generated/flights_100k.parquet",
        },
        returncode=0,
        process_duration_seconds=3.0,
    )

    assert rows == [
        {
            "run_id": "20260520T120000Z",
            "repetition": 1,
            "technology": "spark_sql",
            "job_name": "delay_by_airport_month",
            "input_label": "100k",
            "records": 100000,
            "input_kind": "",
            "synthetic_input": False,
            "source_input_label": "",
            "stress_variant_factor": "",
            "environment": "local",
            "execution_setting": "local",
            "duration_seconds": 2.5,
            "input_read_seconds": 0.1,
            "plan_build_seconds": 0.2,
            "result_collect_seconds": 2.0,
            "full_output_write_seconds": 0.2,
            "sample_output_write_seconds": 0.1,
            "materialization_mode": "small_result_collect_once",
            "output_rows": 42,
            "status": "success",
            "timestamp_utc": "2026-05-20T12:00:00+00:00",
            "input_path": "data/generated/flights_100k.parquet",
            "metrics_path": "outputs/spark_sql/runtime_metrics.json",
            "error": "",
            "stage": "complete",
        }
    ]


def test_normalize_metrics_rows_records_preflight_failure_without_jobs():
    rows = run_benchmarks.normalize_metrics_rows(
        run_id="20260520T120000Z",
        repetition=1,
        technology="hive",
        benchmark_input=BenchmarkInput("100k", 100000, Path("data/generated/flights_100k.parquet")),
        environment="local",
        execution_setting="local",
        timestamp_utc="2026-05-20T12:00:00+00:00",
        metrics_path=Path("outputs/hive/runtime_metrics.json"),
        metrics={
            "status": "failed",
            "stage": "preflight",
            "error": "Docker daemon is not reachable",
            "jobs": [],
            "input_path": "data/generated/flights_100k.parquet",
        },
        returncode=1,
        process_duration_seconds=0.5,
    )

    assert rows[0]["job_name"] == "__run__"
    assert rows[0]["status"] == "failed"
    assert rows[0]["duration_seconds"] == 0.5
    assert rows[0]["error"] == "Docker daemon is not reachable"
    assert rows[0]["stage"] == "preflight"


def test_normalize_metrics_rows_rejects_mismatched_input_path():
    rows = run_benchmarks.normalize_metrics_rows(
        run_id="20260520T120000123456Z",
        repetition=1,
        technology="spark_sql",
        benchmark_input=BenchmarkInput("500k", 500000, Path("data/generated/flights_500k.parquet")),
        environment="local",
        execution_setting="local",
        timestamp_utc="2026-05-20T12:00:00+00:00",
        metrics_path=Path("outputs/spark_sql/runtime_metrics.json"),
        metrics={
            "status": "success",
            "stage": "complete",
            "input_path": "data/generated/flights_100k.parquet",
            "jobs": [
                {
                    "job_name": "delay_by_airport_month",
                    "duration_seconds": 2.5,
                    "output_rows": 42,
                    "status": "success",
                }
            ],
        },
        returncode=0,
        process_duration_seconds=3.0,
    )

    assert rows[0]["job_name"] == "__run__"
    assert rows[0]["status"] == "failed"
    assert rows[0]["stage"] == "metrics_input_mismatch"


def test_stale_metrics_file_is_cleared_before_normalizing_failed_run(tmp_path):
    metrics_path = tmp_path / "runtime_metrics.json"
    metrics_path.write_text('{"input_path": "data/generated/flights_100k.parquet", "jobs": []}', encoding="utf-8")

    run_benchmarks.clear_metrics_file(metrics_path)
    metrics = run_benchmarks.read_metrics(metrics_path)
    rows = run_benchmarks.normalize_metrics_rows(
        run_id="20260520T120000123456Z",
        repetition=1,
        technology="spark_sql",
        benchmark_input=BenchmarkInput("500k", 500000, Path("data/generated/flights_500k.parquet")),
        environment="local",
        execution_setting="local",
        timestamp_utc="2026-05-20T12:00:00+00:00",
        metrics_path=metrics_path,
        metrics=metrics,
        returncode=1,
        process_duration_seconds=0.25,
        stderr="startup failed",
    )

    assert metrics is None
    assert rows[0]["job_name"] == "__run__"
    assert rows[0]["status"] == "failed"
    assert rows[0]["stage"] == "metrics_missing"
    assert rows[0]["error"] == "startup failed"


def test_invocation_logs_include_repetition_to_preserve_raw_evidence(tmp_path):
    result = run_benchmarks.subprocess.CompletedProcess(["python"], 0, stdout="ok\n", stderr="")

    run_benchmarks.write_invocation_logs(
        tmp_path,
        input_label="100k",
        technology="spark_sql",
        repetition=1,
        command=["python", "job.py"],
        result=result,
    )
    run_benchmarks.write_invocation_logs(
        tmp_path,
        input_label="100k",
        technology="spark_sql",
        repetition=2,
        command=["python", "job.py"],
        result=result,
    )

    assert (tmp_path / "100k_spark_sql_rep1.stdout.log").exists()
    assert (tmp_path / "100k_spark_sql_rep2.stdout.log").exists()


def test_microsecond_run_id_and_unique_result_path(tmp_path):
    run_id = run_benchmarks.run_id_from_timestamp(datetime(2026, 5, 20, 12, 0, 0, 123456, tzinfo=timezone.utc))
    existing = tmp_path / f"benchmark_{run_id}.csv"
    existing.write_text("already here\n", encoding="utf-8")

    unique_run_id, unique_path = run_benchmarks.unique_result_path(tmp_path, run_id)

    assert run_id == "20260520T120000123456Z"
    assert unique_run_id == "20260520T120000123456Z_1"
    assert unique_path.name == "benchmark_20260520T120000123456Z_1.csv"


def test_build_command_uses_native_spark_core_outside_windows(tmp_path):
    local_config = {"paths": {"outputs_dir": "outputs"}}
    input_path = tmp_path / "data" / "generated" / "flights_100k.parquet"
    config_path = tmp_path / "config" / "local.yaml"

    spec = run_benchmarks.build_command(
        "spark_core",
        input_path,
        local_config,
        config_path=config_path,
        project_root=tmp_path,
        python_executable="python",
        os_name="posix",
    )

    assert spec.command == [
        "python",
        "src/spark_core/run_spark_core.py",
        "--config",
        "config/local.yaml",
        "--input-path",
        "data/generated/flights_100k.parquet",
    ]
    assert spec.metrics_path == tmp_path / "outputs" / "spark_core" / "runtime_metrics.json"


def test_build_command_isolates_spark_benchmark_outputs_when_run_id_is_available(tmp_path):
    local_config = {"paths": {"outputs_dir": "outputs"}}
    input_path = tmp_path / "data" / "generated" / "flights_1m_hc8.parquet"
    config_path = tmp_path / "config" / "local.yaml"

    spec = run_benchmarks.build_command(
        "spark_sql",
        input_path,
        local_config,
        config_path=config_path,
        project_root=tmp_path,
        python_executable="python",
        run_id="20260524T120000000000Z",
        input_label="1m_hc8",
    )

    output_root = "outputs/spark_sql/.benchmark_runs/20260524T120000000000Z/1m_hc8/spark_sql"
    assert spec.command == [
        "python",
        "src/spark_sql/run_spark_sql.py",
        "--config",
        "config/local.yaml",
        "--input-path",
        "data/generated/flights_1m_hc8.parquet",
        "--output-root",
        output_root,
    ]
    assert spec.metrics_path == tmp_path / output_root / "runtime_metrics.json"


def test_build_command_uses_docker_spark_core_on_windows(tmp_path):
    local_config = {"paths": {"outputs_dir": "outputs"}}
    input_path = tmp_path / "data" / "generated" / "flights_100k.parquet"
    config_path = tmp_path / "config" / "local.yaml"

    spec = run_benchmarks.build_command(
        "spark_core",
        input_path,
        local_config,
        config_path=config_path,
        project_root=tmp_path,
        python_executable="python",
        os_name="nt",
        docker_bin="docker",
    )

    assert spec.command == [
        "docker",
        "compose",
        "run",
        "--rm",
        "spark-core",
        "python",
        "src/spark_core/run_spark_core.py",
        "--config",
        "config/local.yaml",
        "--input-path",
        "data/generated/flights_100k.parquet",
    ]


def test_build_command_uses_spark_driver_for_docker_simulation_spark_sql(tmp_path):
    docker_simulation_config = {
        "paths": {"outputs_dir": "outputs"},
        "benchmark": {
            "spark_driver_service": "spark-driver",
            "container_workspace": "/workspace",
        },
    }
    input_path = tmp_path / "data" / "generated" / "flights_100k.parquet"
    config_path = tmp_path / "config" / "docker_simulation.yaml"

    spec = run_benchmarks.build_command(
        "spark_sql",
        input_path,
        docker_simulation_config,
        config_path=config_path,
        project_root=tmp_path,
        python_executable="python",
        docker_bin="docker",
    )

    assert spec.command == [
        "docker",
        "compose",
        "exec",
        "-T",
        "spark-driver",
        "python",
        "src/spark_sql/run_spark_sql.py",
        "--config",
        "/workspace/config/docker_simulation.yaml",
        "--input-path",
        "/workspace/data/generated/flights_100k.parquet",
    ]
    assert spec.metrics_path == tmp_path / "outputs" / "spark_sql" / "runtime_metrics.json"


def test_build_command_keeps_hive_on_host_for_docker_simulation_config(tmp_path):
    docker_simulation_config = {
        "paths": {"outputs_dir": "outputs"},
        "benchmark": {
            "spark_driver_service": "spark-driver",
            "container_workspace": "/workspace",
        },
    }
    input_path = tmp_path / "data" / "generated" / "flights_100k.parquet"
    config_path = tmp_path / "config" / "docker_simulation.yaml"

    spec = run_benchmarks.build_command(
        "hive",
        input_path,
        docker_simulation_config,
        config_path=config_path,
        project_root=tmp_path,
        python_executable="python",
        docker_bin="docker",
    )

    assert spec.command == [
        "python",
        "src/hive/run_hive.py",
        "--config",
        "config/docker_simulation.yaml",
        "--input-path",
        "data/generated/flights_100k.parquet",
    ]


def test_build_command_supports_opt_in_mapreduce(tmp_path):
    local_config = {"paths": {"outputs_dir": "outputs"}}
    input_path = tmp_path / "data" / "generated" / "flights_100k.parquet"
    config_path = tmp_path / "config" / "local.yaml"

    spec = run_benchmarks.build_command(
        "mapreduce",
        input_path,
        local_config,
        config_path=config_path,
        project_root=tmp_path,
        python_executable="python",
    )

    assert spec.command == [
        "python",
        "src/mapreduce/run_mapreduce.py",
        "--config",
        "config/local.yaml",
        "--input-path",
        "data/generated/flights_100k.parquet",
    ]
    assert spec.metrics_path == tmp_path / "outputs" / "mapreduce" / "runtime_metrics.json"


def test_build_command_isolates_mapreduce_benchmark_outputs(tmp_path):
    local_config = {"paths": {"outputs_dir": "outputs"}}
    input_path = tmp_path / "data" / "generated" / "flights_100k.parquet"
    config_path = tmp_path / "config" / "local.yaml"

    spec = run_benchmarks.build_command(
        "mapreduce",
        input_path,
        local_config,
        config_path=config_path,
        project_root=tmp_path,
        python_executable="python",
        run_id="20260521T120000000000Z",
        input_label="100k",
    )

    isolated_root = "outputs/mapreduce/.benchmark_runs/20260521T120000000000Z/100k"
    assert spec.command == [
        "python",
        "src/mapreduce/run_mapreduce.py",
        "--config",
        "config/local.yaml",
        "--input-path",
        "data/generated/flights_100k.parquet",
        "--output-root",
        isolated_root,
    ]
    assert spec.metrics_path == tmp_path / isolated_root / "runtime_metrics.json"


def test_metrics_input_match_accepts_container_workspace_path():
    metrics = {"input_path": "/workspace/data/generated/flights_100k.parquet"}
    benchmark_input = BenchmarkInput("100k", 100000, Path("data/generated/flights_100k.parquet"))

    assert run_benchmarks.metrics_input_matches(metrics, benchmark_input)


def test_metrics_input_match_accepts_configured_container_workspace_path():
    metrics = {"input_path": "/repo/data/generated/flights_100k.parquet"}
    benchmark_input = BenchmarkInput("100k", 100000, Path("data/generated/flights_100k.parquet"))

    assert run_benchmarks.metrics_input_matches(metrics, benchmark_input, container_workspace="/repo")


def test_metrics_input_match_accepts_configured_file_container_workspace_path():
    metrics = {"input_path": "file:///repo/data/generated/flights_100k.parquet"}
    benchmark_input = BenchmarkInput("100k", 100000, Path("data/generated/flights_100k.parquet"))

    assert run_benchmarks.metrics_input_matches(metrics, benchmark_input, container_workspace="/repo")


def test_normalize_metrics_rows_uses_configured_container_workspace():
    rows = run_benchmarks.normalize_metrics_rows(
        run_id="20260520T120000Z",
        repetition=2,
        technology="spark_sql",
        benchmark_input=BenchmarkInput("100k", 100000, Path("data/generated/flights_100k.parquet")),
        environment="docker-simulation",
        execution_setting="docker simulation",
        timestamp_utc="2026-05-20T12:00:00+00:00",
        metrics_path=Path("outputs/spark_sql/runtime_metrics.json"),
        metrics={
            "status": "success",
            "stage": "complete",
            "input_path": "/repo/data/generated/flights_100k.parquet",
            "jobs": [
                {
                    "job_name": "delay_by_airport_month",
                    "duration_seconds": 2.5,
                    "output_rows": 42,
                    "status": "success",
                }
            ],
        },
        returncode=0,
        process_duration_seconds=3.0,
        container_workspace="/repo",
    )

    assert rows[0]["status"] == "success"
    assert rows[0]["repetition"] == 2
    assert rows[0]["job_name"] == "delay_by_airport_month"


def test_docker_simulation_results_dir_is_respected(tmp_path):
    config = {"paths": {"outputs_dir": "outputs", "results_dir": "experiments/results/docker-simulation"}}

    results_dir = run_benchmarks.resolve_project_path(config["paths"]["results_dir"], project_root=tmp_path)

    assert results_dir == tmp_path / "experiments" / "results" / "docker-simulation"


def test_docker_simulation_config_lists_required_docker_simulation_inputs():
    import yaml

    config = yaml.safe_load(Path("config/docker_simulation.yaml").read_text(encoding="utf-8"))

    assert config["environment"] == "docker-simulation"
    required = [entry["label"] for entry in config["benchmark"]["input_sizes"] if not entry.get("optional")]
    optional = [entry["label"] for entry in config["benchmark"]["input_sizes"] if entry.get("optional")]
    assert required == ["100k", "500k", "1m"]
    assert optional == ["3m", "full", "14m", "28m", "1m_hc8"]


def test_docker_simulation_large_inputs_are_requestable_without_default_matrix(tmp_path):
    import yaml

    config = yaml.safe_load(Path("config/docker_simulation.yaml").read_text(encoding="utf-8"))
    manifest = {
        "datasets": [
            {
                "label": "100k",
                "actual_records": 100000,
                "path": "data/generated/flights_100k.parquet",
                "validation_status": "success",
            },
            {
                "label": "500k",
                "actual_records": 500000,
                "path": "data/generated/flights_500k.parquet",
                "validation_status": "success",
            },
            {
                "label": "1m",
                "actual_records": 1000000,
                "path": "data/generated/flights_1m.parquet",
                "validation_status": "success",
            },
            {
                "label": "14m",
                "actual_records": 14000000,
                "path": "data/generated/flights_14m.parquet",
                "validation_status": "success",
            },
        ]
    }

    default_inputs = run_benchmarks.selected_benchmark_inputs(config, manifest, project_root=tmp_path)
    requested_inputs = run_benchmarks.selected_benchmark_inputs(
        config,
        manifest,
        labels=["14m"],
        project_root=tmp_path,
    )

    assert [item.label for item in default_inputs] == ["100k", "500k", "1m"]
    assert [item.label for item in requested_inputs] == ["14m"]


def test_makefile_uses_docker_simulation_default_matrix():
    makefile = Path("Makefile").read_text(encoding="utf-8")

    assert "--environment docker-simulation" in makefile
    assert "--input-label $(DOCKER_SIMULATION_INPUT_LABEL)" not in makefile
