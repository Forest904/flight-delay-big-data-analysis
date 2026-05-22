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
| local | 100k | 100000 | airline_airport_ranking | 1.854 | 8.447 | 15.664 |
| local | 100k | 100000 | delay_by_airport_month | 5.693 | 2.288 | 13.025 |
| local | 500k | 500000 | airline_airport_ranking | 1.864 | 7.985 | 14.881 |
| local | 500k | 500000 | delay_by_airport_month | 6.572 | 2.211 | 14.532 |
| local | 1m | 1000000 | airline_airport_ranking | 2.327 | 6.762 | 15.736 |
| local | 1m | 1000000 | delay_by_airport_month | 7.266 | 2.15 | 15.618 |
| local | 3m | 3000000 | airline_airport_ranking | 2.698 | 5.34 | 14.41 |
| local | 3m | 3000000 | delay_by_airport_month | 7.123 | 2.071 | 14.751 |
| local | full | 7079081 | airline_airport_ranking | 3.997 | 5.314 | 21.241 |
| local | full | 7079081 | delay_by_airport_month | 7.942 | 2.513 | 19.955 |
| local | 14m | 14000000 | airline_airport_ranking | 3.973 |  |  |
| local | 14m | 14000000 | delay_by_airport_month | 8.939 |  |  |
