| environment | input_label | records | job_name | Spark SQL duration_seconds | Spark Core duration_seconds | Hive duration_seconds | MapReduce duration_seconds |
| --- | --- | --- | --- | --- | --- | --- | --- |
| docker-simulation | 100k | 100000 | airline_airport_ranking | 5.136 | 2.148 | 9.189 |  |
| docker-simulation | 100k | 100000 | delay_by_airport_month | 9.642 | 2.386 | 12.267 |  |
| docker-simulation | 500k | 500000 | airline_airport_ranking | 5.164 | 2.191 | 8.986 |  |
| docker-simulation | 500k | 500000 | delay_by_airport_month | 9.393 | 2.505 | 12.046 |  |
| docker-simulation | 1m | 1000000 | airline_airport_ranking | 3.902 | 2.112 | 8.889 |  |
| docker-simulation | 1m | 1000000 | delay_by_airport_month | 8.765 | 2.638 | 13.03 |  |
| local | 100k | 100000 | airline_airport_ranking | 1.291 | 0.552 | 8.993 | 11.592 |
| local | 100k | 100000 | delay_by_airport_month | 6.666 | 0.713 | 12.075 | 13.194 |
| local | 500k | 500000 | airline_airport_ranking | 1.491 | 0.567 | 9.102 |  |
| local | 500k | 500000 | delay_by_airport_month | 7.164 | 0.763 | 12.926 |  |
| local | 1m | 1000000 | airline_airport_ranking | 1.693 | 0.624 | 8.972 |  |
| local | 1m | 1000000 | delay_by_airport_month | 8.388 | 0.857 | 13.009 |  |
| local | 3m | 3000000 | airline_airport_ranking | 2.201 | 0.607 | 12.141 |  |
| local | 3m | 3000000 | delay_by_airport_month | 9.2 | 0.957 | 14.728 |  |
| local | full | 7079081 | airline_airport_ranking | 2.204 | 0.592 | 12.699 |  |
| local | full | 7079081 | delay_by_airport_month | 9.066 | 0.898 | 19.878 |  |
