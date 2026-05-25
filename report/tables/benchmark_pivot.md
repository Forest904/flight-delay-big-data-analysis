| environment | input_label | records | job_name | Spark SQL median_duration_seconds | Spark Core median_duration_seconds | Hive median_duration_seconds | MapReduce median_duration_seconds |
| --- | --- | --- | --- | --- | --- | --- | --- |
| aws-emr | 100k | 100000 | airline_airport_ranking | 3.984 | 1.213 |  |  |
| aws-emr | 100k | 100000 | delay_by_airport_month | 15.832 | 1.864 |  |  |
| aws-emr | 500k | 500000 | airline_airport_ranking | 3.898 | 1.187 |  |  |
| aws-emr | 500k | 500000 | delay_by_airport_month | 14.054 | 1.93 |  |  |
| aws-emr | 1m | 1000000 | airline_airport_ranking | 4.052 | 1.243 |  |  |
| aws-emr | 1m | 1000000 | delay_by_airport_month | 15.126 | 1.923 |  |  |
| aws-emr | 3m | 3000000 | airline_airport_ranking | 4.08 | 1.437 |  |  |
| aws-emr | 3m | 3000000 | delay_by_airport_month | 14.704 | 2.473 |  |  |
| aws-emr | full | 7079081 | airline_airport_ranking | 4.302 | 1.106 |  |  |
| aws-emr | full | 7079081 | delay_by_airport_month | 15.505 | 1.918 |  |  |
| aws-emr | 14m | 14000000 | airline_airport_ranking | 5.359 | 1.25 |  |  |
| aws-emr | 14m | 14000000 | delay_by_airport_month | 17.02 | 2.265 |  |  |
| aws-emr-larger | 100k | 100000 | airline_airport_ranking | 1.914 | 0.923 |  |  |
| aws-emr-larger | 100k | 100000 | delay_by_airport_month | 10.837 | 2.086 |  |  |
| aws-emr-larger | 100k | 100000 | delay_by_airport_month_all_causes | 3.911 | 1.074 |  |  |
| aws-emr-larger | 500k | 500000 | airline_airport_ranking | 1.965 | 0.852 |  |  |
| aws-emr-larger | 500k | 500000 | delay_by_airport_month | 10.89 | 1.96 |  |  |
| aws-emr-larger | 500k | 500000 | delay_by_airport_month_all_causes | 5.602 | 1.104 |  |  |
| aws-emr-larger | 1m | 1000000 | airline_airport_ranking | 2.262 | 0.843 |  |  |
| aws-emr-larger | 1m | 1000000 | delay_by_airport_month | 11.726 | 1.778 |  |  |
| aws-emr-larger | 1m | 1000000 | delay_by_airport_month_all_causes | 6.028 | 1.144 |  |  |
| aws-emr-larger | 3m | 3000000 | airline_airport_ranking | 2.541 | 0.882 |  |  |
| aws-emr-larger | 3m | 3000000 | delay_by_airport_month | 13.489 | 2.098 |  |  |
| aws-emr-larger | 3m | 3000000 | delay_by_airport_month_all_causes | 6.728 | 1.347 |  |  |
| aws-emr-larger | full | 7079081 | airline_airport_ranking | 2.507 | 0.828 |  |  |
| aws-emr-larger | full | 7079081 | delay_by_airport_month | 13.45 | 1.866 |  |  |
| aws-emr-larger | full | 7079081 | delay_by_airport_month_all_causes | 8.974 | 1.581 |  |  |
| aws-emr-larger | 14m | 14000000 | airline_airport_ranking | 3.813 | 1.037 |  |  |
| aws-emr-larger | 14m | 14000000 | delay_by_airport_month | 19.463 | 1.931 |  |  |
| aws-emr-larger | 14m | 14000000 | delay_by_airport_month_all_causes | 12.43 | 1.532 |  |  |
| aws-emr-larger | 28m | 28000000 | airline_airport_ranking | 4.992 | 0.893 |  |  |
| aws-emr-larger | 28m | 28000000 | delay_by_airport_month | 23.963 | 2.012 |  |  |
| aws-emr-larger | 28m | 28000000 | delay_by_airport_month_all_causes | 17.57 | 1.268 |  |  |
| docker-simulation | 100k | 100000 | airline_airport_ranking | 1.16 | 2.11 | 9.023 | 6.769 |
| docker-simulation | 100k | 100000 | delay_by_airport_month | 6.492 | 2.655 | 13.07 | 7.699 |
| docker-simulation | 100k | 100000 | delay_by_airport_month_all_causes | 2.889 | 1.56 | 7.337 | 4.764 |
| docker-simulation | 500k | 500000 | airline_airport_ranking | 1.058 | 2.082 | 8.953 | 20.666 |
| docker-simulation | 500k | 500000 | delay_by_airport_month | 5.74 | 2.59 | 14.245 | 22.629 |
| docker-simulation | 500k | 500000 | delay_by_airport_month_all_causes | 3.296 | 1.732 | 7.402 | 10.777 |
| docker-simulation | 1m | 1000000 | airline_airport_ranking | 1.104 | 2.151 | 9.05 | 38.476 |
| docker-simulation | 1m | 1000000 | delay_by_airport_month | 6.289 | 2.658 | 15.163 | 41.472 |
| docker-simulation | 1m | 1000000 | delay_by_airport_month_all_causes | 3.288 | 1.714 | 8.373 | 18.587 |
| docker-simulation | 1m_hc8 | 1000000 | airline_airport_ranking | 1.399 | 2.34 |  |  |
| docker-simulation | 1m_hc8 | 1000000 | delay_by_airport_month | 7.334 | 3.537 |  |  |
| docker-simulation | 1m_hc8 | 1000000 | delay_by_airport_month_all_causes | 3.675 | 2.369 |  |  |
| docker-simulation | 3m | 3000000 | airline_airport_ranking | 1.299 | 2.084 | 9.018 | 109.427 |
| docker-simulation | 3m | 3000000 | delay_by_airport_month | 7.092 | 2.725 | 22.284 | 117.145 |
| docker-simulation | 3m | 3000000 | delay_by_airport_month_all_causes | 4.042 | 2.165 | 12.359 | 48.924 |
| docker-simulation | full | 7079081 | airline_airport_ranking | 1.809 | 2.093 | 12.781 | 252.51 |
| docker-simulation | full | 7079081 | delay_by_airport_month | 8.428 | 2.877 | 35.814 | 273.263 |
| docker-simulation | full | 7079081 | delay_by_airport_month_all_causes | 6.346 | 1.486 | 19.946 | 108.158 |
| docker-simulation | 14m | 14000000 | airline_airport_ranking | 2.031 | 2.15 | 14.754 | 426.62 |
| docker-simulation | 14m | 14000000 | delay_by_airport_month | 10.082 | 2.701 | 56.009 | 534.17 |
| docker-simulation | 14m | 14000000 | delay_by_airport_month_all_causes | 7.082 | 1.392 | 30.828 | 215.534 |
| docker-simulation | 28m | 28000000 | airline_airport_ranking | 3.132 | 2.142 | 23.097 | 984.569 |
| docker-simulation | 28m | 28000000 | delay_by_airport_month | 13.282 | 2.76 | 99.359 | 1052.934 |
| docker-simulation | 28m | 28000000 | delay_by_airport_month_all_causes | 11.807 | 1.508 | 54.659 | 414.142 |
| docker-simulation-spark-sql-baseline-m4 | 1m | 1000000 | airline_airport_ranking | 3.591 |  |  |  |
| docker-simulation-spark-sql-baseline-m4 | 1m | 1000000 | delay_by_airport_month | 9.587 |  |  |  |
| docker-simulation-spark-sql-baseline-m4 | 1m | 1000000 | delay_by_airport_month_all_causes | 5.433 |  |  |  |
| docker-simulation-spark-sql-baseline-m4 | full | 7079081 | airline_airport_ranking | 4.12 |  |  |  |
| docker-simulation-spark-sql-baseline-m4 | full | 7079081 | delay_by_airport_month | 11.705 |  |  |  |
| docker-simulation-spark-sql-baseline-m4 | full | 7079081 | delay_by_airport_month_all_causes | 8.34 |  |  |  |
| docker-simulation-spark-sql-baseline-m4 | 14m | 14000000 | airline_airport_ranking | 6.127 |  |  |  |
| docker-simulation-spark-sql-baseline-m4 | 14m | 14000000 | delay_by_airport_month | 18.714 |  |  |  |
| docker-simulation-spark-sql-baseline-m4 | 14m | 14000000 | delay_by_airport_month_all_causes | 13.169 |  |  |  |
| docker-simulation-spark-sql-optimized-m4 | 1m | 1000000 | airline_airport_ranking | 1.048 |  |  |  |
| docker-simulation-spark-sql-optimized-m4 | 1m | 1000000 | delay_by_airport_month | 5.774 |  |  |  |
| docker-simulation-spark-sql-optimized-m4 | 1m | 1000000 | delay_by_airport_month_all_causes | 3.304 |  |  |  |
| docker-simulation-spark-sql-optimized-m4 | full | 7079081 | airline_airport_ranking | 1.674 |  |  |  |
| docker-simulation-spark-sql-optimized-m4 | full | 7079081 | delay_by_airport_month | 8.212 |  |  |  |
| docker-simulation-spark-sql-optimized-m4 | full | 7079081 | delay_by_airport_month_all_causes | 5.912 |  |  |  |
| docker-simulation-spark-sql-optimized-m4 | 14m | 14000000 | airline_airport_ranking | 1.982 |  |  |  |
| docker-simulation-spark-sql-optimized-m4 | 14m | 14000000 | delay_by_airport_month | 9.469 |  |  |  |
| docker-simulation-spark-sql-optimized-m4 | 14m | 14000000 | delay_by_airport_month_all_causes | 6.9 |  |  |  |
| local | 100k | 100000 | airline_airport_ranking | 0.893 | 0.595 | 8.976 | 6.523 |
| local | 100k | 100000 | delay_by_airport_month | 4.904 | 0.965 | 12.833 | 7.424 |
| local | 100k | 100000 | delay_by_airport_month_all_causes | 1.538 | 0.505 | 7.406 | 4.615 |
| local | 500k | 500000 | airline_airport_ranking | 1.104 | 0.628 | 8.816 | 20.664 |
| local | 500k | 500000 | delay_by_airport_month | 5.74 | 0.984 | 13.899 | 22.544 |
| local | 500k | 500000 | delay_by_airport_month_all_causes | 2.024 | 0.571 | 8.199 | 11.237 |
| local | 1m | 1000000 | airline_airport_ranking | 1.059 | 0.618 | 8.807 | 38.437 |
| local | 1m | 1000000 | delay_by_airport_month | 6.273 | 0.969 | 15.801 | 42.257 |
| local | 1m | 1000000 | delay_by_airport_month_all_causes | 2.518 | 0.594 | 9.069 | 18.838 |
| local | 1m_hc8 | 1000000 | airline_airport_ranking | 1.185 | 0.642 |  |  |
| local | 1m_hc8 | 1000000 | delay_by_airport_month | 6.097 | 1.331 |  |  |
| local | 1m_hc8 | 1000000 | delay_by_airport_month_all_causes | 2.697 | 0.84 |  |  |
| local | 3m | 3000000 | airline_airport_ranking | 1.59 | 0.608 | 8.765 | 106.486 |
| local | 3m | 3000000 | delay_by_airport_month | 7.262 | 1.032 | 21.218 | 116.861 |
| local | 3m | 3000000 | delay_by_airport_month_all_causes | 3.163 | 0.633 | 11.952 | 48.923 |
| local | full | 7079081 | airline_airport_ranking | 2.061 | 0.666 | 12.076 | 250.105 |
| local | full | 7079081 | delay_by_airport_month | 8.667 | 1.038 | 35.254 | 270.542 |
| local | full | 7079081 | delay_by_airport_month_all_causes | 6.028 | 0.719 | 19.472 | 107.546 |
| local | 14m | 14000000 | airline_airport_ranking | 1.912 | 0.591 | 13.898 | 491.004 |
| local | 14m | 14000000 | delay_by_airport_month | 8.74 | 1.073 | 54.747 | 530.46 |
| local | 14m | 14000000 | delay_by_airport_month_all_causes | 5.063 | 0.659 | 29.723 | 210.07 |
| local | 28m | 28000000 | airline_airport_ranking | 2.019 | 0.629 | 22.717 | 982.517 |
| local | 28m | 28000000 | delay_by_airport_month | 9.578 | 1.056 | 99.057 | 1062.927 |
| local | 28m | 28000000 | delay_by_airport_month_all_causes | 6.47 | 0.66 | 54.183 | 413.438 |
| local-spark-sql-baseline-m4 | 1m | 1000000 | airline_airport_ranking | 1.168 |  |  |  |
| local-spark-sql-baseline-m4 | 1m | 1000000 | delay_by_airport_month | 5.749 |  |  |  |
| local-spark-sql-baseline-m4 | 1m | 1000000 | delay_by_airport_month_all_causes | 2.313 |  |  |  |
| local-spark-sql-baseline-m4 | full | 7079081 | airline_airport_ranking | 1.454 |  |  |  |
| local-spark-sql-baseline-m4 | full | 7079081 | delay_by_airport_month | 7.842 |  |  |  |
| local-spark-sql-baseline-m4 | full | 7079081 | delay_by_airport_month_all_causes | 5.053 |  |  |  |
| local-spark-sql-baseline-m4 | 14m | 14000000 | airline_airport_ranking | 1.984 |  |  |  |
| local-spark-sql-baseline-m4 | 14m | 14000000 | delay_by_airport_month | 9.138 |  |  |  |
| local-spark-sql-baseline-m4 | 14m | 14000000 | delay_by_airport_month_all_causes | 4.906 |  |  |  |
| local-spark-sql-optimized-m4 | 1m | 1000000 | airline_airport_ranking | 0.91 |  |  |  |
| local-spark-sql-optimized-m4 | 1m | 1000000 | delay_by_airport_month | 4.684 |  |  |  |
| local-spark-sql-optimized-m4 | 1m | 1000000 | delay_by_airport_month_all_causes | 2.175 |  |  |  |
| local-spark-sql-optimized-m4 | full | 7079081 | airline_airport_ranking | 1.477 |  |  |  |
| local-spark-sql-optimized-m4 | full | 7079081 | delay_by_airport_month | 6.812 |  |  |  |
| local-spark-sql-optimized-m4 | full | 7079081 | delay_by_airport_month_all_causes | 5.328 |  |  |  |
| local-spark-sql-optimized-m4 | 14m | 14000000 | airline_airport_ranking | 1.671 |  |  |  |
| local-spark-sql-optimized-m4 | 14m | 14000000 | delay_by_airport_month | 8.259 |  |  |  |
| local-spark-sql-optimized-m4 | 14m | 14000000 | delay_by_airport_month_all_causes | 4.904 |  |  |  |
