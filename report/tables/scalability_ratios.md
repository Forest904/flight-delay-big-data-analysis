| environment | input_label | records | job_name | technology | duration_vs_100k | records_vs_100k | throughput_vs_100k |
| --- | --- | --- | --- | --- | --- | --- | --- |
| docker-simulation | 100k | 100000 | airline_airport_ranking | Hive | 1 | 1 | 1 |
| docker-simulation | 500k | 500000 | airline_airport_ranking | Hive | 0.978 | 5 | 5.113 |
| docker-simulation | 1m | 1000000 | airline_airport_ranking | Hive | 0.967 | 10 | 10.338 |
| docker-simulation | 100k | 100000 | airline_airport_ranking | Spark Core | 1 | 1 | 1 |
| docker-simulation | 500k | 500000 | airline_airport_ranking | Spark Core | 1.02 | 5 | 4.902 |
| docker-simulation | 1m | 1000000 | airline_airport_ranking | Spark Core | 0.984 | 10 | 10.168 |
| docker-simulation | 100k | 100000 | airline_airport_ranking | Spark SQL | 1 | 1 | 1 |
| docker-simulation | 500k | 500000 | airline_airport_ranking | Spark SQL | 1.005 | 5 | 4.973 |
| docker-simulation | 1m | 1000000 | airline_airport_ranking | Spark SQL | 0.76 | 10 | 13.161 |
| docker-simulation | 100k | 100000 | delay_by_airport_month | Hive | 1 | 1 | 1 |
| docker-simulation | 500k | 500000 | delay_by_airport_month | Hive | 0.982 | 5 | 5.092 |
| docker-simulation | 1m | 1000000 | delay_by_airport_month | Hive | 1.062 | 10 | 9.415 |
| docker-simulation | 100k | 100000 | delay_by_airport_month | Spark Core | 1 | 1 | 1 |
| docker-simulation | 500k | 500000 | delay_by_airport_month | Spark Core | 1.05 | 5 | 4.763 |
| docker-simulation | 1m | 1000000 | delay_by_airport_month | Spark Core | 1.106 | 10 | 9.043 |
| docker-simulation | 100k | 100000 | delay_by_airport_month | Spark SQL | 1 | 1 | 1 |
| docker-simulation | 500k | 500000 | delay_by_airport_month | Spark SQL | 0.974 | 5 | 5.133 |
| docker-simulation | 1m | 1000000 | delay_by_airport_month | Spark SQL | 0.909 | 10 | 11 |
| local | 100k | 100000 | airline_airport_ranking | Hive | 1 | 1 | 1 |
| local | 500k | 500000 | airline_airport_ranking | Hive | 1.012 | 5 | 4.94 |
| local | 1m | 1000000 | airline_airport_ranking | Hive | 0.998 | 10 | 10.023 |
| local | 3m | 3000000 | airline_airport_ranking | Hive | 1.35 | 30 | 22.221 |
| local | full | 7079081 | airline_airport_ranking | Hive | 1.412 | 70.791 | 50.131 |
| local | 100k | 100000 | airline_airport_ranking | Spark Core | 1 | 1 | 1 |
| local | 500k | 500000 | airline_airport_ranking | Spark Core | 1.027 | 5 | 4.868 |
| local | 1m | 1000000 | airline_airport_ranking | Spark Core | 1.132 | 10 | 8.832 |
| local | 3m | 3000000 | airline_airport_ranking | Spark Core | 1.1 | 30 | 27.276 |
| local | full | 7079081 | airline_airport_ranking | Spark Core | 1.074 | 70.791 | 65.902 |
| local | 100k | 100000 | airline_airport_ranking | Spark SQL | 1 | 1 | 1 |
| local | 500k | 500000 | airline_airport_ranking | Spark SQL | 1.155 | 5 | 4.329 |
| local | 1m | 1000000 | airline_airport_ranking | Spark SQL | 1.312 | 10 | 7.623 |
| local | 3m | 3000000 | airline_airport_ranking | Spark SQL | 1.705 | 30 | 17.591 |
| local | full | 7079081 | airline_airport_ranking | Spark SQL | 1.708 | 70.791 | 41.451 |
| local | 100k | 100000 | delay_by_airport_month | Hive | 1 | 1 | 1 |
| local | 500k | 500000 | delay_by_airport_month | Hive | 1.07 | 5 | 4.671 |
| local | 1m | 1000000 | delay_by_airport_month | Hive | 1.077 | 10 | 9.282 |
| local | 3m | 3000000 | delay_by_airport_month | Hive | 1.22 | 30 | 24.597 |
| local | full | 7079081 | delay_by_airport_month | Hive | 1.646 | 70.791 | 43.002 |
| local | 100k | 100000 | delay_by_airport_month | Spark Core | 1 | 1 | 1 |
| local | 500k | 500000 | delay_by_airport_month | Spark Core | 1.07 | 5 | 4.674 |
| local | 1m | 1000000 | delay_by_airport_month | Spark Core | 1.203 | 10 | 8.315 |
| local | 3m | 3000000 | delay_by_airport_month | Spark Core | 1.342 | 30 | 22.359 |
| local | full | 7079081 | delay_by_airport_month | Spark Core | 1.26 | 70.791 | 56.2 |
| local | 100k | 100000 | delay_by_airport_month | Spark SQL | 1 | 1 | 1 |
| local | 500k | 500000 | delay_by_airport_month | Spark SQL | 1.075 | 5 | 4.653 |
| local | 1m | 1000000 | delay_by_airport_month | Spark SQL | 1.258 | 10 | 7.947 |
| local | 3m | 3000000 | delay_by_airport_month | Spark SQL | 1.38 | 30 | 21.737 |
| local | full | 7079081 | delay_by_airport_month | Spark SQL | 1.36 | 70.791 | 52.051 |
