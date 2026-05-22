from src.common.prepared_data import prepared_parquet_read_paths
from src.spark_sql import run_spark_sql


def test_prepared_parquet_read_paths_preserves_s3_uri():
    uri = "s3://bucket/flight-delay/data/generated/flights_100k.parquet/"

    assert prepared_parquet_read_paths(uri) == [uri]


def test_spark_sql_output_root_can_be_s3():
    config = {"paths": {"outputs_dir": "s3://bucket/flight-delay/results/runs/run/outputs"}}

    assert run_spark_sql.spark_sql_output_root(config) == "s3://bucket/flight-delay/results/runs/run/outputs/spark_sql"


def test_spark_sql_parse_args_accepts_s3_input_without_pathlib_mangling():
    args = run_spark_sql.parse_args(["--input-path", "s3://bucket/key/", "--output-root", "s3://bucket/output"])

    assert args.input_path == "s3://bucket/key/"
    assert args.output_root == "s3://bucket/output"
