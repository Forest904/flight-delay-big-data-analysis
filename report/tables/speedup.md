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
| aws-emr-larger | 100k | 100000 | airline_airport_ranking | 2.073 |  |  |
| aws-emr-larger | 100k | 100000 | delay_by_airport_month | 5.195 |  |  |
| aws-emr-larger | 100k | 100000 | delay_by_airport_month_all_causes | 3.642 |  |  |
| aws-emr-larger | 500k | 500000 | airline_airport_ranking | 2.306 |  |  |
| aws-emr-larger | 500k | 500000 | delay_by_airport_month | 5.557 |  |  |
| aws-emr-larger | 500k | 500000 | delay_by_airport_month_all_causes | 5.073 |  |  |
| aws-emr-larger | 1m | 1000000 | airline_airport_ranking | 2.683 |  |  |
| aws-emr-larger | 1m | 1000000 | delay_by_airport_month | 6.594 |  |  |
| aws-emr-larger | 1m | 1000000 | delay_by_airport_month_all_causes | 5.268 |  |  |
| aws-emr-larger | 3m | 3000000 | airline_airport_ranking | 2.88 |  |  |
| aws-emr-larger | 3m | 3000000 | delay_by_airport_month | 6.43 |  |  |
| aws-emr-larger | 3m | 3000000 | delay_by_airport_month_all_causes | 4.993 |  |  |
| aws-emr-larger | full | 7079081 | airline_airport_ranking | 3.027 |  |  |
| aws-emr-larger | full | 7079081 | delay_by_airport_month | 7.207 |  |  |
| aws-emr-larger | full | 7079081 | delay_by_airport_month_all_causes | 5.675 |  |  |
| aws-emr-larger | 14m | 14000000 | airline_airport_ranking | 3.676 |  |  |
| aws-emr-larger | 14m | 14000000 | delay_by_airport_month | 10.078 |  |  |
| aws-emr-larger | 14m | 14000000 | delay_by_airport_month_all_causes | 8.113 |  |  |
| aws-emr-larger | 28m | 28000000 | airline_airport_ranking | 5.593 |  |  |
| aws-emr-larger | 28m | 28000000 | delay_by_airport_month | 11.907 |  |  |
| aws-emr-larger | 28m | 28000000 | delay_by_airport_month_all_causes | 13.858 |  |  |
| docker-simulation | 100k | 100000 | airline_airport_ranking | 0.549 | 7.781 | 4.276 |
| docker-simulation | 100k | 100000 | delay_by_airport_month | 2.445 | 2.013 | 4.922 |
| docker-simulation | 100k | 100000 | delay_by_airport_month_all_causes | 1.852 | 2.539 | 4.702 |
| docker-simulation | 500k | 500000 | airline_airport_ranking | 0.508 | 8.463 | 4.301 |
| docker-simulation | 500k | 500000 | delay_by_airport_month | 2.216 | 2.482 | 5.501 |
| docker-simulation | 500k | 500000 | delay_by_airport_month_all_causes | 1.903 | 2.246 | 4.275 |
| docker-simulation | 1m | 1000000 | airline_airport_ranking | 0.513 | 8.196 | 4.208 |
| docker-simulation | 1m | 1000000 | delay_by_airport_month | 2.366 | 2.411 | 5.705 |
| docker-simulation | 1m | 1000000 | delay_by_airport_month_all_causes | 1.918 | 2.546 | 4.884 |
| docker-simulation | 1m_hc8 | 1000000 | airline_airport_ranking | 0.598 |  |  |
| docker-simulation | 1m_hc8 | 1000000 | delay_by_airport_month | 2.074 |  |  |
| docker-simulation | 1m_hc8 | 1000000 | delay_by_airport_month_all_causes | 1.551 |  |  |
| docker-simulation | 3m | 3000000 | airline_airport_ranking | 0.624 | 6.941 | 4.328 |
| docker-simulation | 3m | 3000000 | delay_by_airport_month | 2.603 | 3.142 | 8.179 |
| docker-simulation | 3m | 3000000 | delay_by_airport_month_all_causes | 1.867 | 3.057 | 5.709 |
| docker-simulation | full | 7079081 | airline_airport_ranking | 0.864 | 7.065 | 6.106 |
| docker-simulation | full | 7079081 | delay_by_airport_month | 2.929 | 4.249 | 12.448 |
| docker-simulation | full | 7079081 | delay_by_airport_month_all_causes | 4.271 | 3.143 | 13.424 |
| docker-simulation | 14m | 14000000 | airline_airport_ranking | 0.944 | 7.266 | 6.862 |
| docker-simulation | 14m | 14000000 | delay_by_airport_month | 3.732 | 5.556 | 20.735 |
| docker-simulation | 14m | 14000000 | delay_by_airport_month_all_causes | 5.086 | 4.353 | 22.139 |
| docker-simulation | 28m | 28000000 | airline_airport_ranking | 1.462 | 7.374 | 10.784 |
| docker-simulation | 28m | 28000000 | delay_by_airport_month | 4.812 | 7.481 | 35.996 |
| docker-simulation | 28m | 28000000 | delay_by_airport_month_all_causes | 7.829 | 4.629 | 36.241 |
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
| local | 100k | 100000 | airline_airport_ranking | 1.5 | 10.053 | 15.081 |
| local | 100k | 100000 | delay_by_airport_month | 5.083 | 2.617 | 13.303 |
| local | 100k | 100000 | delay_by_airport_month_all_causes | 3.046 | 4.817 | 14.672 |
| local | 500k | 500000 | airline_airport_ranking | 1.758 | 7.986 | 14.04 |
| local | 500k | 500000 | delay_by_airport_month | 5.833 | 2.421 | 14.124 |
| local | 500k | 500000 | delay_by_airport_month_all_causes | 3.547 | 4.05 | 14.367 |
| local | 1m | 1000000 | airline_airport_ranking | 1.714 | 8.313 | 14.245 |
| local | 1m | 1000000 | delay_by_airport_month | 6.471 | 2.519 | 16.3 |
| local | 1m | 1000000 | delay_by_airport_month_all_causes | 4.238 | 3.602 | 15.265 |
| local | 1m_hc8 | 1000000 | airline_airport_ranking | 1.846 |  |  |
| local | 1m_hc8 | 1000000 | delay_by_airport_month | 4.58 |  |  |
| local | 1m_hc8 | 1000000 | delay_by_airport_month_all_causes | 3.213 |  |  |
| local | 3m | 3000000 | airline_airport_ranking | 2.614 | 5.512 | 14.409 |
| local | 3m | 3000000 | delay_by_airport_month | 7.033 | 2.922 | 20.551 |
| local | 3m | 3000000 | delay_by_airport_month_all_causes | 4.993 | 3.779 | 18.868 |
| local | full | 7079081 | airline_airport_ranking | 3.095 | 5.859 | 18.133 |
| local | full | 7079081 | delay_by_airport_month | 8.353 | 4.068 | 33.977 |
| local | full | 7079081 | delay_by_airport_month_all_causes | 8.388 | 3.23 | 27.093 |
| local | 14m | 14000000 | airline_airport_ranking | 3.237 | 7.271 | 23.535 |
| local | 14m | 14000000 | delay_by_airport_month | 8.145 | 6.264 | 51.018 |
| local | 14m | 14000000 | delay_by_airport_month_all_causes | 7.685 | 5.871 | 45.119 |
| local | 28m | 28000000 | airline_airport_ranking | 3.209 | 11.252 | 36.11 |
| local | 28m | 28000000 | delay_by_airport_month | 9.074 | 10.342 | 93.843 |
| local | 28m | 28000000 | delay_by_airport_month_all_causes | 9.811 | 8.374 | 82.155 |
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
