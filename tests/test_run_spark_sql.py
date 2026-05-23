import pandas as pd
import pytest

from src.common.runtime import configure_pyspark_python, ensure_java_17
from src.spark_sql import run_spark_sql

ensure_java_17()
configure_pyspark_python()

from pyspark.sql import SparkSession


@pytest.fixture(scope="module")
def spark():
    session = SparkSession.builder.master("local[2]").appName("test-run-spark-sql").getOrCreate()
    try:
        yield session
    finally:
        session.stop()


def test_full_and_first_10_writers_use_same_ordered_rows(tmp_path):
    rows = pd.DataFrame(
        {
            "origin_airport": ["AAA", "BBB", "CCC"],
            "month": [1, 1, 1],
            "flight_count": [3, 2, 1],
        }
    )
    full_output = tmp_path / "full"
    sample_output = tmp_path / "first_10.csv"

    run_spark_sql.write_full_csv(rows, full_output)
    run_spark_sql.write_first_10_csv(rows.head(2), sample_output)

    full_part = full_output / "part-00000.csv"
    assert full_part.exists()
    assert full_part.read_text(encoding="utf-8").splitlines() == [
        "origin_airport,month,flight_count",
        "AAA,1,3",
        "BBB,1,2",
        "CCC,1,1",
    ]
    assert sample_output.read_text(encoding="utf-8").splitlines() == [
        "origin_airport,month,flight_count",
        "AAA,1,3",
        "BBB,1,2",
    ]


def test_compact_delay_top_three_ranking_is_deterministic(spark):
    spark.sql(
        """
        CREATE OR REPLACE TEMP VIEW flights AS
        SELECT 'AAA' AS origin_airport, 1 AS month, 20.0 AS departure_delay, 22.0 AS arrival_delay,
               0 AS cancelled, CAST(NULL AS STRING) AS cancellation_code,
               10.0 AS carrier_delay, 0.0 AS weather_delay, 0.0 AS nas_delay,
               0.0 AS security_delay, 0.0 AS late_aircraft_delay
        UNION ALL
        SELECT 'AAA', 1, 25.0, 27.0, 0, CAST(NULL AS STRING), 5.0, 0.0, 0.0, 0.0, 0.0
        UNION ALL
        SELECT 'AAA', 1, 30.0, 33.0, 0, CAST(NULL AS STRING), 0.0, 10.0, 0.0, 0.0, 0.0
        UNION ALL
        SELECT 'AAA', 1, 35.0, 39.0, 0, CAST(NULL AS STRING), 0.0, 7.0, 0.0, 0.0, 0.0
        UNION ALL
        SELECT 'AAA', 1, 40.0, 45.0, 0, CAST(NULL AS STRING), 0.0, 0.0, 20.0, 0.0, 0.0
        """
    )

    row = run_spark_sql.delay_report_query(spark).collect()[0]

    assert row.delay_range == "medium"
    assert row.top_1_cause == "delay:carrier"
    assert row.top_1_count == 2
    assert row.top_2_cause == "delay:weather"
    assert row.top_2_count == 2
    assert row.top_3_cause == "delay:nas"
    assert row.top_3_count == 1


def test_compact_all_causes_ranking_is_deterministic(spark):
    spark.sql(
        """
        CREATE OR REPLACE TEMP VIEW flights AS
        SELECT 'AAA' AS origin_airport, 1 AS month, 20.0 AS departure_delay, 22.0 AS arrival_delay,
               0 AS cancelled, CAST(NULL AS STRING) AS cancellation_code,
               10.0 AS carrier_delay, 8.0 AS weather_delay, 0.0 AS nas_delay,
               0.0 AS security_delay, 0.0 AS late_aircraft_delay
        UNION ALL
        SELECT 'AAA', 1, 25.0, 27.0, 0, CAST(NULL AS STRING), 5.0, 0.0, 4.0, 0.0, 0.0
        """
    )

    rows = run_spark_sql.delay_all_causes_query(spark).collect()

    assert [(row.cause_rank, row.cause, row.cause_count) for row in rows] == [
        (1, "delay:carrier", 2),
        (2, "delay:nas", 1),
        (3, "delay:weather", 1),
    ]
