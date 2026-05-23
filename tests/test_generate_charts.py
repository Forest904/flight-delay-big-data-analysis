import csv
from datetime import datetime, timezone
from pathlib import Path

from scripts import generate_charts


BENCHMARK_COLUMNS = [
    "run_id",
    "repetition",
    "technology",
    "job_name",
    "input_label",
    "records",
    "environment",
    "execution_setting",
    "duration_seconds",
    "output_rows",
    "status",
    "timestamp_utc",
    "input_path",
    "metrics_path",
    "error",
    "stage",
]


def write_benchmark_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=BENCHMARK_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def benchmark_row(
    *,
    run_id: str,
    timestamp_utc: str,
    duration_seconds: float,
    repetition: int = 1,
    status: str = "success",
    technology: str = "spark_sql",
    job_name: str = "delay_by_airport_month",
    input_label: str = "100k",
    records: int = 100000,
    environment: str = "local",
) -> dict[str, object]:
    return {
        "run_id": run_id,
        "repetition": repetition,
        "technology": technology,
        "job_name": job_name,
        "input_label": input_label,
        "records": records,
        "environment": environment,
        "execution_setting": environment,
        "duration_seconds": duration_seconds,
        "output_rows": 12,
        "status": status,
        "timestamp_utc": timestamp_utc,
        "input_path": f"data/generated/flights_{input_label}.parquet",
        "metrics_path": f"outputs/{technology}/runtime_metrics.json",
        "error": "",
        "stage": "complete",
    }


def test_discover_benchmark_csvs_ignores_latest_copy(tmp_path):
    results_dir = tmp_path / "results"
    timestamped = results_dir / "benchmark_20260520T120000123456Z.csv"
    rerun = results_dir / "benchmark_20260520T120000123456Z_1.csv"
    named_run = results_dir / "benchmark_m4-emr-final-2.csv"
    latest = results_dir / "benchmark_latest.csv"
    unrelated = results_dir / "benchmark_notes.csv"
    write_benchmark_csv(timestamped, [])
    write_benchmark_csv(rerun, [])
    write_benchmark_csv(named_run, [])
    write_benchmark_csv(latest, [])
    unrelated.write_text("not a benchmark\n", encoding="utf-8")

    discovered = generate_charts.discover_benchmark_csvs([results_dir])

    assert discovered == [timestamped, rerun, named_run]


def test_latest_successful_rows_keeps_newest_success_and_excludes_failed(tmp_path):
    older = tmp_path / "benchmark_20260520T120000000000Z.csv"
    newer = tmp_path / "benchmark_20260520T130000000000Z.csv"
    failed = tmp_path / "benchmark_20260520T140000000000Z.csv"
    write_benchmark_csv(
        older,
        [
            benchmark_row(
                run_id="older",
                timestamp_utc="2026-05-20T12:00:00+00:00",
                duration_seconds=8.5,
            )
        ],
    )
    write_benchmark_csv(
        newer,
        [
            benchmark_row(
                run_id="newer",
                timestamp_utc="2026-05-20T13:00:00+00:00",
                duration_seconds=7.5,
            )
        ],
    )
    write_benchmark_csv(
        failed,
        [
            benchmark_row(
                run_id="failed",
                timestamp_utc="2026-05-20T14:00:00+00:00",
                duration_seconds=1.0,
                status="failed",
            )
        ],
    )

    rows = generate_charts.read_successful_benchmark_rows([older, newer, failed])
    latest = generate_charts.latest_successful_rows(rows)

    assert len(latest) == 1
    assert latest[0]["run_id"] == "newer"
    assert latest[0]["duration_seconds"] == "7.5"
    assert latest[0]["repetition"] == "1"


def test_read_benchmark_rows_defaults_missing_repetition_to_one(tmp_path):
    csv_path = tmp_path / "benchmark_20260520T120000000000Z.csv"
    row = benchmark_row(
        run_id="run",
        timestamp_utc="2026-05-20T12:00:00+00:00",
        duration_seconds=8.5,
    )
    row.pop("repetition")
    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=[column for column in BENCHMARK_COLUMNS if column != "repetition"])
        writer.writeheader()
        writer.writerow(row)

    rows = generate_charts.read_benchmark_rows([csv_path])

    assert rows[0]["repetition"] == "1"


