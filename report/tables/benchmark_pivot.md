| environment | input_label | records | job_name | Spark SQL duration_seconds | Spark Core duration_seconds | Hive duration_seconds | MapReduce duration_seconds |
| --- | --- | --- | --- | --- | --- | --- | --- |
| docker-simulation | 100k | 100000 | airline_airport_ranking | 4.01 | 2.325 | 8.983 |  |
| docker-simulation | 100k | 100000 | delay_by_airport_month | 9.385 | 2.543 | 12.025 |  |
| docker-simulation | 500k | 500000 | airline_airport_ranking | 5.617 | 2.434 | 8.972 |  |
| docker-simulation | 500k | 500000 | delay_by_airport_month | 9.978 | 2.623 | 12.619 |  |
| docker-simulation | 1m | 1000000 | airline_airport_ranking | 4.444 | 2.334 | 8.901 |  |
| docker-simulation | 1m | 1000000 | delay_by_airport_month | 10.921 | 2.619 | 12.584 |  |
| local | 100k | 100000 | airline_airport_ranking | 1.056 | 0.57 | 8.924 | 6.551 |
| local | 100k | 100000 | delay_by_airport_month | 5.215 | 0.916 | 11.932 | 7.49 |
| local | 500k | 500000 | airline_airport_ranking | 1.104 | 0.592 | 8.813 |  |
| local | 500k | 500000 | delay_by_airport_month | 5.74 | 0.873 | 12.692 |  |
| local | 1m | 1000000 | airline_airport_ranking | 1.31 | 0.563 | 8.861 |  |
| local | 1m | 1000000 | delay_by_airport_month | 5.901 | 0.812 | 12.683 |  |
| local | 3m | 3000000 | airline_airport_ranking | 1.659 | 0.615 | 8.861 |  |
| local | 3m | 3000000 | delay_by_airport_month | 6.662 | 0.935 | 13.797 |  |
| local | full | 7079081 | airline_airport_ranking | 2.33 | 0.583 | 12.382 |  |
| local | full | 7079081 | delay_by_airport_month | 7.641 | 0.962 | 19.2 |  |
