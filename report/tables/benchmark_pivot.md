| environment | input_label | records | job_name | Spark SQL median_duration_seconds | Spark Core median_duration_seconds | Hive median_duration_seconds | MapReduce median_duration_seconds |
| --- | --- | --- | --- | --- | --- | --- | --- |
| aws-emr | 100k | 100000 | airline_airport_ranking | 3.984 | 1.213 |  |  |
| aws-emr | 100k | 100000 | delay_by_airport_month | 15.832 | 1.864 |  |  |
| aws-emr | 500k | 500000 | airline_airport_ranking | 4.179 | 1.205 |  |  |
| aws-emr | 500k | 500000 | delay_by_airport_month | 13.879 | 1.706 |  |  |
| aws-emr | 1m | 1000000 | airline_airport_ranking | 4.052 | 1.243 |  |  |
| aws-emr | 1m | 1000000 | delay_by_airport_month | 15.126 | 1.923 |  |  |
| aws-emr | 3m | 3000000 | airline_airport_ranking | 4.457 | 1.249 |  |  |
| aws-emr | 3m | 3000000 | delay_by_airport_month | 14.582 | 2.02 |  |  |
| aws-emr | full | 7079081 | airline_airport_ranking | 4.302 | 1.106 |  |  |
| aws-emr | full | 7079081 | delay_by_airport_month | 15.505 | 1.918 |  |  |
| aws-emr | 14m | 14000000 | airline_airport_ranking | 6.056 | 1.235 |  |  |
| aws-emr | 14m | 14000000 | delay_by_airport_month | 18.147 | 2.061 |  |  |
| aws-emr-larger | 1m | 1000000 | airline_airport_ranking | 4.087 | 1.018 |  |  |
| aws-emr-larger | 1m | 1000000 | delay_by_airport_month | 14.374 | 1.679 |  |  |
| aws-emr-larger | full | 7079081 | airline_airport_ranking | 4.475 | 0.919 |  |  |
| aws-emr-larger | full | 7079081 | delay_by_airport_month | 16.309 | 1.65 |  |  |
| docker-simulation | 100k | 100000 | airline_airport_ranking | 12.685 | 6.214 | 18.288 |  |
| docker-simulation | 100k | 100000 | delay_by_airport_month | 23.69 | 6.954 | 27.848 |  |
| docker-simulation | 500k | 500000 | airline_airport_ranking | 12.537 | 5.974 | 18.131 |  |
| docker-simulation | 500k | 500000 | delay_by_airport_month | 25.606 | 7.256 | 28.206 |  |
| docker-simulation | 1m | 1000000 | airline_airport_ranking | 5.869 | 3.044 | 10.094 |  |
| docker-simulation | 1m | 1000000 | delay_by_airport_month | 14.541 | 3.673 | 16.797 |  |
| local | 100k | 100000 | airline_airport_ranking | 1.744 | 0.74 | 14.322 | 6.708 |
| local | 100k | 100000 | delay_by_airport_month | 7.966 | 1.002 | 19.841 | 7.644 |
| local | 500k | 500000 | airline_airport_ranking | 1.853 | 0.783 | 14.125 | 20.328 |
| local | 500k | 500000 | delay_by_airport_month | 8.675 | 1.122 | 21.005 | 23.3 |
| local | 1m | 1000000 | airline_airport_ranking | 2.5 | 0.796 | 15.984 | 37.887 |
| local | 1m | 1000000 | delay_by_airport_month | 12.181 | 1.195 | 22.411 | 40.762 |
| local | 3m | 3000000 | airline_airport_ranking | 3.11 | 0.73 | 15.341 | 105.491 |
| local | 3m | 3000000 | delay_by_airport_month | 13.09 | 1.126 | 25.069 | 116.11 |
| local | full | 7079081 | airline_airport_ranking | 3.4 | 0.785 | 24.02 | 249.968 |
| local | full | 7079081 | delay_by_airport_month | 12.997 | 1.221 | 35.005 | 267.284 |
| local | 14m | 14000000 | airline_airport_ranking | 3.314 | 0.792 | 26.78 |  |
| local | 14m | 14000000 | delay_by_airport_month | 11.868 | 1.223 | 41.112 |  |
| local | 28m | 28000000 | airline_airport_ranking | 3.373 | 0.83 | 66.541 |  |
| local | 28m | 28000000 | delay_by_airport_month | 11.924 | 1.333 | 101.265 |  |
