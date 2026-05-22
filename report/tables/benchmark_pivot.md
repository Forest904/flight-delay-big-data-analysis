| environment | input_label | records | job_name | Spark SQL median_duration_seconds | Spark Core median_duration_seconds | Hive median_duration_seconds |
| --- | --- | --- | --- | --- | --- | --- |
| aws-emr | 100k | 100000 | airline_airport_ranking | 3.984 | 1.213 |  |
| aws-emr | 100k | 100000 | delay_by_airport_month | 15.832 | 1.864 |  |
| aws-emr | 500k | 500000 | airline_airport_ranking | 4.179 | 1.205 |  |
| aws-emr | 500k | 500000 | delay_by_airport_month | 13.879 | 1.706 |  |
| aws-emr | 1m | 1000000 | airline_airport_ranking | 4.052 | 1.243 |  |
| aws-emr | 1m | 1000000 | delay_by_airport_month | 15.126 | 1.923 |  |
| aws-emr | 3m | 3000000 | airline_airport_ranking | 4.457 | 1.249 |  |
| aws-emr | 3m | 3000000 | delay_by_airport_month | 14.582 | 2.02 |  |
| aws-emr | full | 7079081 | airline_airport_ranking | 4.302 | 1.106 |  |
| aws-emr | full | 7079081 | delay_by_airport_month | 15.505 | 1.918 |  |
| aws-emr | 14m | 14000000 | airline_airport_ranking | 6.056 | 1.235 |  |
| aws-emr | 14m | 14000000 | delay_by_airport_month | 18.147 | 2.061 |  |
| docker-simulation | 100k | 100000 | airline_airport_ranking | 4.01 | 2.325 | 8.983 |
| docker-simulation | 100k | 100000 | delay_by_airport_month | 9.385 | 2.543 | 12.025 |
| docker-simulation | 500k | 500000 | airline_airport_ranking | 5.617 | 2.434 | 8.972 |
| docker-simulation | 500k | 500000 | delay_by_airport_month | 9.978 | 2.623 | 12.619 |
| docker-simulation | 1m | 1000000 | airline_airport_ranking | 4.444 | 2.334 | 8.901 |
| docker-simulation | 1m | 1000000 | delay_by_airport_month | 10.921 | 2.619 | 12.584 |
| local | 14m | 14000000 | airline_airport_ranking | 2.241 | 0.564 |  |
| local | 14m | 14000000 | delay_by_airport_month | 7.68 | 0.859 |  |
