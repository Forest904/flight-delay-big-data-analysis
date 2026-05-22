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
| docker-simulation | 500k | 500000 | airline_airport_ranking | Hive | 0.991 | 5 | 5.043 |
| docker-simulation | 1m | 1000000 | airline_airport_ranking | Hive | 0.552 | 10 | 18.118 |
| docker-simulation | 100k | 100000 | airline_airport_ranking | Spark Core | 1 | 1 | 1 |
| docker-simulation | 500k | 500000 | airline_airport_ranking | Spark Core | 0.961 | 5 | 5.2 |
| docker-simulation | 1m | 1000000 | airline_airport_ranking | Spark Core | 0.49 | 10 | 20.415 |
| docker-simulation | 100k | 100000 | airline_airport_ranking | Spark SQL | 1 | 1 | 1 |
| docker-simulation | 500k | 500000 | airline_airport_ranking | Spark SQL | 0.988 | 5 | 5.059 |
| docker-simulation | 1m | 1000000 | airline_airport_ranking | Spark SQL | 0.463 | 10 | 21.615 |
| docker-simulation | 100k | 100000 | delay_by_airport_month | Hive | 1 | 1 | 1 |
| docker-simulation | 500k | 500000 | delay_by_airport_month | Hive | 1.013 | 5 | 4.936 |
| docker-simulation | 1m | 1000000 | delay_by_airport_month | Hive | 0.603 | 10 | 16.579 |
| docker-simulation | 100k | 100000 | delay_by_airport_month | Spark Core | 1 | 1 | 1 |
| docker-simulation | 500k | 500000 | delay_by_airport_month | Spark Core | 1.043 | 5 | 4.792 |
| docker-simulation | 1m | 1000000 | delay_by_airport_month | Spark Core | 0.528 | 10 | 18.934 |
| docker-simulation | 100k | 100000 | delay_by_airport_month | Spark SQL | 1 | 1 | 1 |
| docker-simulation | 500k | 500000 | delay_by_airport_month | Spark SQL | 1.081 | 5 | 4.626 |
| docker-simulation | 1m | 1000000 | delay_by_airport_month | Spark SQL | 0.614 | 10 | 16.292 |
| local | 100k | 100000 | airline_airport_ranking | Hive | 1 | 1 | 1 |
| local | 500k | 500000 | airline_airport_ranking | Hive | 0.986 | 5 | 5.07 |
| local | 1m | 1000000 | airline_airport_ranking | Hive | 1.116 | 10 | 8.96 |
| local | 3m | 3000000 | airline_airport_ranking | Hive | 1.071 | 30 | 28.006 |
| local | full | 7079081 | airline_airport_ranking | Hive | 1.677 | 70.791 | 42.209 |
| local | 14m | 14000000 | airline_airport_ranking | Hive | 1.87 | 140 | 74.873 |
| local | 28m | 28000000 | airline_airport_ranking | Hive | 4.646 | 280 | 60.266 |
| local | 100k | 100000 | airline_airport_ranking | Spark Core | 1 | 1 | 1 |
| local | 500k | 500000 | airline_airport_ranking | Spark Core | 1.059 | 5 | 4.723 |
| local | 1m | 1000000 | airline_airport_ranking | Spark Core | 1.075 | 10 | 9.3 |
| local | 3m | 3000000 | airline_airport_ranking | Spark Core | 0.986 | 30 | 30.417 |
| local | full | 7079081 | airline_airport_ranking | Spark Core | 1.061 | 70.791 | 66.727 |
| local | 14m | 14000000 | airline_airport_ranking | Spark Core | 1.07 | 140 | 130.877 |
| local | 28m | 28000000 | airline_airport_ranking | Spark Core | 1.122 | 280 | 249.594 |
| local | 100k | 100000 | airline_airport_ranking | Spark SQL | 1 | 1 | 1 |
| local | 500k | 500000 | airline_airport_ranking | Spark SQL | 1.062 | 5 | 4.708 |
| local | 1m | 1000000 | airline_airport_ranking | Spark SQL | 1.433 | 10 | 6.977 |
| local | 3m | 3000000 | airline_airport_ranking | Spark SQL | 1.783 | 30 | 16.826 |
| local | full | 7079081 | airline_airport_ranking | Spark SQL | 1.949 | 70.791 | 36.324 |
| local | 14m | 14000000 | airline_airport_ranking | Spark SQL | 1.9 | 140 | 73.696 |
| local | 28m | 28000000 | airline_airport_ranking | Spark SQL | 1.934 | 280 | 144.813 |
| local | 100k | 100000 | delay_by_airport_month | Hive | 1 | 1 | 1 |
| local | 500k | 500000 | delay_by_airport_month | Hive | 1.059 | 5 | 4.723 |
| local | 1m | 1000000 | delay_by_airport_month | Hive | 1.13 | 10 | 8.853 |
| local | 3m | 3000000 | delay_by_airport_month | Hive | 1.263 | 30 | 23.744 |
| local | full | 7079081 | delay_by_airport_month | Hive | 1.764 | 70.791 | 40.125 |
| local | 14m | 14000000 | delay_by_airport_month | Hive | 2.072 | 140 | 67.566 |
| local | 28m | 28000000 | delay_by_airport_month | Hive | 5.104 | 280 | 54.861 |
| local | 100k | 100000 | delay_by_airport_month | Spark Core | 1 | 1 | 1 |
| local | 500k | 500000 | delay_by_airport_month | Spark Core | 1.12 | 5 | 4.463 |
| local | 1m | 1000000 | delay_by_airport_month | Spark Core | 1.193 | 10 | 8.379 |
| local | 3m | 3000000 | delay_by_airport_month | Spark Core | 1.125 | 30 | 26.678 |
| local | full | 7079081 | delay_by_airport_month | Spark Core | 1.219 | 70.791 | 58.061 |
| local | 14m | 14000000 | delay_by_airport_month | Spark Core | 1.221 | 140 | 114.664 |
| local | 28m | 28000000 | delay_by_airport_month | Spark Core | 1.331 | 280 | 210.444 |
| local | 100k | 100000 | delay_by_airport_month | Spark SQL | 1 | 1 | 1 |
| local | 500k | 500000 | delay_by_airport_month | Spark SQL | 1.089 | 5 | 4.591 |
| local | 1m | 1000000 | delay_by_airport_month | Spark SQL | 1.529 | 10 | 6.539 |
| local | 3m | 3000000 | delay_by_airport_month | Spark SQL | 1.643 | 30 | 18.256 |
| local | full | 7079081 | delay_by_airport_month | Spark SQL | 1.632 | 70.791 | 43.387 |
| local | 14m | 14000000 | delay_by_airport_month | Spark SQL | 1.49 | 140 | 93.972 |
| local | 28m | 28000000 | delay_by_airport_month | Spark SQL | 1.497 | 280 | 187.062 |
