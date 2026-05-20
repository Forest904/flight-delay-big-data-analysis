| environment | input_label | records | job_name | Spark SQL duration_seconds | Spark Core duration_seconds | Hive duration_seconds |
| --- | --- | --- | --- | --- | --- | --- |
| docker-cluster | 100k | 100000 | airline_airport_ranking | 8.676 | 3.693 | 14.976 |
| docker-cluster | 100k | 100000 | delay_by_airport_month | 15.454 | 4.164 | 17.509 |
| docker-cluster | 1m | 1000000 | airline_airport_ranking | 7.54 | 3.702 | 14.15 |
| docker-cluster | 1m | 1000000 | delay_by_airport_month | 16.15 | 4.082 | 19.66 |
| local | 100k | 100000 | airline_airport_ranking | 1.842 | 0.765 | 14.831 |
| local | 100k | 100000 | delay_by_airport_month | 8.581 | 0.959 | 18.071 |
