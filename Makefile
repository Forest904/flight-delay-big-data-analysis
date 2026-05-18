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

.PHONY: setup check-env inspect-raw prepare generate-sizes run-spark-sql run-spark-core run-spark-core-native run-spark-core-docker run-hive run-all-local benchmark-local benchmark-cluster charts report clean

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

generate-sizes run-hive run-all-local benchmark-local benchmark-cluster charts report:
	@echo Target "$@" is not implemented yet. This milestone only sets up the project foundation.
	@$(FAIL)

clean:
	@echo Target "clean" is not implemented yet. This milestone does not remove generated artifacts.
	@$(FAIL)