def test_read_benchmark_rows_accepts_utf8_sig_header(tmp_path):
    csv_path = tmp_path / "benchmark_20260520T120000000000Z.csv"
    row = benchmark_row(
        run_id="run",
        timestamp_utc="2026-05-20T12:00:00+00:00",
        duration_seconds=8.5,
    )
    content = ",".join(BENCHMARK_COLUMNS) + "\n" + ",".join(str(row[column]) for column in BENCHMARK_COLUMNS) + "\n"
    csv_path.write_bytes(("\ufeff" + content).encode("utf-8"))

    assert generate_charts.benchmark_csv_schema_errors(csv_path) == []
    rows = generate_charts.read_benchmark_rows([csv_path])

    assert rows[0]["run_id"] == "run"


def test_read_benchmark_rows_keeps_docker_simulation_label(tmp_path):
    csv_path = tmp_path / "benchmark_20260520T120000000000Z.csv"
    write_benchmark_csv(
        csv_path,
        [
            benchmark_row(
                run_id="run",
                timestamp_utc="2026-05-20T12:00:00+00:00",
                duration_seconds=8.5,
                environment="docker-simulation",
            )
        ],
    )

    rows = generate_charts.read_benchmark_rows([csv_path])

    assert rows[0]["environment"] == "docker-simulation"


def test_default_chart_discovery_includes_aws_emr_results_dir():
    assert Path("experiments/results/aws-emr") in [
        path.relative_to(generate_charts.PROJECT_ROOT) for path in generate_charts.DEFAULT_RESULTS_DIRS
    ]
    assert Path("experiments/results/aws-emr-larger") in [
        path.relative_to(generate_charts.PROJECT_ROOT) for path in generate_charts.DEFAULT_RESULTS_DIRS
    ]
    assert generate_charts.ENVIRONMENT_LABELS["aws-emr"] == "AWS EMR"
    assert generate_charts.ENVIRONMENT_LABELS["aws-emr-larger"] == "AWS EMR larger cluster"
    assert "14m" in [label for label, _ in generate_charts.EXPECTED_INPUTS_BY_ENVIRONMENT["aws-emr"]]
    assert generate_charts.EXPECTED_TECHNOLOGIES_BY_ENVIRONMENT["aws-emr"] == ("spark_sql", "spark_core")
    assert generate_charts.EXPECTED_INPUTS_BY_ENVIRONMENT["aws-emr-larger"] == (
        ("1m", 1_000_000),
        ("full", 7_079_081),
        ("14m", 14_000_000),
        ("28m", 28_000_000),
    )
    assert generate_charts.EXPECTED_INPUTS_BY_ENVIRONMENT["docker-simulation"] == (
        ("100k", 100_000),
        ("500k", 500_000),
        ("1m", 1_000_000),
        ("3m", 3_000_000),
        ("full", 7_079_081),
        ("14m", 14_000_000),
        ("28m", 28_000_000),
    )


def test_input_tick_label_is_compact_for_pdf_readability():
    assert generate_charts.input_tick_label("100k", 100_000) == "100k"
    assert "rows" not in generate_charts.input_tick_label("full", 7_079_081)


def test_benchmark_pivot_contains_available_technology_duration_columns():
    rows = [
        benchmark_row(
            run_id="run",
            timestamp_utc=datetime(2026, 5, 20, tzinfo=timezone.utc).isoformat(),
            duration_seconds=8.5,
            technology="spark_sql",
        ),
        benchmark_row(
            run_id="run",
            timestamp_utc=datetime(2026, 5, 20, tzinfo=timezone.utc).isoformat(),
            duration_seconds=2.25,
            technology="spark_core",
        ),
    ]
    for row in rows:
        row["_timestamp"] = generate_charts.parse_timestamp(row["timestamp_utc"])

    summary = generate_charts.benchmark_summary_records(rows)
    pivot = generate_charts.benchmark_pivot_records(summary)

    assert len(pivot) == 1
    assert pivot[0]["Spark SQL median_duration_seconds"] == 8.5
    assert pivot[0]["Spark Core median_duration_seconds"] == 2.25


