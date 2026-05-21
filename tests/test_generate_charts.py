import csv
from datetime import datetime, timezone
from pathlib import Path

from scripts import generate_charts


BENCHMARK_COLUMNS = [
    "run_id",
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
    status: str = "success",
    technology: str = "spark_sql",
    job_name: str = "delay_by_airport_month",
    input_label: str = "100k",
    records: int = 100000,
    environment: str = "local",
) -> dict[str, object]:
    return {
        "run_id": run_id,
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
    latest = results_dir / "benchmark_latest.csv"
    unrelated = results_dir / "benchmark_notes.csv"
    write_benchmark_csv(timestamped, [])
    write_benchmark_csv(rerun, [])
    write_benchmark_csv(latest, [])
    unrelated.write_text("not a benchmark\n", encoding="utf-8")

    discovered = generate_charts.discover_benchmark_csvs([results_dir])

    assert discovered == [timestamped, rerun]


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
    assert pivot[0]["Spark SQL duration_seconds"] == 8.5
    assert pivot[0]["Spark Core duration_seconds"] == 2.25


def test_rows_per_second_records_compute_records_divided_by_duration():
    summary = [
        {
            "environment": "local",
            "input_label": "100k",
            "records": 100000,
            "job_name": "delay_by_airport_month",
            "technology": "Spark SQL",
            "duration_seconds": 4.0,
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
            "Spark SQL duration_seconds": 6.0,
            "Spark Core duration_seconds": 2.0,
            "Hive duration_seconds": 12.0,
        }
    ]

    speedups = generate_charts.speedup_records(pivot)

    assert speedups[0]["spark_sql_div_spark_core"] == 3.0
    assert speedups[0]["hive_div_spark_sql"] == 2.0
    assert speedups[0]["hive_div_spark_core"] == 6.0


def test_scalability_ratio_records_require_three_inputs_and_100k_baseline():
    summary = [
        {
            "environment": "local",
            "input_label": "100k",
            "records": 100000,
            "job_name": "delay_by_airport_month",
            "technology": "Spark SQL",
            "duration_seconds": 2.0,
        },
        {
            "environment": "local",
            "input_label": "500k",
            "records": 500000,
            "job_name": "delay_by_airport_month",
            "technology": "Spark SQL",
            "duration_seconds": 4.0,
        },
        {
            "environment": "local",
            "input_label": "1m",
            "records": 1000000,
            "job_name": "delay_by_airport_month",
            "technology": "Spark SQL",
            "duration_seconds": 5.0,
        },
        {
            "environment": "local",
            "input_label": "100k",
            "records": 100000,
            "job_name": "airline_airport_ranking",
            "technology": "Spark SQL",
            "duration_seconds": 2.0,
        },
        {
            "environment": "local",
            "input_label": "500k",
            "records": 500000,
            "job_name": "airline_airport_ranking",
            "technology": "Spark SQL",
            "duration_seconds": 4.0,
        },
    ]

    scalability = generate_charts.scalability_ratio_records(summary)

    assert len(scalability) == 3
    one_million = next(row for row in scalability if row["input_label"] == "1m")
    assert one_million["duration_vs_100k"] == 2.5
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
    calls = {"bar": 0, "plot": 0}
    original_bar = generate_charts.plt.bar
    original_plot = generate_charts.plt.plot

    def fake_bar(*args, **kwargs):
        calls["bar"] += 1
        return original_bar(*args, **kwargs)

    def fake_plot(*args, **kwargs):
        calls["plot"] += 1
        return original_plot(*args, **kwargs)

    monkeypatch.setattr(generate_charts.plt, "bar", fake_bar)
    monkeypatch.setattr(generate_charts.plt, "plot", fake_plot)
    monkeypatch.setattr(generate_charts.plt, "savefig", lambda path, **kwargs: Path(path).touch())

    figures = generate_charts.generate_execution_time_charts(
        chart_rows([("100k", 100000), ("500k", 500000)]),
        tmp_path,
    )

    assert calls["bar"] > 0
    assert calls["plot"] == 0
    assert figures == [tmp_path / "execution_time_local_delay_by_airport_month.png"]


def test_execution_time_chart_uses_lines_for_three_or_more_inputs(tmp_path, monkeypatch):
    calls = {"bar": 0, "plot": 0}
    original_bar = generate_charts.plt.bar
    original_plot = generate_charts.plt.plot

    def fake_bar(*args, **kwargs):
        calls["bar"] += 1
        return original_bar(*args, **kwargs)

    def fake_plot(*args, **kwargs):
        calls["plot"] += 1
        return original_plot(*args, **kwargs)

    monkeypatch.setattr(generate_charts.plt, "bar", fake_bar)
    monkeypatch.setattr(generate_charts.plt, "plot", fake_plot)
    monkeypatch.setattr(generate_charts.plt, "savefig", lambda path, **kwargs: Path(path).touch())

    generate_charts.generate_execution_time_charts(
        chart_rows([("100k", 100000), ("500k", 500000), ("1m", 1000000)]),
        tmp_path,
    )

    assert calls["plot"] > 0
    assert calls["bar"] == 0


def test_execution_time_chart_uses_marker_for_single_optional_technology_point(tmp_path, monkeypatch):
    calls = {"plot": 0, "scatter": 0}
    original_plot = generate_charts.plt.plot
    original_scatter = generate_charts.plt.scatter

    def fake_plot(*args, **kwargs):
        calls["plot"] += 1
        return original_plot(*args, **kwargs)

    def fake_scatter(*args, **kwargs):
        calls["scatter"] += 1
        return original_scatter(*args, **kwargs)

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

    monkeypatch.setattr(generate_charts.plt, "plot", fake_plot)
    monkeypatch.setattr(generate_charts.plt, "scatter", fake_scatter)
    monkeypatch.setattr(generate_charts.plt, "savefig", lambda path, **kwargs: Path(path).touch())

    generate_charts.generate_execution_time_charts(rows, tmp_path)

    assert calls["plot"] > 0
    assert calls["scatter"] == 1


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
