ifeq ($(OS),Windows_NT)
PYTHON_LAUNCHER := py -3.12
VENV_PYTHON := .venv/Scripts/python.exe
FAIL := exit /B 1
DOCKER_BIN_DIR := C:\Program Files\Docker\Docker\resources\bin
DOCKER ?= "$(DOCKER_BIN_DIR)\docker.exe"
DOCKER_COMPOSE := set "PATH=$(DOCKER_BIN_DIR);%PATH%" && $(DOCKER) compose
else
PYTHON_LAUNCHER := python3.12
VENV_PYTHON := .venv/bin/python
FAIL := exit 1
DOCKER ?= docker
DOCKER_COMPOSE := $(DOCKER) compose
endif

GENERATE_SIZE_FLAGS :=
CLUSTER_INPUT_LABEL ?= 100k
ifeq ($(FORCE),1)
GENERATE_SIZE_FLAGS += --force
endif
ifeq ($(GENERATE_LARGE),1)
GENERATE_SIZE_FLAGS += --include-large
endif

.PHONY: setup check-env inspect-raw prepare generate-sizes run-spark-sql run-spark-core run-spark-core-native run-spark-core-docker run-hive stop-hive run-all-local benchmark-local benchmark-cluster charts report clean

setup:
	$(PYTHON_LAUNCHER) -m venv .venv
	$(VENV_PYTHON) -m pip install --upgrade pip
	$(VENV_PYTHON) -m pip install -r requirements.txt

check-env:
	$(VENV_PYTHON) scripts/check_env.py

inspect-raw:
	$(VENV_PYTHON) scripts/inspect_raw_dataset.py

prepare:
	$(VENV_PYTHON) src/preparation/prepare_spark.py

generate-sizes:
	$(VENV_PYTHON) src/preparation/generate_input_sizes.py $(GENERATE_SIZE_FLAGS)

benchmark-local:
	$(VENV_PYTHON) experiments/run_benchmarks.py --environment local $(BENCHMARK_FLAGS)

benchmark-cluster:
	$(DOCKER_COMPOSE) up -d --build spark-master spark-worker-1 spark-worker-2 spark-driver
	$(VENV_PYTHON) experiments/run_benchmarks.py --config config/cluster.yaml --environment docker-cluster --input-label $(CLUSTER_INPUT_LABEL) $(BENCHMARK_FLAGS)

run-spark-sql:
	$(VENV_PYTHON) src/spark_sql/run_spark_sql.py

ifeq ($(OS),Windows_NT)
run-spark-core: run-spark-core-docker
else
run-spark-core: run-spark-core-native
endif

run-spark-core-native:
	$(VENV_PYTHON) src/spark_core/run_spark_core.py

run-spark-core-docker:
	$(DOCKER_COMPOSE) run --rm spark-core

run-hive:
	$(VENV_PYTHON) src/hive/run_hive.py

stop-hive:
	$(DOCKER_COMPOSE) stop hiveserver2 hive-metastore hive-postgres

charts:
	$(VENV_PYTHON) scripts/generate_charts.py

report:
	$(VENV_PYTHON) scripts/build_report.py

run-all-local:
	@echo Target "$@" is not implemented yet. This milestone only sets up the project foundation.
	@$(FAIL)

clean:
	@echo Target "clean" is not implemented yet. This milestone does not remove generated artifacts.
	@$(FAIL)