def test_cluster_size_comparison_keeps_emr_profiles_separate_and_marks_docker_full_na():
    summary = [
        {
            "environment": "local",
            "input_label": "full",
            "records": 7079081,
            "job_name": "delay_by_airport_month",
            "technology": "Spark SQL",
            "median_duration_seconds": 8.0,
            "run_id": "local-run",
        },
        {
            "environment": "aws-emr",
            "input_label": "full",
            "records": 7079081,
            "job_name": "delay_by_airport_month",
            "technology": "Spark SQL",
            "median_duration_seconds": 16.0,
            "run_id": "m4-emr-final-2",
        },
        {
            "environment": "aws-emr-larger",
            "input_label": "full",
            "records": 7079081,
            "job_name": "delay_by_airport_month",
            "technology": "Spark SQL",
            "median_duration_seconds": 12.0,
            "run_id": "m5-emr-3core-1m-full",
        },
    ]

    comparison = generate_charts.cluster_size_comparison_records(summary)
    full_sql = next(
        row
        for row in comparison
        if row["input_label"] == "full"
        and row["job_name"] == "delay_by_airport_month"
        and row["technology"] == "Spark SQL"
    )

    assert full_sql["docker_simulation_median_duration_seconds"] == "N/A"
    assert full_sql["emr_baseline_run_id"] == "m4-emr-final-2"
    assert full_sql["emr_larger_run_id"] == "m5-emr-3core-1m-full"
    assert full_sql["emr_larger_vs_baseline_speedup"] == 16.0 / 12.0
    assert "Docker standalone simulation full input was not run" in full_sql["notes"]


def test_benchmark_summary_records_compute_aggregate_statistics():
    timestamp = datetime(2026, 5, 20, tzinfo=timezone.utc).isoformat()
    rows = [
        benchmark_row(run_id="run", timestamp_utc=timestamp, duration_seconds=2.0, repetition=1),
        benchmark_row(run_id="run", timestamp_utc=timestamp, duration_seconds=4.0, repetition=2),
        benchmark_row(run_id="run", timestamp_utc=timestamp, duration_seconds=9.0, repetition=3),
    ]

    summary = generate_charts.benchmark_summary_records(rows)

    assert summary[0]["runs"] == 3
    assert summary[0]["median_duration_seconds"] == 4.0
    assert summary[0]["mean_duration_seconds"] == 5.0
    assert summary[0]["min_duration_seconds"] == 2.0
    assert summary[0]["max_duration_seconds"] == 9.0
    assert round(summary[0]["stddev_duration_seconds"], 6) == 3.605551


def test_rows_per_second_records_compute_records_divided_by_duration():
    summary = [
        {
            "environment": "local",
            "input_label": "100k",
            "records": 100000,
            "job_name": "delay_by_airport_month",
            "technology": "Spark SQL",
            "median_duration_seconds": 4.0,
        }
    ]

    rows_per_second = generate_charts.rows_per_second_records(summary)

    assert rows_per_second[0]["rows_per_second"] == 25000.0


def test_speedup_records_compute_requested_duration_ratios():
    pivot = [
        {
            "environment": "local",
            "input_label": "100k",
            "records": 100000,
            "job_name": "delay_by_airport_month",
            "Spark SQL median_duration_seconds": 6.0,
            "Spark Core median_duration_seconds": 2.0,
            "Hive median_duration_seconds": 12.0,
        }
    ]

    speedups = generate_charts.speedup_records(pivot)

    assert speedups[0]["spark_sql_div_spark_core"] == 3.0
    assert speedups[0]["hive_div_spark_sql"] == 2.0
    assert speedups[0]["hive_div_spark_core"] == 6.0


