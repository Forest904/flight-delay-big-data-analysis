| environment | input_label | records | job_name | technology | runs | median_duration_seconds | mean_duration_seconds | min_duration_seconds | max_duration_seconds | stddev_duration_seconds | output_rows | run_id | timestamp_utc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| aws-emr | 100k | 100000 | airline_airport_ranking | Spark Core | 1 | 1.213 | 1.213 | 1.213 | 1.213 |  | 1641 | m4-hardened-smoke-3 | 2026-05-22T00:15:34.771522+00:00 |
| aws-emr | 100k | 100000 | airline_airport_ranking | Spark SQL | 1 | 3.984 | 3.984 | 3.984 | 3.984 |  | 1641 | m4-hardened-smoke-3 | 2026-05-22T00:15:34.771522+00:00 |
| aws-emr | 100k | 100000 | delay_by_airport_month | Spark Core | 1 | 1.864 | 1.864 | 1.864 | 1.864 |  | 6367 | m4-hardened-smoke-3 | 2026-05-22T00:15:34.771522+00:00 |
| aws-emr | 100k | 100000 | delay_by_airport_month | Spark SQL | 1 | 15.832 | 15.832 | 15.832 | 15.832 |  | 6367 | m4-hardened-smoke-3 | 2026-05-22T00:15:34.771522+00:00 |
| aws-emr | 500k | 500000 | airline_airport_ranking | Spark Core | 2 | 1.187 | 1.187 | 1.181 | 1.192 | 0.008 | 1707 | m4-emr-p2-weak-cells | 2026-05-22T19:58:01.737116+00:00 |
| aws-emr | 500k | 500000 | airline_airport_ranking | Spark SQL | 2 | 3.898 | 3.898 | 3.627 | 4.169 | 0.383 | 1707 | m4-emr-p2-weak-cells | 2026-05-22T19:58:01.737116+00:00 |
| aws-emr | 500k | 500000 | delay_by_airport_month | Spark Core | 2 | 1.93 | 1.93 | 1.873 | 1.987 | 0.081 | 9265 | m4-emr-p2-weak-cells | 2026-05-22T19:58:01.737116+00:00 |
| aws-emr | 500k | 500000 | delay_by_airport_month | Spark SQL | 2 | 14.054 | 14.054 | 13.971 | 14.137 | 0.117 | 9265 | m4-emr-p2-weak-cells | 2026-05-22T19:58:01.737116+00:00 |
| aws-emr | 1m | 1000000 | airline_airport_ranking | Spark Core | 3 | 1.243 | 1.277 | 1.177 | 1.411 | 0.121 | 1723 | m4-emr-final-2 | 2026-05-21T22:51:56.622854+00:00 |
| aws-emr | 1m | 1000000 | airline_airport_ranking | Spark SQL | 3 | 4.052 | 4.111 | 3.882 | 4.399 | 0.263 | 1723 | m4-emr-final-2 | 2026-05-21T22:51:56.622854+00:00 |
| aws-emr | 1m | 1000000 | delay_by_airport_month | Spark Core | 3 | 1.923 | 2.006 | 1.863 | 2.231 | 0.197 | 10206 | m4-emr-final-2 | 2026-05-21T22:51:56.622854+00:00 |
| aws-emr | 1m | 1000000 | delay_by_airport_month | Spark SQL | 3 | 15.126 | 14.696 | 13.826 | 15.137 | 0.754 | 10206 | m4-emr-final-2 | 2026-05-21T22:51:56.622854+00:00 |
| aws-emr | 3m | 3000000 | airline_airport_ranking | Spark Core | 2 | 1.437 | 1.437 | 1.166 | 1.707 | 0.382 | 1735 | m4-emr-p2-weak-cells | 2026-05-22T19:58:01.737116+00:00 |
| aws-emr | 3m | 3000000 | airline_airport_ranking | Spark SQL | 2 | 4.08 | 4.08 | 3.911 | 4.249 | 0.24 | 1735 | m4-emr-p2-weak-cells | 2026-05-22T19:58:01.737116+00:00 |
| aws-emr | 3m | 3000000 | delay_by_airport_month | Spark Core | 2 | 2.473 | 2.473 | 2.148 | 2.797 | 0.459 | 11417 | m4-emr-p2-weak-cells | 2026-05-22T19:58:01.737116+00:00 |
| aws-emr | 3m | 3000000 | delay_by_airport_month | Spark SQL | 2 | 14.704 | 14.704 | 14.698 | 14.71 | 0.009 | 11417 | m4-emr-p2-weak-cells | 2026-05-22T19:58:01.737116+00:00 |
| aws-emr | full | 7079081 | airline_airport_ranking | Spark Core | 3 | 1.106 | 1.134 | 1.104 | 1.191 | 0.049 | 1738 | m4-emr-final-2 | 2026-05-21T22:51:56.622854+00:00 |
| aws-emr | full | 7079081 | airline_airport_ranking | Spark SQL | 3 | 4.302 | 4.413 | 4.122 | 4.816 | 0.361 | 1738 | m4-emr-final-2 | 2026-05-21T22:51:56.622854+00:00 |
| aws-emr | full | 7079081 | delay_by_airport_month | Spark Core | 3 | 1.918 | 1.901 | 1.807 | 1.978 | 0.087 | 11902 | m4-emr-final-2 | 2026-05-21T22:51:56.622854+00:00 |
| aws-emr | full | 7079081 | delay_by_airport_month | Spark SQL | 3 | 15.505 | 15.939 | 15.256 | 17.055 | 0.975 | 11902 | m4-emr-final-2 | 2026-05-21T22:51:56.622854+00:00 |
| aws-emr | 14m | 14000000 | airline_airport_ranking | Spark Core | 2 | 1.25 | 1.25 | 1.248 | 1.253 | 0.004 | 1738 | m4-emr-p2-weak-cells | 2026-05-22T19:58:01.737116+00:00 |
| aws-emr | 14m | 14000000 | airline_airport_ranking | Spark SQL | 2 | 5.359 | 5.359 | 5.203 | 5.515 | 0.22 | 1738 | m4-emr-p2-weak-cells | 2026-05-22T19:58:01.737116+00:00 |
| aws-emr | 14m | 14000000 | delay_by_airport_month | Spark Core | 2 | 2.265 | 2.265 | 2.123 | 2.408 | 0.201 | 11902 | m4-emr-p2-weak-cells | 2026-05-22T19:58:01.737116+00:00 |
| aws-emr | 14m | 14000000 | delay_by_airport_month | Spark SQL | 2 | 17.02 | 17.02 | 16.832 | 17.207 | 0.265 | 11902 | m4-emr-p2-weak-cells | 2026-05-22T19:58:01.737116+00:00 |
| aws-emr-larger | 1m | 1000000 | airline_airport_ranking | Spark Core | 3 | 1.018 | 1.016 | 0.991 | 1.038 | 0.024 | 1723 | m5-emr-3core-1m-full | 2026-05-22T00:46:03.790422+00:00 |
| aws-emr-larger | 1m | 1000000 | airline_airport_ranking | Spark SQL | 3 | 4.087 | 4.11 | 3.368 | 4.875 | 0.753 | 1723 | m5-emr-3core-1m-full | 2026-05-22T00:46:03.790422+00:00 |
| aws-emr-larger | 1m | 1000000 | delay_by_airport_month | Spark Core | 3 | 1.679 | 1.804 | 1.652 | 2.08 | 0.24 | 10206 | m5-emr-3core-1m-full | 2026-05-22T00:46:03.790422+00:00 |
| aws-emr-larger | 1m | 1000000 | delay_by_airport_month | Spark SQL | 3 | 14.374 | 14.402 | 14.303 | 14.527 | 0.115 | 10206 | m5-emr-3core-1m-full | 2026-05-22T00:46:03.790422+00:00 |
| aws-emr-larger | full | 7079081 | airline_airport_ranking | Spark Core | 3 | 0.919 | 0.978 | 0.911 | 1.103 | 0.109 | 1738 | m5-emr-3core-1m-full | 2026-05-22T00:46:03.790422+00:00 |
| aws-emr-larger | full | 7079081 | airline_airport_ranking | Spark SQL | 3 | 4.475 | 4.583 | 4.34 | 4.934 | 0.312 | 1738 | m5-emr-3core-1m-full | 2026-05-22T00:46:03.790422+00:00 |
| aws-emr-larger | full | 7079081 | delay_by_airport_month | Spark Core | 3 | 1.65 | 1.694 | 1.618 | 1.813 | 0.105 | 11902 | m5-emr-3core-1m-full | 2026-05-22T00:46:03.790422+00:00 |
| aws-emr-larger | full | 7079081 | delay_by_airport_month | Spark SQL | 3 | 16.309 | 15.691 | 14.437 | 16.328 | 1.086 | 11902 | m5-emr-3core-1m-full | 2026-05-22T00:46:03.790422+00:00 |
| aws-emr-larger | 14m | 14000000 | airline_airport_ranking | Spark Core | 3 | 0.995 | 0.986 | 0.954 | 1.01 | 0.029 | 1738 | m5-emr-p2-14m | 2026-05-22T20:35:33.699560+00:00 |
| aws-emr-larger | 14m | 14000000 | airline_airport_ranking | Spark SQL | 3 | 4.98 | 4.998 | 4.89 | 5.125 | 0.119 | 1738 | m5-emr-p2-14m | 2026-05-22T20:35:33.699560+00:00 |
| aws-emr-larger | 14m | 14000000 | delay_by_airport_month | Spark Core | 3 | 1.742 | 1.798 | 1.742 | 1.912 | 0.098 | 11902 | m5-emr-p2-14m | 2026-05-22T20:35:33.699560+00:00 |
| aws-emr-larger | 14m | 14000000 | delay_by_airport_month | Spark SQL | 3 | 18.056 | 17.832 | 16.484 | 18.957 | 1.252 | 11902 | m5-emr-p2-14m | 2026-05-22T20:35:33.699560+00:00 |
| aws-emr-larger | 28m | 28000000 | airline_airport_ranking | Spark Core | 1 | 1.037 | 1.037 | 1.037 | 1.037 |  | 1738 | m5-emr-p2-28m-smoke | 2026-05-23T00:06:39.794890+00:00 |
| aws-emr-larger | 28m | 28000000 | airline_airport_ranking | Spark SQL | 1 | 6.343 | 6.343 | 6.343 | 6.343 |  | 1738 | m5-emr-p2-28m-smoke | 2026-05-23T00:06:39.794890+00:00 |
| aws-emr-larger | 28m | 28000000 | delay_by_airport_month | Spark Core | 1 | 2.321 | 2.321 | 2.321 | 2.321 |  | 11902 | m5-emr-p2-28m-smoke | 2026-05-23T00:06:39.794890+00:00 |
| aws-emr-larger | 28m | 28000000 | delay_by_airport_month | Spark SQL | 1 | 19.184 | 19.184 | 19.184 | 19.184 |  | 11902 | m5-emr-p2-28m-smoke | 2026-05-23T00:06:39.794890+00:00 |
| docker-simulation | 100k | 100000 | airline_airport_ranking | Hive | 3 | 18.288 | 18.243 | 17.96 | 18.481 | 0.263 | 1641 | 20260522T161751426398Z | 2026-05-22T16:17:51.426398+00:00 |
| docker-simulation | 100k | 100000 | airline_airport_ranking | Spark Core | 3 | 6.214 | 6.142 | 5.99 | 6.223 | 0.132 | 1641 | 20260522T161751426398Z | 2026-05-22T16:17:51.426398+00:00 |
| docker-simulation | 100k | 100000 | airline_airport_ranking | Spark SQL | 3 | 12.685 | 13.654 | 11.637 | 16.64 | 2.638 | 1641 | 20260522T161751426398Z | 2026-05-22T16:17:51.426398+00:00 |
| docker-simulation | 100k | 100000 | delay_by_airport_month | Hive | 3 | 27.848 | 28.776 | 26.939 | 31.542 | 2.438 | 6367 | 20260522T161751426398Z | 2026-05-22T16:17:51.426398+00:00 |
| docker-simulation | 100k | 100000 | delay_by_airport_month | Spark Core | 3 | 6.954 | 6.893 | 6.639 | 7.086 | 0.23 | 6367 | 20260522T161751426398Z | 2026-05-22T16:17:51.426398+00:00 |
| docker-simulation | 100k | 100000 | delay_by_airport_month | Spark SQL | 3 | 23.69 | 24.446 | 23.594 | 26.055 | 1.394 | 6367 | 20260522T161751426398Z | 2026-05-22T16:17:51.426398+00:00 |
| docker-simulation | 500k | 500000 | airline_airport_ranking | Hive | 3 | 18.131 | 15.771 | 10.345 | 18.836 | 4.712 | 1707 | 20260522T161751426398Z | 2026-05-22T16:17:51.426398+00:00 |
| docker-simulation | 500k | 500000 | airline_airport_ranking | Spark Core | 3 | 5.974 | 6.105 | 5.926 | 6.415 | 0.269 | 1707 | 20260522T161751426398Z | 2026-05-22T16:17:51.426398+00:00 |
| docker-simulation | 500k | 500000 | airline_airport_ranking | Spark SQL | 3 | 12.537 | 13.133 | 12.01 | 14.851 | 1.511 | 1707 | 20260522T161751426398Z | 2026-05-22T16:17:51.426398+00:00 |
| docker-simulation | 500k | 500000 | delay_by_airport_month | Hive | 3 | 28.206 | 27.802 | 25.903 | 29.296 | 1.733 | 9265 | 20260522T161751426398Z | 2026-05-22T16:17:51.426398+00:00 |
| docker-simulation | 500k | 500000 | delay_by_airport_month | Spark Core | 3 | 7.256 | 7.357 | 6.613 | 8.202 | 0.799 | 9265 | 20260522T161751426398Z | 2026-05-22T16:17:51.426398+00:00 |
| docker-simulation | 500k | 500000 | delay_by_airport_month | Spark SQL | 3 | 25.606 | 25.493 | 25.197 | 25.678 | 0.26 | 9265 | 20260522T161751426398Z | 2026-05-22T16:17:51.426398+00:00 |
| docker-simulation | 1m | 1000000 | airline_airport_ranking | Hive | 3 | 10.094 | 10.491 | 10.077 | 11.301 | 0.702 | 1723 | 20260522T161751426398Z | 2026-05-22T16:17:51.426398+00:00 |
| docker-simulation | 1m | 1000000 | airline_airport_ranking | Spark Core | 3 | 3.044 | 3.017 | 2.93 | 3.079 | 0.078 | 1723 | 20260522T161751426398Z | 2026-05-22T16:17:51.426398+00:00 |
| docker-simulation | 1m | 1000000 | airline_airport_ranking | Spark SQL | 3 | 5.869 | 6.162 | 5.697 | 6.922 | 0.663 | 1723 | 20260522T161751426398Z | 2026-05-22T16:17:51.426398+00:00 |
| docker-simulation | 1m | 1000000 | delay_by_airport_month | Hive | 3 | 16.797 | 17.116 | 16.305 | 18.245 | 1.009 | 10206 | 20260522T161751426398Z | 2026-05-22T16:17:51.426398+00:00 |
| docker-simulation | 1m | 1000000 | delay_by_airport_month | Spark Core | 3 | 3.673 | 3.653 | 3.457 | 3.829 | 0.187 | 10206 | 20260522T161751426398Z | 2026-05-22T16:17:51.426398+00:00 |
| docker-simulation | 1m | 1000000 | delay_by_airport_month | Spark SQL | 3 | 14.541 | 14.559 | 14.242 | 14.895 | 0.327 | 10206 | 20260522T161751426398Z | 2026-05-22T16:17:51.426398+00:00 |
| docker-simulation | 3m | 3000000 | airline_airport_ranking | Hive | 3 | 8.83 | 8.843 | 8.713 | 8.986 | 0.137 | 1735 | 20260523T002216937593Z | 2026-05-23T00:22:16.937593+00:00 |
| docker-simulation | 3m | 3000000 | airline_airport_ranking | Spark Core | 3 | 2.292 | 2.343 | 2.227 | 2.51 | 0.148 | 1735 | 20260523T002216937593Z | 2026-05-23T00:22:16.937593+00:00 |
| docker-simulation | 3m | 3000000 | airline_airport_ranking | Spark SQL | 3 | 5.813 | 5.837 | 5.392 | 6.304 | 0.457 | 1735 | 20260523T002216937593Z | 2026-05-23T00:22:16.937593+00:00 |
| docker-simulation | 3m | 3000000 | delay_by_airport_month | Hive | 3 | 13.976 | 14.296 | 13.619 | 15.293 | 0.881 | 11417 | 20260523T002216937593Z | 2026-05-23T00:22:16.937593+00:00 |
| docker-simulation | 3m | 3000000 | delay_by_airport_month | Spark Core | 3 | 2.589 | 2.595 | 2.549 | 2.647 | 0.049 | 11417 | 20260523T002216937593Z | 2026-05-23T00:22:16.937593+00:00 |
| docker-simulation | 3m | 3000000 | delay_by_airport_month | Spark SQL | 3 | 11.369 | 11.378 | 10.6 | 12.165 | 0.783 | 11417 | 20260523T002216937593Z | 2026-05-23T00:22:16.937593+00:00 |
| docker-simulation | full | 7079081 | airline_airport_ranking | Hive | 3 | 13.464 | 13.461 | 13.429 | 13.491 | 0.031 | 1738 | 20260523T002948918166Z | 2026-05-23T00:29:48.918166+00:00 |
| docker-simulation | full | 7079081 | airline_airport_ranking | Spark Core | 3 | 2.34 | 2.338 | 2.3 | 2.375 | 0.037 | 1738 | 20260523T002948918166Z | 2026-05-23T00:29:48.918166+00:00 |
| docker-simulation | full | 7079081 | airline_airport_ranking | Spark SQL | 3 | 6.444 | 6.229 | 5.705 | 6.538 | 0.457 | 1738 | 20260523T002948918166Z | 2026-05-23T00:29:48.918166+00:00 |
| docker-simulation | full | 7079081 | delay_by_airport_month | Hive | 3 | 19.24 | 19.211 | 19.121 | 19.272 | 0.079 | 11902 | 20260523T002948918166Z | 2026-05-23T00:29:48.918166+00:00 |
| docker-simulation | full | 7079081 | delay_by_airport_month | Spark Core | 3 | 2.774 | 2.801 | 2.769 | 2.858 | 0.05 | 11902 | 20260523T002948918166Z | 2026-05-23T00:29:48.918166+00:00 |
| docker-simulation | full | 7079081 | delay_by_airport_month | Spark SQL | 3 | 12.503 | 12.65 | 12.481 | 12.966 | 0.274 | 11902 | 20260523T002948918166Z | 2026-05-23T00:29:48.918166+00:00 |
| docker-simulation | 14m | 14000000 | airline_airport_ranking | Hive | 3 | 15.326 | 15.341 | 15.253 | 15.443 | 0.096 | 1738 | 20260523T004842214881Z | 2026-05-23T00:48:42.214881+00:00 |
| docker-simulation | 14m | 14000000 | airline_airport_ranking | Spark Core | 3 | 2.4 | 2.356 | 2.266 | 2.403 | 0.079 | 1738 | 20260523T003851694527Z | 2026-05-23T00:38:51.694527+00:00 |
| docker-simulation | 14m | 14000000 | airline_airport_ranking | Spark SQL | 3 | 5.995 | 6.04 | 5.978 | 6.148 | 0.093 | 1738 | 20260523T003851694527Z | 2026-05-23T00:38:51.694527+00:00 |
| docker-simulation | 14m | 14000000 | delay_by_airport_month | Hive | 3 | 23.822 | 23.824 | 23.75 | 23.899 | 0.075 | 11902 | 20260523T004842214881Z | 2026-05-23T00:48:42.214881+00:00 |
| docker-simulation | 14m | 14000000 | delay_by_airport_month | Spark Core | 3 | 2.826 | 2.824 | 2.785 | 2.86 | 0.038 | 11902 | 20260523T003851694527Z | 2026-05-23T00:38:51.694527+00:00 |
| docker-simulation | 14m | 14000000 | delay_by_airport_month | Spark SQL | 3 | 13.316 | 13.278 | 13.197 | 13.32 | 0.07 | 11902 | 20260523T003851694527Z | 2026-05-23T00:38:51.694527+00:00 |
| docker-simulation | 28m | 28000000 | airline_airport_ranking | Hive | 3 | 22.965 | 23.165 | 22.76 | 23.77 | 0.534 | 1738 | 20260523T010842627918Z | 2026-05-23T01:08:42.627918+00:00 |
| docker-simulation | 28m | 28000000 | airline_airport_ranking | Spark Core | 3 | 2.266 | 2.26 | 2.188 | 2.325 | 0.069 | 1738 | 20260523T005223008588Z | 2026-05-23T00:52:23.008588+00:00 |
| docker-simulation | 28m | 28000000 | airline_airport_ranking | Spark SQL | 3 | 7.379 | 7.605 | 7.355 | 8.08 | 0.412 | 1738 | 20260523T005223008588Z | 2026-05-23T00:52:23.008588+00:00 |
| docker-simulation | 28m | 28000000 | delay_by_airport_month | Hive | 3 | 35.275 | 35.512 | 35.184 | 36.078 | 0.492 | 11902 | 20260523T010842627918Z | 2026-05-23T01:08:42.627918+00:00 |
| docker-simulation | 28m | 28000000 | delay_by_airport_month | Spark Core | 3 | 2.76 | 2.808 | 2.732 | 2.932 | 0.108 | 11902 | 20260523T005223008588Z | 2026-05-23T00:52:23.008588+00:00 |
| docker-simulation | 28m | 28000000 | delay_by_airport_month | Spark SQL | 3 | 14.397 | 14.629 | 14.298 | 15.192 | 0.49 | 11902 | 20260523T005223008588Z | 2026-05-23T00:52:23.008588+00:00 |
| docker-simulation-spark-sql-baseline-m4 | 1m | 1000000 | airline_airport_ranking | Spark SQL | 3 | 3.591 | 3.69 | 3.494 | 3.986 | 0.261 | 1723 | 20260523T222744444536Z | 2026-05-23T22:27:44.444536+00:00 |
| docker-simulation-spark-sql-baseline-m4 | 1m | 1000000 | delay_by_airport_month | Spark SQL | 3 | 9.587 | 9.585 | 9.275 | 9.894 | 0.31 | 11861 | 20260523T222744444536Z | 2026-05-23T22:27:44.444536+00:00 |
| docker-simulation-spark-sql-baseline-m4 | 1m | 1000000 | delay_by_airport_month_all_causes | Spark SQL | 3 | 5.433 | 5.607 | 5.356 | 6.031 | 0.37 | 27416 | 20260523T222744444536Z | 2026-05-23T22:27:44.444536+00:00 |
| docker-simulation-spark-sql-baseline-m4 | full | 7079081 | airline_airport_ranking | Spark SQL | 3 | 4.12 | 4.193 | 4.085 | 4.374 | 0.158 | 1738 | 20260523T222744444536Z | 2026-05-23T22:27:44.444536+00:00 |
| docker-simulation-spark-sql-baseline-m4 | full | 7079081 | delay_by_airport_month | Spark SQL | 3 | 11.705 | 11.781 | 11.658 | 11.979 | 0.173 | 14804 | 20260523T222744444536Z | 2026-05-23T22:27:44.444536+00:00 |
| docker-simulation-spark-sql-baseline-m4 | full | 7079081 | delay_by_airport_month_all_causes | Spark SQL | 3 | 8.34 | 8.34 | 8.287 | 8.392 | 0.052 | 46745 | 20260523T222744444536Z | 2026-05-23T22:27:44.444536+00:00 |
| docker-simulation-spark-sql-baseline-m4 | 14m | 14000000 | airline_airport_ranking | Spark SQL | 3 | 6.127 | 5.657 | 4.546 | 6.299 | 0.966 | 1738 | 20260523T222744444536Z | 2026-05-23T22:27:44.444536+00:00 |
| docker-simulation-spark-sql-baseline-m4 | 14m | 14000000 | delay_by_airport_month | Spark SQL | 3 | 18.714 | 17.106 | 12.768 | 19.837 | 3.799 | 14804 | 20260523T222744444536Z | 2026-05-23T22:27:44.444536+00:00 |
| docker-simulation-spark-sql-baseline-m4 | 14m | 14000000 | delay_by_airport_month_all_causes | Spark SQL | 3 | 13.169 | 12.059 | 9.345 | 13.662 | 2.363 | 46745 | 20260523T222744444536Z | 2026-05-23T22:27:44.444536+00:00 |
| docker-simulation-spark-sql-optimized-m4 | 1m | 1000000 | airline_airport_ranking | Spark SQL | 3 | 1.048 | 1.04 | 0.965 | 1.106 | 0.071 | 1723 | 20260523T224239080920Z | 2026-05-23T22:42:39.080920+00:00 |
| docker-simulation-spark-sql-optimized-m4 | 1m | 1000000 | delay_by_airport_month | Spark SQL | 3 | 5.774 | 5.885 | 5.588 | 6.294 | 0.366 | 11861 | 20260523T224239080920Z | 2026-05-23T22:42:39.080920+00:00 |
| docker-simulation-spark-sql-optimized-m4 | 1m | 1000000 | delay_by_airport_month_all_causes | Spark SQL | 3 | 3.304 | 3.338 | 3.017 | 3.693 | 0.339 | 27416 | 20260523T224239080920Z | 2026-05-23T22:42:39.080920+00:00 |
| docker-simulation-spark-sql-optimized-m4 | full | 7079081 | airline_airport_ranking | Spark SQL | 3 | 1.674 | 1.676 | 1.651 | 1.703 | 0.026 | 1738 | 20260523T224239080920Z | 2026-05-23T22:42:39.080920+00:00 |
| docker-simulation-spark-sql-optimized-m4 | full | 7079081 | delay_by_airport_month | Spark SQL | 3 | 8.212 | 8.204 | 8.182 | 8.218 | 0.019 | 14804 | 20260523T224239080920Z | 2026-05-23T22:42:39.080920+00:00 |
| docker-simulation-spark-sql-optimized-m4 | full | 7079081 | delay_by_airport_month_all_causes | Spark SQL | 3 | 5.912 | 6.002 | 5.868 | 6.227 | 0.196 | 46745 | 20260523T224239080920Z | 2026-05-23T22:42:39.080920+00:00 |
| docker-simulation-spark-sql-optimized-m4 | 14m | 14000000 | airline_airport_ranking | Spark SQL | 3 | 1.982 | 2.017 | 1.9 | 2.167 | 0.137 | 1738 | 20260523T224239080920Z | 2026-05-23T22:42:39.080920+00:00 |
| docker-simulation-spark-sql-optimized-m4 | 14m | 14000000 | delay_by_airport_month | Spark SQL | 3 | 9.469 | 9.9 | 9.223 | 11.008 | 0.968 | 14804 | 20260523T224239080920Z | 2026-05-23T22:42:39.080920+00:00 |
| docker-simulation-spark-sql-optimized-m4 | 14m | 14000000 | delay_by_airport_month_all_causes | Spark SQL | 3 | 6.9 | 6.9 | 6.627 | 7.173 | 0.273 | 46745 | 20260523T224239080920Z | 2026-05-23T22:42:39.080920+00:00 |
| local | 100k | 100000 | airline_airport_ranking | Hive | 3 | 14.322 | 14.207 | 13.91 | 14.389 | 0.259 | 1641 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | 100k | 100000 | airline_airport_ranking | MapReduce | 3 | 6.708 | 6.705 | 6.693 | 6.713 | 0.01 | 1641 | 20260522T182250129354Z | 2026-05-22T18:22:50.129354+00:00 |
| local | 100k | 100000 | airline_airport_ranking | Spark Core | 3 | 0.74 | 0.807 | 0.719 | 0.96 | 0.134 | 1641 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | 100k | 100000 | airline_airport_ranking | Spark SQL | 3 | 1.744 | 1.702 | 1.556 | 1.805 | 0.13 | 1641 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | 100k | 100000 | delay_by_airport_month | Hive | 3 | 19.841 | 20.207 | 19.595 | 21.187 | 0.857 | 6367 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | 100k | 100000 | delay_by_airport_month | MapReduce | 3 | 7.644 | 7.306 | 6.623 | 7.65 | 0.591 | 6367 | 20260522T182250129354Z | 2026-05-22T18:22:50.129354+00:00 |
| local | 100k | 100000 | delay_by_airport_month | Spark Core | 3 | 1.002 | 1.117 | 0.996 | 1.354 | 0.205 | 6367 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | 100k | 100000 | delay_by_airport_month | Spark SQL | 3 | 7.966 | 8.011 | 7.927 | 8.139 | 0.113 | 6367 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | 500k | 500000 | airline_airport_ranking | Hive | 3 | 14.125 | 14.602 | 14.117 | 15.563 | 0.832 | 1707 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | 500k | 500000 | airline_airport_ranking | MapReduce | 3 | 20.328 | 20.366 | 19.337 | 21.433 | 1.048 | 1707 | 20260522T182250129354Z | 2026-05-22T18:22:50.129354+00:00 |
| local | 500k | 500000 | airline_airport_ranking | Spark Core | 3 | 0.783 | 0.775 | 0.69 | 0.85 | 0.081 | 1707 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | 500k | 500000 | airline_airport_ranking | Spark SQL | 3 | 1.853 | 1.99 | 1.76 | 2.359 | 0.322 | 1707 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | 500k | 500000 | delay_by_airport_month | Hive | 3 | 21.005 | 21.178 | 20.566 | 21.962 | 0.714 | 9265 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | 500k | 500000 | delay_by_airport_month | MapReduce | 3 | 23.3 | 23.286 | 23.256 | 23.302 | 0.026 | 9265 | 20260522T182250129354Z | 2026-05-22T18:22:50.129354+00:00 |
| local | 500k | 500000 | delay_by_airport_month | Spark Core | 3 | 1.122 | 1.166 | 1.059 | 1.317 | 0.134 | 9265 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | 500k | 500000 | delay_by_airport_month | Spark SQL | 3 | 8.675 | 8.604 | 8.432 | 8.704 | 0.15 | 9265 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | 1m | 1000000 | airline_airport_ranking | Hive | 3 | 15.984 | 15.761 | 15.291 | 16.007 | 0.407 | 1723 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | 1m | 1000000 | airline_airport_ranking | MapReduce | 3 | 37.887 | 37.606 | 36.916 | 38.016 | 0.601 | 1723 | 20260522T182250129354Z | 2026-05-22T18:22:50.129354+00:00 |
| local | 1m | 1000000 | airline_airport_ranking | Spark Core | 3 | 0.796 | 0.814 | 0.78 | 0.867 | 0.046 | 1723 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | 1m | 1000000 | airline_airport_ranking | Spark SQL | 3 | 2.5 | 2.483 | 2.406 | 2.542 | 0.07 | 1723 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | 1m | 1000000 | delay_by_airport_month | Hive | 3 | 22.411 | 22.38 | 22.087 | 22.642 | 0.279 | 10206 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | 1m | 1000000 | delay_by_airport_month | MapReduce | 3 | 40.762 | 40.156 | 38.838 | 40.867 | 1.142 | 10206 | 20260522T182250129354Z | 2026-05-22T18:22:50.129354+00:00 |
| local | 1m | 1000000 | delay_by_airport_month | Spark Core | 3 | 1.195 | 1.211 | 1.172 | 1.265 | 0.048 | 10206 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | 1m | 1000000 | delay_by_airport_month | Spark SQL | 3 | 12.181 | 12.249 | 11.705 | 12.861 | 0.581 | 10206 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | 3m | 3000000 | airline_airport_ranking | Hive | 3 | 15.341 | 15.246 | 15.005 | 15.391 | 0.21 | 1735 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | 3m | 3000000 | airline_airport_ranking | MapReduce | 3 | 105.491 | 106.612 | 105.03 | 109.316 | 2.353 | 1735 | 20260522T182250129354Z | 2026-05-22T18:22:50.129354+00:00 |
| local | 3m | 3000000 | airline_airport_ranking | Spark Core | 3 | 0.73 | 0.753 | 0.729 | 0.799 | 0.04 | 1735 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | 3m | 3000000 | airline_airport_ranking | Spark SQL | 3 | 3.11 | 3.065 | 2.85 | 3.237 | 0.197 | 1735 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | 3m | 3000000 | delay_by_airport_month | Hive | 3 | 25.069 | 25.134 | 24.998 | 25.335 | 0.178 | 11417 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | 3m | 3000000 | delay_by_airport_month | MapReduce | 3 | 116.11 | 114.727 | 110.95 | 117.121 | 3.31 | 11417 | 20260522T182250129354Z | 2026-05-22T18:22:50.129354+00:00 |
| local | 3m | 3000000 | delay_by_airport_month | Spark Core | 3 | 1.126 | 1.14 | 1.101 | 1.192 | 0.047 | 11417 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | 3m | 3000000 | delay_by_airport_month | Spark SQL | 3 | 13.09 | 13.406 | 13.058 | 14.07 | 0.575 | 11417 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | full | 7079081 | airline_airport_ranking | Hive | 3 | 24.02 | 24.221 | 22.011 | 26.633 | 2.317 | 1738 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | full | 7079081 | airline_airport_ranking | MapReduce | 3 | 249.968 | 248.431 | 241.338 | 253.988 | 6.464 | 1738 | 20260522T182250129354Z | 2026-05-22T18:22:50.129354+00:00 |
| local | full | 7079081 | airline_airport_ranking | Spark Core | 3 | 0.785 | 0.776 | 0.753 | 0.789 | 0.02 | 1738 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | full | 7079081 | airline_airport_ranking | Spark SQL | 3 | 3.4 | 3.411 | 3.301 | 3.532 | 0.116 | 1738 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | full | 7079081 | delay_by_airport_month | Hive | 3 | 35.005 | 34.473 | 32.788 | 35.625 | 1.491 | 11902 | 20260522T133525179005Z | 2026-05-22T13:35:25.179005+00:00 |
| local | full | 7079081 | delay_by_airport_month | MapReduce | 3 | 267.284 | 267.172 | 265.238 | 268.993 | 1.88 | 11902 | 20260522T182250129354Z | 2026-05-22T18:22:50.129354+00:00 |
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
| local-spark-sql-baseline-m4 | 1m | 1000000 | airline_airport_ranking | Spark SQL | 3 | 1.168 | 1.164 | 1.127 | 1.198 | 0.036 | 1723 | 20260523T222417711003Z | 2026-05-23T22:24:17.711003+00:00 |
| local-spark-sql-baseline-m4 | 1m | 1000000 | delay_by_airport_month | Spark SQL | 3 | 5.749 | 5.775 | 5.73 | 5.846 | 0.062 | 11861 | 20260523T222417711003Z | 2026-05-23T22:24:17.711003+00:00 |
| local-spark-sql-baseline-m4 | 1m | 1000000 | delay_by_airport_month_all_causes | Spark SQL | 3 | 2.313 | 2.288 | 2.213 | 2.337 | 0.066 | 27416 | 20260523T222417711003Z | 2026-05-23T22:24:17.711003+00:00 |
| local-spark-sql-baseline-m4 | full | 7079081 | airline_airport_ranking | Spark SQL | 3 | 1.454 | 1.469 | 1.414 | 1.539 | 0.064 | 1738 | 20260523T222417711003Z | 2026-05-23T22:24:17.711003+00:00 |
| local-spark-sql-baseline-m4 | full | 7079081 | delay_by_airport_month | Spark SQL | 3 | 7.842 | 7.878 | 7.609 | 8.182 | 0.288 | 14804 | 20260523T222417711003Z | 2026-05-23T22:24:17.711003+00:00 |
| local-spark-sql-baseline-m4 | full | 7079081 | delay_by_airport_month_all_causes | Spark SQL | 3 | 5.053 | 5.09 | 4.962 | 5.256 | 0.151 | 46745 | 20260523T222417711003Z | 2026-05-23T22:24:17.711003+00:00 |
| local-spark-sql-baseline-m4 | 14m | 14000000 | airline_airport_ranking | Spark SQL | 3 | 1.984 | 1.992 | 1.967 | 2.026 | 0.03 | 1738 | 20260523T222417711003Z | 2026-05-23T22:24:17.711003+00:00 |
| local-spark-sql-baseline-m4 | 14m | 14000000 | delay_by_airport_month | Spark SQL | 3 | 9.138 | 9.138 | 9.133 | 9.142 | 0.004 | 14804 | 20260523T222417711003Z | 2026-05-23T22:24:17.711003+00:00 |
| local-spark-sql-baseline-m4 | 14m | 14000000 | delay_by_airport_month_all_causes | Spark SQL | 3 | 4.906 | 4.924 | 4.787 | 5.08 | 0.147 | 46745 | 20260523T222417711003Z | 2026-05-23T22:24:17.711003+00:00 |
| local-spark-sql-optimized-m4 | 1m | 1000000 | airline_airport_ranking | Spark SQL | 3 | 0.91 | 0.897 | 0.841 | 0.94 | 0.051 | 1723 | 20260523T223936581097Z | 2026-05-23T22:39:36.581097+00:00 |
| local-spark-sql-optimized-m4 | 1m | 1000000 | delay_by_airport_month | Spark SQL | 3 | 4.684 | 4.675 | 4.609 | 4.731 | 0.062 | 11861 | 20260523T223936581097Z | 2026-05-23T22:39:36.581097+00:00 |
| local-spark-sql-optimized-m4 | 1m | 1000000 | delay_by_airport_month_all_causes | Spark SQL | 3 | 2.175 | 2.173 | 2.12 | 2.225 | 0.053 | 27416 | 20260523T223936581097Z | 2026-05-23T22:39:36.581097+00:00 |
| local-spark-sql-optimized-m4 | full | 7079081 | airline_airport_ranking | Spark SQL | 3 | 1.477 | 1.47 | 1.379 | 1.555 | 0.088 | 1738 | 20260523T223936581097Z | 2026-05-23T22:39:36.581097+00:00 |
| local-spark-sql-optimized-m4 | full | 7079081 | delay_by_airport_month | Spark SQL | 3 | 6.812 | 6.904 | 6.757 | 7.143 | 0.209 | 14804 | 20260523T223936581097Z | 2026-05-23T22:39:36.581097+00:00 |
| local-spark-sql-optimized-m4 | full | 7079081 | delay_by_airport_month_all_causes | Spark SQL | 3 | 5.328 | 5.216 | 4.967 | 5.352 | 0.215 | 46745 | 20260523T223936581097Z | 2026-05-23T22:39:36.581097+00:00 |
| local-spark-sql-optimized-m4 | 14m | 14000000 | airline_airport_ranking | Spark SQL | 3 | 1.671 | 1.675 | 1.614 | 1.741 | 0.064 | 1738 | 20260523T223936581097Z | 2026-05-23T22:39:36.581097+00:00 |
| local-spark-sql-optimized-m4 | 14m | 14000000 | delay_by_airport_month | Spark SQL | 3 | 8.259 | 8.241 | 7.891 | 8.573 | 0.341 | 14804 | 20260523T223936581097Z | 2026-05-23T22:39:36.581097+00:00 |
| local-spark-sql-optimized-m4 | 14m | 14000000 | delay_by_airport_month_all_causes | Spark SQL | 3 | 4.904 | 4.887 | 4.815 | 4.943 | 0.065 | 46745 | 20260523T223936581097Z | 2026-05-23T22:39:36.581097+00:00 |
