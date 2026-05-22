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
| aws-emr-larger | 1m | 1000000 | airline_airport_ranking | Spark Core | 3 | 1.018 | 1.016 | 0.991 | 1.038 | 0.024 | 1723 | m5-emr-3core-1m-full | 2026-05-22T00:46:03.790422+00:00 |
| aws-emr-larger | 1m | 1000000 | airline_airport_ranking | Spark SQL | 3 | 4.087 | 4.11 | 3.368 | 4.875 | 0.753 | 1723 | m5-emr-3core-1m-full | 2026-05-22T00:46:03.790422+00:00 |
| aws-emr-larger | 1m | 1000000 | delay_by_airport_month | Spark Core | 3 | 1.679 | 1.804 | 1.652 | 2.08 | 0.24 | 10206 | m5-emr-3core-1m-full | 2026-05-22T00:46:03.790422+00:00 |
| aws-emr-larger | 1m | 1000000 | delay_by_airport_month | Spark SQL | 3 | 14.374 | 14.402 | 14.303 | 14.527 | 0.115 | 10206 | m5-emr-3core-1m-full | 2026-05-22T00:46:03.790422+00:00 |
| aws-emr-larger | full | 7079081 | airline_airport_ranking | Spark Core | 3 | 0.919 | 0.978 | 0.911 | 1.103 | 0.109 | 1738 | m5-emr-3core-1m-full | 2026-05-22T00:46:03.790422+00:00 |
| aws-emr-larger | full | 7079081 | airline_airport_ranking | Spark SQL | 3 | 4.475 | 4.583 | 4.34 | 4.934 | 0.312 | 1738 | m5-emr-3core-1m-full | 2026-05-22T00:46:03.790422+00:00 |
| aws-emr-larger | full | 7079081 | delay_by_airport_month | Spark Core | 3 | 1.65 | 1.694 | 1.618 | 1.813 | 0.105 | 11902 | m5-emr-3core-1m-full | 2026-05-22T00:46:03.790422+00:00 |
| aws-emr-larger | full | 7079081 | delay_by_airport_month | Spark SQL | 3 | 16.309 | 15.691 | 14.437 | 16.328 | 1.086 | 11902 | m5-emr-3core-1m-full | 2026-05-22T00:46:03.790422+00:00 |
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
| local | 100k | 100000 | airline_airport_ranking | Hive | 3 | 14.322 | 14.207 | 13.91 | 14.389 | 0.259 | 1641 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | 100k | 100000 | airline_airport_ranking | MapReduce | 1 | 6.551 | 6.551 | 6.551 | 6.551 |  | 1641 | 20260521T153912538439Z | 2026-05-21T15:39:12.538439+00:00 |
| local | 100k | 100000 | airline_airport_ranking | Spark Core | 3 | 0.74 | 0.807 | 0.719 | 0.96 | 0.134 | 1641 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | 100k | 100000 | airline_airport_ranking | Spark SQL | 3 | 1.744 | 1.702 | 1.556 | 1.805 | 0.13 | 1641 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | 100k | 100000 | delay_by_airport_month | Hive | 3 | 19.841 | 20.207 | 19.595 | 21.187 | 0.857 | 6367 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | 100k | 100000 | delay_by_airport_month | MapReduce | 1 | 7.49 | 7.49 | 7.49 | 7.49 |  | 6367 | 20260521T153912538439Z | 2026-05-21T15:39:12.538439+00:00 |
| local | 100k | 100000 | delay_by_airport_month | Spark Core | 3 | 1.002 | 1.117 | 0.996 | 1.354 | 0.205 | 6367 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | 100k | 100000 | delay_by_airport_month | Spark SQL | 3 | 7.966 | 8.011 | 7.927 | 8.139 | 0.113 | 6367 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | 500k | 500000 | airline_airport_ranking | Hive | 3 | 14.125 | 14.602 | 14.117 | 15.563 | 0.832 | 1707 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | 500k | 500000 | airline_airport_ranking | Spark Core | 3 | 0.783 | 0.775 | 0.69 | 0.85 | 0.081 | 1707 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | 500k | 500000 | airline_airport_ranking | Spark SQL | 3 | 1.853 | 1.99 | 1.76 | 2.359 | 0.322 | 1707 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | 500k | 500000 | delay_by_airport_month | Hive | 3 | 21.005 | 21.178 | 20.566 | 21.962 | 0.714 | 9265 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | 500k | 500000 | delay_by_airport_month | Spark Core | 3 | 1.122 | 1.166 | 1.059 | 1.317 | 0.134 | 9265 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | 500k | 500000 | delay_by_airport_month | Spark SQL | 3 | 8.675 | 8.604 | 8.432 | 8.704 | 0.15 | 9265 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | 1m | 1000000 | airline_airport_ranking | Hive | 3 | 15.984 | 15.761 | 15.291 | 16.007 | 0.407 | 1723 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | 1m | 1000000 | airline_airport_ranking | Spark Core | 3 | 0.796 | 0.814 | 0.78 | 0.867 | 0.046 | 1723 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | 1m | 1000000 | airline_airport_ranking | Spark SQL | 3 | 2.5 | 2.483 | 2.406 | 2.542 | 0.07 | 1723 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | 1m | 1000000 | delay_by_airport_month | Hive | 3 | 22.411 | 22.38 | 22.087 | 22.642 | 0.279 | 10206 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | 1m | 1000000 | delay_by_airport_month | Spark Core | 3 | 1.195 | 1.211 | 1.172 | 1.265 | 0.048 | 10206 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | 1m | 1000000 | delay_by_airport_month | Spark SQL | 3 | 12.181 | 12.249 | 11.705 | 12.861 | 0.581 | 10206 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | 3m | 3000000 | airline_airport_ranking | Hive | 3 | 15.341 | 15.246 | 15.005 | 15.391 | 0.21 | 1735 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | 3m | 3000000 | airline_airport_ranking | Spark Core | 3 | 0.73 | 0.753 | 0.729 | 0.799 | 0.04 | 1735 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | 3m | 3000000 | airline_airport_ranking | Spark SQL | 3 | 3.11 | 3.065 | 2.85 | 3.237 | 0.197 | 1735 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | 3m | 3000000 | delay_by_airport_month | Hive | 3 | 25.069 | 25.134 | 24.998 | 25.335 | 0.178 | 11417 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | 3m | 3000000 | delay_by_airport_month | Spark Core | 3 | 1.126 | 1.14 | 1.101 | 1.192 | 0.047 | 11417 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | 3m | 3000000 | delay_by_airport_month | Spark SQL | 3 | 13.09 | 13.406 | 13.058 | 14.07 | 0.575 | 11417 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | full | 7079081 | airline_airport_ranking | Hive | 3 | 24.02 | 24.221 | 22.011 | 26.633 | 2.317 | 1738 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | full | 7079081 | airline_airport_ranking | Spark Core | 3 | 0.785 | 0.776 | 0.753 | 0.789 | 0.02 | 1738 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | full | 7079081 | airline_airport_ranking | Spark SQL | 3 | 3.4 | 3.411 | 3.301 | 3.532 | 0.116 | 1738 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | full | 7079081 | delay_by_airport_month | Hive | 3 | 35.005 | 34.473 | 32.788 | 35.625 | 1.491 | 11902 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | full | 7079081 | delay_by_airport_month | Spark Core | 3 | 1.221 | 1.208 | 1.176 | 1.229 | 0.029 | 11902 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | full | 7079081 | delay_by_airport_month | Spark SQL | 3 | 12.997 | 13.06 | 12.989 | 13.193 | 0.116 | 11902 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | 14m | 14000000 | airline_airport_ranking | Hive | 3 | 26.78 | 27.099 | 25.702 | 28.815 | 1.581 | 1738 | 20260522T142052973274Z | 2026-05-22T14:20:52.973274+00:00 |
| local | 14m | 14000000 | airline_airport_ranking | Spark Core | 3 | 0.792 | 0.787 | 0.737 | 0.831 | 0.047 | 1738 | 20260522T142052973274Z | 2026-05-22T14:20:52.973274+00:00 |
| local | 14m | 14000000 | airline_airport_ranking | Spark SQL | 3 | 3.314 | 3.239 | 3.086 | 3.318 | 0.133 | 1738 | 20260522T142052973274Z | 2026-05-22T14:20:52.973274+00:00 |
| local | 14m | 14000000 | delay_by_airport_month | Hive | 3 | 41.112 | 41.271 | 41.031 | 41.67 | 0.348 | 11902 | 20260522T142052973274Z | 2026-05-22T14:20:52.973274+00:00 |
| local | 14m | 14000000 | delay_by_airport_month | Spark Core | 3 | 1.223 | 1.226 | 1.185 | 1.269 | 0.042 | 11902 | 20260522T142052973274Z | 2026-05-22T14:20:52.973274+00:00 |
| local | 14m | 14000000 | delay_by_airport_month | Spark SQL | 3 | 11.868 | 11.863 | 11.619 | 12.104 | 0.243 | 11902 | 20260522T142052973274Z | 2026-05-22T14:20:52.973274+00:00 |
| local | 28m | 28000000 | airline_airport_ranking | Hive | 3 | 66.541 | 66.881 | 66.444 | 67.656 | 0.673 | 1738 | 20260522T144129099690Z | 2026-05-22T14:41:29.099690+00:00 |
| local | 28m | 28000000 | airline_airport_ranking | Spark Core | 3 | 0.83 | 0.904 | 0.742 | 1.14 | 0.209 | 1738 | 20260522T144129099690Z | 2026-05-22T14:41:29.099690+00:00 |
| local | 28m | 28000000 | airline_airport_ranking | Spark SQL | 3 | 3.373 | 3.443 | 3.292 | 3.665 | 0.196 | 1738 | 20260522T144129099690Z | 2026-05-22T14:41:29.099690+00:00 |
| local | 28m | 28000000 | delay_by_airport_month | Hive | 3 | 101.265 | 101.785 | 100.484 | 103.605 | 1.624 | 11902 | 20260522T144129099690Z | 2026-05-22T14:41:29.099690+00:00 |
| local | 28m | 28000000 | delay_by_airport_month | Spark Core | 3 | 1.333 | 1.403 | 1.252 | 1.625 | 0.196 | 11902 | 20260522T144129099690Z | 2026-05-22T14:41:29.099690+00:00 |
| local | 28m | 28000000 | delay_by_airport_month | Spark SQL | 3 | 11.924 | 11.896 | 11.79 | 11.973 | 0.095 | 11902 | 20260522T144129099690Z | 2026-05-22T14:41:29.099690+00:00 |
