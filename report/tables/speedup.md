| environment | input_label | records | job_name | spark_sql_div_spark_core | hive_div_spark_sql | hive_div_spark_core |
| --- | --- | --- | --- | --- | --- | --- |
| aws-emr | 100k | 100000 | airline_airport_ranking | 3.283 |  |  |
| aws-emr | 100k | 100000 | delay_by_airport_month | 8.492 |  |  |
| aws-emr | 500k | 500000 | airline_airport_ranking | 3.468 |  |  |
| aws-emr | 500k | 500000 | delay_by_airport_month | 8.135 |  |  |
| aws-emr | 1m | 1000000 | airline_airport_ranking | 3.259 |  |  |
| aws-emr | 1m | 1000000 | delay_by_airport_month | 7.865 |  |  |
| aws-emr | 3m | 3000000 | airline_airport_ranking | 3.569 |  |  |
| aws-emr | 3m | 3000000 | delay_by_airport_month | 7.219 |  |  |
| aws-emr | full | 7079081 | airline_airport_ranking | 3.888 |  |  |
| aws-emr | full | 7079081 | delay_by_airport_month | 8.083 |  |  |
| aws-emr | 14m | 14000000 | airline_airport_ranking | 4.904 |  |  |
| aws-emr | 14m | 14000000 | delay_by_airport_month | 8.804 |  |  |
| aws-emr-larger | 1m | 1000000 | airline_airport_ranking | 4.014 |  |  |
| aws-emr-larger | 1m | 1000000 | delay_by_airport_month | 8.563 |  |  |
| aws-emr-larger | full | 7079081 | airline_airport_ranking | 4.872 |  |  |
| aws-emr-larger | full | 7079081 | delay_by_airport_month | 9.886 |  |  |
| docker-simulation | 100k | 100000 | airline_airport_ranking | 1.724 | 2.24 | 3.864 |
| docker-simulation | 100k | 100000 | delay_by_airport_month | 3.691 | 1.281 | 4.73 |
| docker-simulation | 500k | 500000 | airline_airport_ranking | 2.308 | 1.597 | 3.686 |
| docker-simulation | 500k | 500000 | delay_by_airport_month | 3.805 | 1.265 | 4.812 |
| docker-simulation | 1m | 1000000 | airline_airport_ranking | 1.904 | 2.003 | 3.813 |
| docker-simulation | 1m | 1000000 | delay_by_airport_month | 4.169 | 1.152 | 4.805 |
| local | 100k | 100000 | airline_airport_ranking | 2.357 | 8.21 | 19.354 |
| local | 100k | 100000 | delay_by_airport_month | 7.953 | 2.491 | 19.81 |
| local | 500k | 500000 | airline_airport_ranking | 2.365 | 7.625 | 18.03 |
| local | 500k | 500000 | delay_by_airport_month | 7.731 | 2.421 | 18.721 |
| local | 1m | 1000000 | airline_airport_ranking | 3.142 | 6.393 | 20.088 |
| local | 1m | 1000000 | delay_by_airport_month | 10.191 | 1.84 | 18.749 |
| local | 3m | 3000000 | airline_airport_ranking | 4.261 | 4.933 | 21.019 |
| local | 3m | 3000000 | delay_by_airport_month | 11.623 | 1.915 | 22.258 |
| local | full | 7079081 | airline_airport_ranking | 4.33 | 7.066 | 30.596 |
| local | full | 7079081 | delay_by_airport_month | 10.643 | 2.693 | 28.666 |
| local | 14m | 14000000 | airline_airport_ranking | 4.186 | 8.081 | 33.83 |
| local | 14m | 14000000 | delay_by_airport_month | 9.705 | 3.464 | 33.619 |
| local | 28m | 28000000 | airline_airport_ranking | 4.063 | 19.729 | 80.154 |
| local | 28m | 28000000 | delay_by_airport_month | 8.948 | 8.493 | 75.991 |