def test_spark_sql_optimization_before_after_pairs_only_m4_labels():
    summary = [
        {
            "environment": "local-spark-sql-baseline-m4",
            "input_label": "1m",
            "records": 1000000,
            "job_name": "delay_by_airport_month",
            "technology": "Spark SQL",
            "runs": 3,
            "median_duration_seconds": 12.0,
            "run_id": "baseline",
        },
        {
            "environment": "local-spark-sql-optimized-m4",
            "input_label": "1m",
            "records": 1000000,
            "job_name": "delay_by_airport_month",
            "technology": "Spark SQL",
            "runs": 3,
            "median_duration_seconds": 8.0,
            "run_id": "optimized",
        },
        {
            "environment": "local",
            "input_label": "1m",
            "records": 1000000,
            "job_name": "delay_by_airport_month",
            "technology": "Spark SQL",
            "runs": 3,
            "median_duration_seconds": 6.0,
            "run_id": "main-baseline",
        },
        {
            "environment": "docker-simulation-spark-sql-baseline-m4",
            "input_label": "full",
            "records": 7079081,
            "job_name": "airline_airport_ranking",
            "technology": "Spark SQL",
            "runs": 3,
            "median_duration_seconds": 10.0,
            "run_id": "docker-baseline",
        },
    ]

    records = generate_charts.spark_sql_optimization_before_after_records(summary)

    assert records == [
        {
            "environment_family": "local",
            "input_label": "1m",
            "records": 1000000,
            "job_name": "delay_by_airport_month",
            "baseline_median_duration_seconds": 12.0,
            "optimized_median_duration_seconds": 8.0,
            "optimized_speedup": 1.5,
            "baseline_runs": 3,
            "optimized_runs": 3,
            "baseline_run_id": "baseline",
            "optimized_run_id": "optimized",
        }
    ]


def test_scalability_ratio_records_require_three_inputs_and_100k_baseline():
    summary = [
        {
            "environment": "local",
            "input_label": "100k",
            "records": 100000,
            "job_name": "delay_by_airport_month",
            "technology": "Spark SQL",
            "median_duration_seconds": 2.0,
        },
        {
            "environment": "local",
            "input_label": "500k",
            "records": 500000,
            "job_name": "delay_by_airport_month",
            "technology": "Spark SQL",
            "median_duration_seconds": 4.0,
        },
        {
            "environment": "local",
            "input_label": "1m",
            "records": 1000000,
            "job_name": "delay_by_airport_month",
            "technology": "Spark SQL",
            "median_duration_seconds": 5.0,
        },
        {
            "environment": "local",
            "input_label": "100k",
            "records": 100000,
            "job_name": "airline_airport_ranking",
            "technology": "Spark SQL",
            "median_duration_seconds": 2.0,
        },
        {
            "environment": "local",
            "input_label": "500k",
            "records": 500000,
            "job_name": "airline_airport_ranking",
            "technology": "Spark SQL",
            "median_duration_seconds": 4.0,
        },
    ]

    scalability = generate_charts.scalability_ratio_records(summary)

    assert len(scalability) == 3
    one_million = next(row for row in scalability if row["input_label"] == "1m")
    assert one_million["median_duration_vs_100k"] == 2.5
    assert one_million["records_vs_100k"] == 10.0
    assert one_million["throughput_vs_100k"] == 4.0


