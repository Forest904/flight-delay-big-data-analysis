# Data Preparation Notes

This document records the measured facts gathered before building the cleaning
pipeline. M2 is inspection only; transformations and cleaning rules are planned
for M3.

## Raw Dataset Source

- Source: Kaggle, `hrishitpatil/flight-data-2024`
- Local file: `data/raw/flight_data_2024.csv`
- Config path: `config/local.yaml` -> `paths.raw_file`
- File size: `1,309,010,752` bytes
- Kaggle credentials: not used for this run because the CSV was downloaded
  manually and placed in `data/raw/`
- Optional redownload instructions: `scripts/download_dataset.md`

## Inspection Command

Run the reproducible inspection from the project root:

```powershell
make inspect-raw
```

If `make` is not available on the local PATH, run the underlying command:

```powershell
.\.venv\Scripts\python.exe scripts\inspect_raw_dataset.py
```

## Raw Shape

- Row count: `7,079,081`
- Column count: `35`
- Header columns:

```text
year, month, day_of_month, day_of_week, fl_date, op_unique_carrier,
op_carrier_fl_num, origin, origin_city_name, origin_state_nm, dest,
dest_city_name, dest_state_nm, crs_dep_time, dep_time, dep_delay,
taxi_out, wheels_off, wheels_on, taxi_in, crs_arr_time, arr_time,
arr_delay, cancelled, cancellation_code, diverted, crs_elapsed_time,
actual_elapsed_time, air_time, distance, carrier_delay, weather_delay,
nas_delay, security_delay, late_aircraft_delay
```

## Inferred Raw Schema

| Column | Inferred type | Non-null rows |
|---|---:|---:|
| year | integer | 7,079,081 |
| month | integer | 7,079,081 |
| day_of_month | integer | 7,079,081 |
| day_of_week | integer | 7,079,081 |
| fl_date | date | 7,079,081 |
| op_unique_carrier | string | 7,079,081 |
| op_carrier_fl_num | float | 7,079,080 |
| origin | string | 7,079,081 |
| origin_city_name | string | 7,079,081 |
| origin_state_nm | string | 7,079,081 |
| dest | string | 7,079,081 |
| dest_city_name | string | 7,079,081 |
| dest_state_nm | string | 7,079,081 |
| crs_dep_time | integer | 7,079,081 |
| dep_time | float | 6,986,422 |
| dep_delay | float | 6,986,111 |
| taxi_out | float | 6,983,347 |
| wheels_off | float | 6,983,347 |
| wheels_on | float | 6,981,225 |
| taxi_in | float | 6,981,225 |
| crs_arr_time | integer | 7,079,081 |
| arr_time | float | 6,981,227 |
| arr_delay | float | 6,965,267 |
| cancelled | integer | 7,079,081 |
| cancellation_code | string | 96,315 |
| diverted | integer | 7,079,081 |
| crs_elapsed_time | float | 7,079,080 |
| actual_elapsed_time | float | 6,965,267 |
| air_time | float | 6,965,267 |
| distance | float | 7,079,081 |
| carrier_delay | integer | 7,079,081 |
| weather_delay | integer | 7,079,081 |
| nas_delay | integer | 7,079,081 |
| security_delay | integer | 7,079,081 |
| late_aircraft_delay | integer | 7,079,081 |

## Canonical Column Mapping

| Canonical column | Source column | Status |
|---|---|---|
| flight_date | fl_date | available |
| month | month | available |
| airline_code | op_unique_carrier | available |
| airline_name | N/A | unavailable in raw CSV |
| origin_airport | origin | available |
| destination_airport | dest | available |
| departure_delay | dep_delay | available |
| arrival_delay | arr_delay | available |
| cancelled | cancelled | available |
| diverted | diverted | available |
| cancellation_code | cancellation_code | available |
| carrier_delay | carrier_delay | available |
| weather_delay | weather_delay | available |
| nas_delay | nas_delay | available |
| security_delay | security_delay | available |
| late_aircraft_delay | late_aircraft_delay | available |

`airline_name` should be treated as unavailable unless a separate airline lookup
is added. Analyses should use `airline_code` as the airline identifier.

## Null Counts For Analysis-Critical Fields

| Canonical column | Source column | Null rows | Null percent |
|---|---|---:|---:|
| flight_date | fl_date | 0 | 0.0000 |
| month | month | 0 | 0.0000 |
| airline_code | op_unique_carrier | 0 | 0.0000 |
| airline_name | N/A | N/A | N/A |
| origin_airport | origin | 0 | 0.0000 |
| destination_airport | dest | 0 | 0.0000 |
| departure_delay | dep_delay | 92,970 | 1.3133 |
| arrival_delay | arr_delay | 113,814 | 1.6078 |
| cancelled | cancelled | 0 | 0.0000 |
| diverted | diverted | 0 | 0.0000 |
| cancellation_code | cancellation_code | 6,982,766 | 98.6394 |
| carrier_delay | carrier_delay | 0 | 0.0000 |
| weather_delay | weather_delay | 0 | 0.0000 |
| nas_delay | nas_delay | 0 | 0.0000 |
| security_delay | security_delay | 0 | 0.0000 |
| late_aircraft_delay | late_aircraft_delay | 0 | 0.0000 |

## Sample Observations

- The first records are January 2024 flights.
- Delay fields include negative values, which represent early departures or
  arrivals and should be preserved in M3.
- Non-cancelled rows commonly have an empty `cancellation_code`.
- Delay-cause fields are present and populated with zeroes when no cause is
  recorded.
- `cancelled` and `diverted` are numeric indicator fields.

## Git Ignore Confirmation

The raw CSV, data dictionary, and sample CSV are ignored by `.gitignore` under
`data/raw/*`; only `data/raw/.gitkeep` should be tracked.
