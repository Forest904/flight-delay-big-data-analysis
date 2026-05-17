ifeq ($(OS),Windows_NT)
PYTHON_LAUNCHER := py -3.12
VENV_PYTHON := .venv/Scripts/python.exe
FAIL := exit /B 1
else
PYTHON_LAUNCHER := python3.12
VENV_PYTHON := .venv/bin/python
FAIL := exit 1
endif

.PHONY: setup check-env prepare generate-sizes run-spark-sql run-spark-core run-hive run-all-local benchmark-local benchmark-cluster charts report clean

setup:
	$(PYTHON_LAUNCHER) -m venv .venv
	$(VENV_PYTHON) -m pip install --upgrade pip
	$(VENV_PYTHON) -m pip install -r requirements.txt

check-env:
	$(VENV_PYTHON) scripts/check_env.py

prepare generate-sizes run-spark-sql run-spark-core run-hive run-all-local benchmark-local benchmark-cluster charts report:
	@echo Target "$@" is not implemented yet. This milestone only sets up the project foundation.
	@$(FAIL)

clean:
	@echo Target "clean" is not implemented yet. This milestone does not remove generated artifacts.
	@$(FAIL)
