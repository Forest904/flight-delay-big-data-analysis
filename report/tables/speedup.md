| environment | input_label | records | job_name | spark_sql_div_spark_core | hive_div_spark_sql | hive_div_spark_core |
| --- | --- | --- | --- | --- | --- | --- |
| aws-emr | 100k | 100000 | airline_airport_ranking | 3.283 |  |  |
| aws-emr | 100k | 100000 | delay_by_airport_month | 8.492 |  |  |
| aws-emr | 500k | 500000 | airline_airport_ranking | 3.284 |  |  |
| aws-emr | 500k | 500000 | delay_by_airport_month | 7.282 |  |  |
| aws-emr | 1m | 1000000 | airline_airport_ranking | 3.259 |  |  |
| aws-emr | 1m | 1000000 | delay_by_airport_month | 7.865 |  |  |
| aws-emr | 3m | 3000000 | airline_airport_ranking | 2.84 |  |  |
| aws-emr | 3m | 3000000 | delay_by_airport_month | 5.947 |  |  |
| aws-emr | full | 7079081 | airline_airport_ranking | 3.888 |  |  |
| aws-emr | full | 7079081 | delay_by_airport_month | 8.083 |  |  |
| aws-emr | 14m | 14000000 | airline_airport_ranking | 4.286 |  |  |
| aws-emr | 14m | 14000000 | delay_by_airport_month | 7.513 |  |  |
| aws-emr-larger | 1m | 1000000 | airline_airport_ranking | 4.014 |  |  |
| aws-emr-larger | 1m | 1000000 | delay_by_airport_month | 8.563 |  |  |
| aws-emr-larger | full | 7079081 | airline_airport_ranking | 4.872 |  |  |
| aws-emr-larger | full | 7079081 | delay_by_airport_month | 9.886 |  |  |
| aws-emr-larger | 14m | 14000000 | airline_airport_ranking | 5.005 |  |  |
| aws-emr-larger | 14m | 14000000 | delay_by_airport_month | 10.367 |  |  |
| aws-emr-larger | 28m | 28000000 | airline_airport_ranking | 6.115 |  |  |
| aws-emr-larger | 28m | 28000000 | delay_by_airport_month | 8.265 |  |  |
| docker-simulation | 100k | 100000 | airline_airport_ranking | 2.042 | 1.442 | 2.943 |
| docker-simulation | 100k | 100000 | delay_by_airport_month | 3.407 | 1.176 | 4.005 |
| docker-simulation | 500k | 500000 | airline_airport_ranking | 2.099 | 1.446 | 3.035 |
| docker-simulation | 500k | 500000 | delay_by_airport_month | 3.529 | 1.102 | 3.887 |
| docker-simulation | 1m | 1000000 | airline_airport_ranking | 1.928 | 1.72 | 3.316 |
| docker-simulation | 1m | 1000000 | delay_by_airport_month | 3.959 | 1.155 | 4.573 |
| docker-simulation | 3m | 3000000 | airline_airport_ranking | 2.536 | 1.519 | 3.852 |
| docker-simulation | 3m | 3000000 | delay_by_airport_month | 4.391 | 1.229 | 5.398 |
| docker-simulation | full | 7079081 | airline_airport_ranking | 2.754 | 2.089 | 5.754 |
| docker-simulation | full | 7079081 | delay_by_airport_month | 4.507 | 1.539 | 6.936 |
| docker-simulation | 14m | 14000000 | airline_airport_ranking | 2.498 | 2.556 | 6.385 |
| docker-simulation | 14m | 14000000 | delay_by_airport_month | 4.712 | 1.789 | 8.431 |
| docker-simulation | 28m | 28000000 | airline_airport_ranking | 3.256 | 3.112 | 10.136 |
| docker-simulation | 28m | 28000000 | delay_by_airport_month | 5.216 | 2.45 | 12.78 |
| docker-simulation-spark-sql-baseline-m4 | 1m | 1000000 | airline_airport_ranking |  |  |  |
| docker-simulation-spark-sql-baseline-m4 | 1m | 1000000 | delay_by_airport_month |  |  |  |
| docker-simulation-spark-sql-baseline-m4 | 1m | 1000000 | delay_by_airport_month_all_causes |  |  |  |
| docker-simulation-spark-sql-baseline-m4 | full | 7079081 | airline_airport_ranking |  |  |  |
| docker-simulation-spark-sql-baseline-m4 | full | 7079081 | delay_by_airport_month |  |  |  |
| docker-simulation-spark-sql-baseline-m4 | full | 7079081 | delay_by_airport_month_all_causes |  |  |  |
| docker-simulation-spark-sql-baseline-m4 | 14m | 14000000 | airline_airport_ranking |  |  |  |
| docker-simulation-spark-sql-baseline-m4 | 14m | 14000000 | delay_by_airport_month |  |  |  |
| docker-simulation-spark-sql-baseline-m4 | 14m | 14000000 | delay_by_airport_month_all_causes |  |  |  |
| docker-simulation-spark-sql-optimized-m4 | 1m | 1000000 | airline_airport_ranking |  |  |  |
| docker-simulation-spark-sql-optimized-m4 | 1m | 1000000 | delay_by_airport_month |  |  |  |
| docker-simulation-spark-sql-optimized-m4 | 1m | 1000000 | delay_by_airport_month_all_causes |  |  |  |
| docker-simulation-spark-sql-optimized-m4 | full | 7079081 | airline_airport_ranking |  |  |  |
| docker-simulation-spark-sql-optimized-m4 | full | 7079081 | delay_by_airport_month |  |  |  |
| docker-simulation-spark-sql-optimized-m4 | full | 7079081 | delay_by_airport_month_all_causes |  |  |  |
| docker-simulation-spark-sql-optimized-m4 | 14m | 14000000 | airline_airport_ranking |  |  |  |
| docker-simulation-spark-sql-optimized-m4 | 14m | 14000000 | delay_by_airport_month |  |  |  |
| docker-simulation-spark-sql-optimized-m4 | 14m | 14000000 | delay_by_airport_month_all_causes |  |  |  |
| local | 100k | 100000 | airline_airport_ranking | 2.357 | 8.21 | 19.354 |
| local | 100k | 100000 | delay_by_airport_month | 7.953 | 2.491 | 19.81 |
| local | 500k | 500000 | airline_airport_ranking | 2.365 | 7.625 | 18.03 |
| local | 500k | 500000 | delay_by_airport_month | 7.731 | 2.421 | 18.721 |
| local | 1m | 1000000 | airline_airport_ranking | 3.142 | 6.393 | 20.088 |
| local | 1m | 1000000 | delay_by_airport_month | 10.191 | 1.84 | 18.749 |
| local | 3m | 3000000 | airline_airport_ranking | 4.261 | 4.933 | 21.019 |
| local | 3m | 3000000 | delay_by_airport_month | 11.623 | 1.915 | 22.258 |
| local | full | 7079081 | airline_airport_ranking | 4.33 | 7.066 | 30.596 |
| local | full | 7079081 | delay_by_airport_month | 10.643 | 2.693 | 28.666 |
| local | 14m | 14000000 | airline_airport_ranking | 4.186 | 8.081 | 33.83 |
| local | 14m | 14000000 | delay_by_airport_month | 9.705 | 3.464 | 33.619 |
| local | 28m | 28000000 | airline_airport_ranking | 4.063 | 19.729 | 80.154 |
| local | 28m | 28000000 | delay_by_airport_month | 8.948 | 8.493 | 75.991 |
| local-spark-sql-baseline-m4 | 1m | 1000000 | airline_airport_ranking |  |  |  |
| local-spark-sql-baseline-m4 | 1m | 1000000 | delay_by_airport_month |  |  |  |
| local-spark-sql-baseline-m4 | 1m | 1000000 | delay_by_airport_month_all_causes |  |  |  |
| local-spark-sql-baseline-m4 | full | 7079081 | airline_airport_ranking |  |  |  |
| local-spark-sql-baseline-m4 | full | 7079081 | delay_by_airport_month |  |  |  |
| local-spark-sql-baseline-m4 | full | 7079081 | delay_by_airport_month_all_causes |  |  |  |
| local-spark-sql-baseline-m4 | 14m | 14000000 | airline_airport_ranking |  |  |  |
| local-spark-sql-baseline-m4 | 14m | 14000000 | delay_by_airport_month |  |  |  |
| local-spark-sql-baseline-m4 | 14m | 14000000 | delay_by_airport_month_all_causes |  |  |  |
| local-spark-sql-optimized-m4 | 1m | 1000000 | airline_airport_ranking |  |  |  |
| local-spark-sql-optimized-m4 | 1m | 1000000 | delay_by_airport_month |  |  |  |
| local-spark-sql-optimized-m4 | 1m | 1000000 | delay_by_airport_month_all_causes |  |  |  |
| local-spark-sql-optimized-m4 | full | 7079081 | airline_airport_ranking |  |  |  |
| local-spark-sql-optimized-m4 | full | 7079081 | delay_by_airport_month |  |  |  |
| local-spark-sql-optimized-m4 | full | 7079081 | delay_by_airport_month_all_causes |  |  |  |
| local-spark-sql-optimized-m4 | 14m | 14000000 | airline_airport_ranking |  |  |  |
| local-spark-sql-optimized-m4 | 14m | 14000000 | delay_by_airport_month |  |  |  |
| local-spark-sql-optimized-m4 | 14m | 14000000 | delay_by_airport_month_all_causes |  |  |  |
