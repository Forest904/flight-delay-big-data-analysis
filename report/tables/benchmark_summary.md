| environment | input_label | records | job_name | technology | runs | median_duration_seconds | mean_duration_seconds | min_duration_seconds | max_duration_seconds | stddev_duration_seconds | output_rows | run_id | timestamp_utc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| aws-emr | 100k | 100000 | airline_airport_ranking | Spark Core | 1 | 1.213 | 1.213 | 1.213 | 1.213 |  | 1641 | m4-hardened-smoke-3 | 2026-05-22T00:15:34.771522+00:00 |
| aws-emr | 100k | 100000 | airline_airport_ranking | Spark SQL | 1 | 3.984 | 3.984 | 3.984 | 3.984 |  | 1641 | m4-hardened-smoke-3 | 2026-05-22T00:15:34.771522+00:00 |
| aws-emr | 100k | 100000 | delay_by_airport_month | Spark Core | 1 | 1.864 | 1.864 | 1.864 | 1.864 |  | 6367 | m4-hardened-smoke-3 | 2026-05-22T00:15:34.771522+00:00 |
| aws-emr | 100k | 100000 | delay_by_airport_month | Spark SQL | 1 | 15.832 | 15.832 | 15.832 | 15.832 |  | 6367 | m4-hardened-smoke-3 | 2026-05-22T00:15:34.771522+00:00 |
| aws-emr | 500k | 500000 | airline_airport_ranking | Spark Core | 1 | 1.205 | 1.205 | 1.205 | 1.205 |  | 1707 | m4-emr-final-2 | 2026-05-21T22:51:56.622854+00:00 |
| aws-emr | 500k | 500000 | airline_airport_ranking | Spark SQL | 1 | 4.179 | 4.179 | 4.179 | 4.179 |  | 1707 | m4-emr-final-2 | 2026-05-21T22:51:56.622854+00:00 |
| aws-emr | 500k | 500000 | delay_by_airport_month | Spark Core | 1 | 1.706 | 1.706 | 1.706 | 1.706 |  | 9265 | m4-emr-final-2 | 2026-05-21T22:51:56.622854+00:00 |
| aws-emr | 500k | 500000 | delay_by_airport_month | Spark SQL | 1 | 13.879 | 13.879 | 13.879 | 13.879 |  | 9265 | m4-emr-final-2 | 2026-05-21T22:51:56.622854+00:00 |
| aws-emr | 1m | 1000000 | airline_airport_ranking | Spark Core | 3 | 1.243 | 1.277 | 1.177 | 1.411 | 0.121 | 1723 | m4-emr-final-2 | 2026-05-21T22:51:56.622854+00:00 |
| aws-emr | 1m | 1000000 | airline_airport_ranking | Spark SQL | 3 | 4.052 | 4.111 | 3.882 | 4.399 | 0.263 | 1723 | m4-emr-final-2 | 2026-05-21T22:51:56.622854+00:00 |
| aws-emr | 1m | 1000000 | delay_by_airport_month | Spark Core | 3 | 1.923 | 2.006 | 1.863 | 2.231 | 0.197 | 10206 | m4-emr-final-2 | 2026-05-21T22:51:56.622854+00:00 |
| aws-emr | 1m | 1000000 | delay_by_airport_month | Spark SQL | 3 | 15.126 | 14.696 | 13.826 | 15.137 | 0.754 | 10206 | m4-emr-final-2 | 2026-05-21T22:51:56.622854+00:00 |
| aws-emr | 3m | 3000000 | airline_airport_ranking | Spark Core | 1 | 1.249 | 1.249 | 1.249 | 1.249 |  | 1735 | m4-emr-final-2 | 2026-05-21T22:51:56.622854+00:00 |
| aws-emr | 3m | 3000000 | airline_airport_ranking | Spark SQL | 1 | 4.457 | 4.457 | 4.457 | 4.457 |  | 1735 | m4-emr-final-2 | 2026-05-21T22:51:56.622854+00:00 |
| aws-emr | 3m | 3000000 | delay_by_airport_month | Spark Core | 1 | 2.02 | 2.02 | 2.02 | 2.02 |  | 11417 | m4-emr-final-2 | 2026-05-21T22:51:56.622854+00:00 |
| aws-emr | 3m | 3000000 | delay_by_airport_month | Spark SQL | 1 | 14.582 | 14.582 | 14.582 | 14.582 |  | 11417 | m4-emr-final-2 | 2026-05-21T22:51:56.622854+00:00 |
| aws-emr | full | 7079081 | airline_airport_ranking | Spark Core | 3 | 1.106 | 1.134 | 1.104 | 1.191 | 0.049 | 1738 | m4-emr-final-2 | 2026-05-21T22:51:56.622854+00:00 |
| aws-emr | full | 7079081 | airline_airport_ranking | Spark SQL | 3 | 4.302 | 4.413 | 4.122 | 4.816 | 0.361 | 1738 | m4-emr-final-2 | 2026-05-21T22:51:56.622854+00:00 |
| aws-emr | full | 7079081 | delay_by_airport_month | Spark Core | 3 | 1.918 | 1.901 | 1.807 | 1.978 | 0.087 | 11902 | m4-emr-final-2 | 2026-05-21T22:51:56.622854+00:00 |
| aws-emr | full | 7079081 | delay_by_airport_month | Spark SQL | 3 | 15.505 | 15.939 | 15.256 | 17.055 | 0.975 | 11902 | m4-emr-final-2 | 2026-05-21T22:51:56.622854+00:00 |
| aws-emr | 14m | 14000000 | airline_airport_ranking | Spark Core | 1 | 1.235 | 1.235 | 1.235 | 1.235 |  | 1738 | m4-emr-final-2 | 2026-05-21T22:51:56.622854+00:00 |
| aws-emr | 14m | 14000000 | airline_airport_ranking | Spark SQL | 1 | 6.056 | 6.056 | 6.056 | 6.056 |  | 1738 | m4-emr-final-2 | 2026-05-21T22:51:56.622854+00:00 |
| aws-emr | 14m | 14000000 | delay_by_airport_month | Spark Core | 1 | 2.061 | 2.061 | 2.061 | 2.061 |  | 11902 | m4-emr-final-2 | 2026-05-21T22:51:56.622854+00:00 |
| aws-emr | 14m | 14000000 | delay_by_airport_month | Spark SQL | 1 | 18.147 | 18.147 | 18.147 | 18.147 |  | 11902 | m4-emr-final-2 | 2026-05-21T22:51:56.622854+00:00 |
| docker-simulation | 100k | 100000 | airline_airport_ranking | Hive | 1 | 8.983 | 8.983 | 8.983 | 8.983 |  | 1641 | 20260521T160042313560Z | 2026-05-21T16:00:42.313560+00:00 |
| docker-simulation | 100k | 100000 | airline_airport_ranking | Spark Core | 1 | 2.325 | 2.325 | 2.325 | 2.325 |  | 1641 | 20260521T160042313560Z | 2026-05-21T16:00:42.313560+00:00 |
| docker-simulation | 100k | 100000 | airline_airport_ranking | Spark SQL | 1 | 4.01 | 4.01 | 4.01 | 4.01 |  | 1641 | 20260521T160042313560Z | 2026-05-21T16:00:42.313560+00:00 |
| docker-simulation | 100k | 100000 | delay_by_airport_month | Hive | 1 | 12.025 | 12.025 | 12.025 | 12.025 |  | 6367 | 20260521T160042313560Z | 2026-05-21T16:00:42.313560+00:00 |
| docker-simulation | 100k | 100000 | delay_by_airport_month | Spark Core | 1 | 2.543 | 2.543 | 2.543 | 2.543 |  | 6367 | 20260521T160042313560Z | 2026-05-21T16:00:42.313560+00:00 |
| docker-simulation | 100k | 100000 | delay_by_airport_month | Spark SQL | 1 | 9.385 | 9.385 | 9.385 | 9.385 |  | 6367 | 20260521T160042313560Z | 2026-05-21T16:00:42.313560+00:00 |
| docker-simulation | 500k | 500000 | airline_airport_ranking | Hive | 1 | 8.972 | 8.972 | 8.972 | 8.972 |  | 1707 | 20260521T160042313560Z | 2026-05-21T16:00:42.313560+00:00 |
| docker-simulation | 500k | 500000 | airline_airport_ranking | Spark Core | 1 | 2.434 | 2.434 | 2.434 | 2.434 |  | 1707 | 20260521T160042313560Z | 2026-05-21T16:00:42.313560+00:00 |
| docker-simulation | 500k | 500000 | airline_airport_ranking | Spark SQL | 1 | 5.617 | 5.617 | 5.617 | 5.617 |  | 1707 | 20260521T160042313560Z | 2026-05-21T16:00:42.313560+00:00 |
| docker-simulation | 500k | 500000 | delay_by_airport_month | Hive | 1 | 12.619 | 12.619 | 12.619 | 12.619 |  | 9265 | 20260521T160042313560Z | 2026-05-21T16:00:42.313560+00:00 |
| docker-simulation | 500k | 500000 | delay_by_airport_month | Spark Core | 1 | 2.623 | 2.623 | 2.623 | 2.623 |  | 9265 | 20260521T160042313560Z | 2026-05-21T16:00:42.313560+00:00 |
| docker-simulation | 500k | 500000 | delay_by_airport_month | Spark SQL | 1 | 9.978 | 9.978 | 9.978 | 9.978 |  | 9265 | 20260521T160042313560Z | 2026-05-21T16:00:42.313560+00:00 |
| docker-simulation | 1m | 1000000 | airline_airport_ranking | Hive | 1 | 8.901 | 8.901 | 8.901 | 8.901 |  | 1723 | 20260521T160042313560Z | 2026-05-21T16:00:42.313560+00:00 |
| docker-simulation | 1m | 1000000 | airline_airport_ranking | Spark Core | 1 | 2.334 | 2.334 | 2.334 | 2.334 |  | 1723 | 20260521T160042313560Z | 2026-05-21T16:00:42.313560+00:00 |
| docker-simulation | 1m | 1000000 | airline_airport_ranking | Spark SQL | 1 | 4.444 | 4.444 | 4.444 | 4.444 |  | 1723 | 20260521T160042313560Z | 2026-05-21T16:00:42.313560+00:00 |
| docker-simulation | 1m | 1000000 | delay_by_airport_month | Hive | 1 | 12.584 | 12.584 | 12.584 | 12.584 |  | 10206 | 20260521T160042313560Z | 2026-05-21T16:00:42.313560+00:00 |
| docker-simulation | 1m | 1000000 | delay_by_airport_month | Spark Core | 1 | 2.619 | 2.619 | 2.619 | 2.619 |  | 10206 | 20260521T160042313560Z | 2026-05-21T16:00:42.313560+00:00 |
| docker-simulation | 1m | 1000000 | delay_by_airport_month | Spark SQL | 1 | 10.921 | 10.921 | 10.921 | 10.921 |  | 10206 | 20260521T160042313560Z | 2026-05-21T16:00:42.313560+00:00 |
| local | 14m | 14000000 | airline_airport_ranking | Spark Core | 3 | 0.564 | 0.572 | 0.562 | 0.589 | 0.015 | 1738 | 20260521T220744784794Z | 2026-05-21T22:07:44.784794+00:00 |
| local | 14m | 14000000 | airline_airport_ranking | Spark SQL | 3 | 2.241 | 2.238 | 2.106 | 2.367 | 0.131 | 1738 | 20260521T220744784794Z | 2026-05-21T22:07:44.784794+00:00 |
| local | 14m | 14000000 | delay_by_airport_month | Spark Core | 3 | 0.859 | 0.863 | 0.79 | 0.939 | 0.075 | 11902 | 20260521T220744784794Z | 2026-05-21T22:07:44.784794+00:00 |
| local | 14m | 14000000 | delay_by_airport_month | Spark SQL | 3 | 7.68 | 7.68 | 7.61 | 7.752 | 0.071 | 11902 | 20260521T220744784794Z | 2026-05-21T22:07:44.784794+00:00 |
