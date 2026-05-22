| environment | input_label | records | job_name | technology | median_duration_vs_100k | records_vs_100k | throughput_vs_100k |
| --- | --- | --- | --- | --- | --- | --- | --- |
| aws-emr | 100k | 100000 | airline_airport_ranking | Spark Core | 1 | 1 | 1 |
| aws-emr | 500k | 500000 | airline_airport_ranking | Spark Core | 0.993 | 5 | 5.035 |
| aws-emr | 1m | 1000000 | airline_airport_ranking | Spark Core | 1.025 | 10 | 9.761 |
| aws-emr | 3m | 3000000 | airline_airport_ranking | Spark Core | 1.029 | 30 | 29.152 |
| aws-emr | full | 7079081 | airline_airport_ranking | Spark Core | 0.912 | 70.791 | 77.626 |
| aws-emr | 14m | 14000000 | airline_airport_ranking | Spark Core | 1.018 | 140 | 137.545 |
| aws-emr | 100k | 100000 | airline_airport_ranking | Spark SQL | 1 | 1 | 1 |
| aws-emr | 500k | 500000 | airline_airport_ranking | Spark SQL | 1.049 | 5 | 4.767 |
| aws-emr | 1m | 1000000 | airline_airport_ranking | Spark SQL | 1.017 | 10 | 9.833 |
| aws-emr | 3m | 3000000 | airline_airport_ranking | Spark SQL | 1.119 | 30 | 26.817 |
| aws-emr | full | 7079081 | airline_airport_ranking | Spark SQL | 1.08 | 70.791 | 65.56 |
| aws-emr | 14m | 14000000 | airline_airport_ranking | Spark SQL | 1.52 | 140 | 92.098 |
| aws-emr | 100k | 100000 | delay_by_airport_month | Spark Core | 1 | 1 | 1 |
| aws-emr | 500k | 500000 | delay_by_airport_month | Spark Core | 0.915 | 5 | 5.463 |
| aws-emr | 1m | 1000000 | delay_by_airport_month | Spark Core | 1.032 | 10 | 9.694 |
| aws-emr | 3m | 3000000 | delay_by_airport_month | Spark Core | 1.084 | 30 | 27.688 |
| aws-emr | full | 7079081 | delay_by_airport_month | Spark Core | 1.029 | 70.791 | 68.803 |
| aws-emr | 14m | 14000000 | delay_by_airport_month | Spark Core | 1.106 | 140 | 126.631 |
| aws-emr | 100k | 100000 | delay_by_airport_month | Spark SQL | 1 | 1 | 1 |
| aws-emr | 500k | 500000 | delay_by_airport_month | Spark SQL | 0.877 | 5 | 5.703 |
| aws-emr | 1m | 1000000 | delay_by_airport_month | Spark SQL | 0.955 | 10 | 10.467 |
| aws-emr | 3m | 3000000 | delay_by_airport_month | Spark SQL | 0.921 | 30 | 32.57 |
| aws-emr | full | 7079081 | delay_by_airport_month | Spark SQL | 0.979 | 70.791 | 72.28 |
| aws-emr | 14m | 14000000 | delay_by_airport_month | Spark SQL | 1.146 | 140 | 122.138 |
| docker-simulation | 100k | 100000 | airline_airport_ranking | Hive | 1 | 1 | 1 |
| docker-simulation | 500k | 500000 | airline_airport_ranking | Hive | 0.999 | 5 | 5.006 |
| docker-simulation | 1m | 1000000 | airline_airport_ranking | Hive | 0.991 | 10 | 10.093 |
| docker-simulation | 100k | 100000 | airline_airport_ranking | Spark Core | 1 | 1 | 1 |
| docker-simulation | 500k | 500000 | airline_airport_ranking | Spark Core | 1.047 | 5 | 4.776 |
| docker-simulation | 1m | 1000000 | airline_airport_ranking | Spark Core | 1.004 | 10 | 9.961 |
| docker-simulation | 100k | 100000 | airline_airport_ranking | Spark SQL | 1 | 1 | 1 |
| docker-simulation | 500k | 500000 | airline_airport_ranking | Spark SQL | 1.401 | 5 | 3.569 |
| docker-simulation | 1m | 1000000 | airline_airport_ranking | Spark SQL | 1.108 | 10 | 9.023 |
| docker-simulation | 100k | 100000 | delay_by_airport_month | Hive | 1 | 1 | 1 |
| docker-simulation | 500k | 500000 | delay_by_airport_month | Hive | 1.049 | 5 | 4.765 |
| docker-simulation | 1m | 1000000 | delay_by_airport_month | Hive | 1.046 | 10 | 9.556 |
| docker-simulation | 100k | 100000 | delay_by_airport_month | Spark Core | 1 | 1 | 1 |
| docker-simulation | 500k | 500000 | delay_by_airport_month | Spark Core | 1.031 | 5 | 4.847 |
| docker-simulation | 1m | 1000000 | delay_by_airport_month | Spark Core | 1.03 | 10 | 9.707 |
| docker-simulation | 100k | 100000 | delay_by_airport_month | Spark SQL | 1 | 1 | 1 |
| docker-simulation | 500k | 500000 | delay_by_airport_month | Spark SQL | 1.063 | 5 | 4.703 |
| docker-simulation | 1m | 1000000 | delay_by_airport_month | Spark SQL | 1.164 | 10 | 8.594 |
| local | 100k | 100000 | airline_airport_ranking | Hive | 1 | 1 | 1 |
| local | 500k | 500000 | airline_airport_ranking | Hive | 0.988 | 5 | 5.063 |
| local | 1m | 1000000 | airline_airport_ranking | Hive | 0.993 | 10 | 10.071 |
| local | 3m | 3000000 | airline_airport_ranking | Hive | 0.993 | 30 | 30.21 |
| local | full | 7079081 | airline_airport_ranking | Hive | 1.388 | 70.791 | 51.018 |
| local | 100k | 100000 | airline_airport_ranking | Spark Core | 1 | 1 | 1 |
| local | 500k | 500000 | airline_airport_ranking | Spark Core | 1.04 | 5 | 4.81 |
| local | 1m | 1000000 | airline_airport_ranking | Spark Core | 0.988 | 10 | 10.118 |
| local | 3m | 3000000 | airline_airport_ranking | Spark Core | 1.079 | 30 | 27.792 |
| local | full | 7079081 | airline_airport_ranking | Spark Core | 1.023 | 70.791 | 69.185 |
| local | 14m | 14000000 | airline_airport_ranking | Spark Core | 0.99 | 140 | 141.432 |
| local | 100k | 100000 | airline_airport_ranking | Spark SQL | 1 | 1 | 1 |
| local | 500k | 500000 | airline_airport_ranking | Spark SQL | 1.045 | 5 | 4.786 |
| local | 1m | 1000000 | airline_airport_ranking | Spark SQL | 1.24 | 10 | 8.062 |
| local | 3m | 3000000 | airline_airport_ranking | Spark SQL | 1.571 | 30 | 19.099 |
| local | full | 7079081 | airline_airport_ranking | Spark SQL | 2.206 | 70.791 | 32.097 |
| local | 14m | 14000000 | airline_airport_ranking | Spark SQL | 2.121 | 140 | 66.005 |
| local | 100k | 100000 | delay_by_airport_month | Hive | 1 | 1 | 1 |
| local | 500k | 500000 | delay_by_airport_month | Hive | 1.064 | 5 | 4.701 |
| local | 1m | 1000000 | delay_by_airport_month | Hive | 1.063 | 10 | 9.408 |
| local | 3m | 3000000 | delay_by_airport_month | Hive | 1.156 | 30 | 25.945 |
| local | full | 7079081 | delay_by_airport_month | Hive | 1.609 | 70.791 | 43.995 |
| local | 100k | 100000 | delay_by_airport_month | Spark Core | 1 | 1 | 1 |
| local | 500k | 500000 | delay_by_airport_month | Spark Core | 0.953 | 5 | 5.244 |
| local | 1m | 1000000 | delay_by_airport_month | Spark Core | 0.886 | 10 | 11.281 |
| local | 3m | 3000000 | delay_by_airport_month | Spark Core | 1.021 | 30 | 29.384 |
| local | full | 7079081 | delay_by_airport_month | Spark Core | 1.05 | 70.791 | 67.404 |
| local | 14m | 14000000 | delay_by_airport_month | Spark Core | 0.938 | 140 | 149.289 |
| local | 100k | 100000 | delay_by_airport_month | Spark SQL | 1 | 1 | 1 |
| local | 500k | 500000 | delay_by_airport_month | Spark SQL | 1.101 | 5 | 4.542 |
| local | 1m | 1000000 | delay_by_airport_month | Spark SQL | 1.131 | 10 | 8.838 |
| local | 3m | 3000000 | delay_by_airport_month | Spark SQL | 1.278 | 30 | 23.483 |
| local | full | 7079081 | delay_by_airport_month | Spark SQL | 1.465 | 70.791 | 48.313 |
| local | 14m | 14000000 | delay_by_airport_month | Spark SQL | 1.473 | 140 | 95.072 |