def chart_rows(input_sizes: list[tuple[str, int]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    timestamp = datetime(2026, 5, 20, tzinfo=timezone.utc).isoformat()
    for input_label, records in input_sizes:
        for technology, duration in (
            ("spark_sql", 6.0),
            ("spark_core", 2.0),
            ("hive", 12.0),
        ):
            rows.append(
                benchmark_row(
                    run_id="run",
                    timestamp_utc=timestamp,
                    duration_seconds=duration,
                    technology=technology,
                    input_label=input_label,
                    records=records,
                )
            )
    return rows


def test_execution_time_chart_uses_grouped_bars_for_one_or_two_inputs(tmp_path, monkeypatch):
    calls = {"bar": 0, "errorbar": 0}
    original_bar = generate_charts.plt.bar
    original_errorbar = generate_charts.plt.errorbar

    def fake_bar(*args, **kwargs):
        calls["bar"] += 1
        return original_bar(*args, **kwargs)

    def fake_errorbar(*args, **kwargs):
        calls["errorbar"] += 1
        return original_errorbar(*args, **kwargs)

    monkeypatch.setattr(generate_charts.plt, "bar", fake_bar)
    monkeypatch.setattr(generate_charts.plt, "errorbar", fake_errorbar)
    monkeypatch.setattr(generate_charts.plt, "savefig", lambda path, **kwargs: Path(path).touch())

    figures = generate_charts.generate_execution_time_charts(
        chart_rows([("100k", 100000), ("500k", 500000)]),
        tmp_path,
    )

    assert calls["bar"] > 0
    assert calls["errorbar"] == 0
    assert figures == [tmp_path / "execution_time_local_delay_by_airport_month.png"]


def test_execution_time_chart_uses_lines_for_three_or_more_inputs(tmp_path, monkeypatch):
    calls = {"bar": 0, "errorbar": 0}
    original_bar = generate_charts.plt.bar
    original_errorbar = generate_charts.plt.errorbar

    def fake_bar(*args, **kwargs):
        calls["bar"] += 1
        return original_bar(*args, **kwargs)

    def fake_errorbar(*args, **kwargs):
        calls["errorbar"] += 1
        return original_errorbar(*args, **kwargs)

    monkeypatch.setattr(generate_charts.plt, "bar", fake_bar)
    monkeypatch.setattr(generate_charts.plt, "errorbar", fake_errorbar)
    monkeypatch.setattr(generate_charts.plt, "savefig", lambda path, **kwargs: Path(path).touch())

    generate_charts.generate_execution_time_charts(
        chart_rows([("100k", 100000), ("500k", 500000), ("1m", 1000000)]),
        tmp_path,
    )

    assert calls["errorbar"] > 0
    assert calls["bar"] == 0


def test_execution_time_chart_uses_errorbar_marker_for_single_optional_technology_point(tmp_path, monkeypatch):
    calls = {"errorbar": 0}
    original_errorbar = generate_charts.plt.errorbar

    def fake_errorbar(*args, **kwargs):
        calls["errorbar"] += 1
        return original_errorbar(*args, **kwargs)

    rows = chart_rows([("100k", 100000), ("500k", 500000), ("1m", 1000000)])
    rows.append(
        benchmark_row(
            run_id="run",
            timestamp_utc=datetime(2026, 5, 20, tzinfo=timezone.utc).isoformat(),
            duration_seconds=11.0,
            technology="mapreduce",
            input_label="100k",
            records=100000,
        )
    )

    monkeypatch.setattr(generate_charts.plt, "errorbar", fake_errorbar)
    monkeypatch.setattr(generate_charts.plt, "savefig", lambda path, **kwargs: Path(path).touch())

    generate_charts.generate_execution_time_charts(rows, tmp_path)

    assert calls["errorbar"] == 4


def test_docker_simulation_rows_generate_docker_simulation_figure_name(tmp_path):
    csv_path = tmp_path / "benchmark_20260520T120000000000Z.csv"
    write_benchmark_csv(
        csv_path,
        [
            benchmark_row(
                run_id="run",
                timestamp_utc="2026-05-20T12:00:00+00:00",
                duration_seconds=8.5,
                environment="docker-simulation",
            )
        ],
    )
    rows = generate_charts.read_successful_benchmark_rows([csv_path])
    latest = generate_charts.latest_successful_rows(rows)

    figures = generate_charts.generate_execution_time_charts(latest, tmp_path)

    assert figures == [tmp_path / "execution_time_docker-simulation_delay_by_airport_month.png"]


def test_benchmark_status_records_include_success_failure_and_not_run():
    success = benchmark_row(
        run_id="success",
        timestamp_utc=datetime(2026, 5, 20, 12, 0, tzinfo=timezone.utc).isoformat(),
        duration_seconds=8.5,
        status="success",
        technology="spark_sql",
        job_name="delay_by_airport_month",
        input_label="100k",
        records=100000,
        environment="local",
    )
    failure = benchmark_row(
        run_id="failed",
        timestamp_utc=datetime(2026, 5, 20, 13, 0, tzinfo=timezone.utc).isoformat(),
        duration_seconds=0.5,
        status="failed",
        technology="hive",
        job_name="__run__",
        input_label="full",
        records=7079081,
        environment="local",
    )
    failure["stage"] = "preflight"
    failure["error"] = "Hive full run exceeded practical limit"
    for row in (success, failure):
        row["_timestamp"] = generate_charts.parse_timestamp(row["timestamp_utc"])
        row["_source_file"] = "benchmark_20260520T120000000000Z.csv"

    status = generate_charts.benchmark_status_records([success, failure])
    by_key = {
        (row["environment"], row["input_label"], row["job_name"], row["technology"]): row
        for row in status
    }

    assert by_key[("local", "100k", "delay_by_airport_month", "Spark SQL")]["status"] == "success"
    assert by_key[("local", "full", "delay_by_airport_month", "Hive")]["status"] == "failed"
    assert "exceeded practical limit" in by_key[("local", "full", "delay_by_airport_month", "Hive")]["reason"]
    assert by_key[("docker-simulation", "500k", "airline_airport_ranking", "Spark SQL")]["status"] == "not_run"
    assert by_key[("docker-simulation", "28m", "delay_by_airport_month", "Hive")]["status"] == "not_run"


def test_first_10_csv_inputs_are_written_as_report_tables(tmp_path):
    outputs_dir = tmp_path / "outputs"
    sample_path = outputs_dir / "spark_sql" / "delay_by_airport_month" / "first_10.csv"
    sample_path.parent.mkdir(parents=True)
    outputs_dir.joinpath("spark_core").mkdir()
    outputs_dir.joinpath("hive").mkdir()
    sample_path.write_text("origin_airport,month,flight_count\nABE,1,42\nABQ,2,10\n", encoding="utf-8")
    tables_dir = tmp_path / "report" / "tables"

    tables, warnings = generate_charts.copy_first_10_tables(outputs_dir, tables_dir)

    assert warnings == []
    assert tables_dir.joinpath("first_10_spark_sql_delay_by_airport_month.csv").read_text(
        encoding="utf-8"
    ).startswith("origin_airport,month,flight_count")
    assert "| origin_airport | month | flight_count |" in tables_dir.joinpath(
        "first_10_spark_sql_delay_by_airport_month.md"
    ).read_text(encoding="utf-8")
    assert len(tables) == 2


def test_benchmark_csv_schema_validation_rejects_unexpected_columns(tmp_path):
    csv_path = tmp_path / "benchmark_bad.csv"
    row = benchmark_row(
        run_id="run",
        timestamp_utc="2026-05-20T12:00:00+00:00",
        duration_seconds=8.5,
    )
    row["extra"] = "not part of the schema"
    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=[*BENCHMARK_COLUMNS, "extra"])
        writer.writeheader()
        writer.writerow(row)

    assert generate_charts.benchmark_csv_schema_errors(csv_path) == ["unexpected columns: extra"]
    assert generate_charts.read_benchmark_rows([csv_path]) == []


def test_aws_audit_records_are_flattened_for_report_tables(tmp_path):
    results_dir = tmp_path / "aws-emr"
    results_dir.mkdir()
    manifest_path = results_dir / "run_manifest_m4-hardened-smoke.json"
    manifest_path.write_text(
        """
{
  "run_id": "m4-hardened-smoke",
  "run_kind": "smoke",
  "status": "success",
  "canonical_run_id": "m4-emr-final-2",
  "is_canonical_full_run": false,
  "git": {"commit": "abc", "dirty": true},
  "aws": {"bucket": "bucket", "region": "us-east-1", "emr_release": "emr-7.13.0", "cluster_id": "j-123", "instance_type": "m5.xlarge", "node_count": 3},
  "artifacts": {"source_bundle_sha256": "source", "runtime_config_sha256": "runtime", "config_sha256": "config"},
  "python_dependencies": ["pandas==3.0.3", "pyarrow==24.0.0"]
}
""",
        encoding="utf-8",
    )

    records = generate_charts.read_aws_run_manifest_records([results_dir])

    assert records[0]["run_id"] == "m4-hardened-smoke"
    assert records[0]["canonical_run_id"] == "m4-emr-final-2"
    assert records[0]["git_dirty"] is True
    assert "pandas==3.0.3" in records[0]["dependencies"]


def test_aws_first_10_downloaded_outputs_are_written_as_report_tables(tmp_path):
    results_dir = tmp_path / "aws-emr"
    sample_path = (
        results_dir
        / "downloaded"
        / "m4-hardened-smoke"
        / "outputs"
        / "100k"
        / "spark_sql"
        / "rep1"
        / "spark_sql"
        / "delay_by_airport_month"
        / "first_10.csv"
    )
    sample_path.parent.mkdir(parents=True)
    sample_path.write_text("origin_airport,month,flight_count\nABE,1,42\n", encoding="utf-8")
    tables_dir = tmp_path / "tables"

    tables, warnings = generate_charts.copy_aws_first_10_tables(
        [results_dir],
        tables_dir,
        {"m4-hardened-smoke"},
    )

    assert warnings == []
    assert len(tables) == 2
    assert tables_dir.joinpath(
        "first_10_aws-emr_m4-hardened-smoke_100k_spark_sql_rep1_delay_by_airport_month.csv"
    ).exists()
