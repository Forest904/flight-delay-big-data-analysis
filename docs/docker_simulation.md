# Docker Standalone Simulation

This document records the Docker standalone simulation. The goal is to add
execution-setting evidence without overclaiming that a laptop Docker Compose
setup is equivalent to a future remote execution service.

## Topology

The Spark simulation uses standalone Spark services in `docker-compose.yml`:

- `spark-master`: Spark standalone master at `spark://spark-master:7077`.
- `spark-worker-1`: Spark worker with 2 cores and 2 GB memory.
- `spark-worker-2`: Spark worker with 2 cores and 2 GB memory.
- `spark-driver`: stable Python driver container used by the benchmark runner.

All Spark containers reuse the project Python/Spark image from
`Dockerfile.spark-core`. The PySpark package provides the `spark-class` command
used to start the standalone master and workers, so the project does not need a
second Spark distribution image.

The Docker simulation config is `config/docker_simulation.yaml`. It sets the Spark master to
`spark://spark-master:7077`, configures the driver host as `spark-driver`, and
keeps benchmark results under `experiments/results/docker-simulation/`.

## Hive Scope

Hive is included in `make benchmark-docker-simulation` so the benchmark CSV still contains
rows for all three required technologies. Its execution remains the Docker
Hive stack:

- `hiveserver2`
- `hive-metastore`
- `hive-postgres`

This is a single-node containerized Hive setup without HDFS and YARN. The final
report should describe Hive Docker evidence as a
limitation, while still using the Docker run as controlled execution-setting
evidence.

## Command

Run the Docker simulation benchmark matrix with:

```powershell
make benchmark-docker-simulation
```

The target starts the Spark master, workers, and driver, then runs:

```powershell
.\.venv\Scripts\python.exe experiments\run_benchmarks.py --config config\docker_simulation.yaml --environment docker-simulation
```

Additional benchmark flags can be passed through `BENCHMARK_FLAGS`. For example:

```powershell
make benchmark-docker-simulation BENCHMARK_FLAGS="--technology spark_sql"
```

The default M2 simulation matrix is `100k`, `500k`, and `1m`. Use
`BENCHMARK_FLAGS` to run a narrower configured and validated input:

```powershell
make benchmark-docker-simulation BENCHMARK_FLAGS="--input-label 1m"
```

## Results

Docker simulation benchmark evidence is written separately from local benchmark evidence:

```text
experiments/results/docker-simulation/
  benchmark_<YYYYMMDDTHHMMSSffffffZ>.csv
  benchmark_latest.csv
  logs/<run_id>/
```

Rows from this path use `environment=docker-simulation` and an execution-setting label
that identifies the Spark standalone topology plus Hive's single-node
containerized limitation.

## Limits

This simulation varies the execution setting, but it has important limits:

- All containers run on one physical machine.
- All services share Docker Desktop CPU, memory, and disk limits.
- Data is read from a bind-mounted local project directory, not HDFS or object
  storage.
- Spark worker separation is real at the container/process level, but not at
  the physical-machine level.
- Hive does not use a Hadoop execution service in this setup.

The report should use this evidence for cautious scalability discussion only.
It can compare local mode against Docker Spark standalone mode, but it should
not present the result as production remote-service performance.
