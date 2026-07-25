# Define package manager, interpreter, and entrypoint
UV := uv
PYTHON := python3
ENTRYPOINT := new_simulation.py
map ?= default.txt

.PHONY: all install run debug clean lint lint-strict help

# Default target
all: help

## install: Install project dependencies using uv
install:
	$(UV) add pydantic flake8 mypy

## run: Execute the main simulation script with uv
run:
	$(UV) run $(PYTHON) $(ENTRYPOINT) $(map)

## debug: Run the main script under python's built-in debugger (pdb) using uv
debug:
	$(UV) run $(PYTHON) -m pdb $(ENTRYPOINT)

## clean: Remove cache directories, virtual environments, and temporary files
clean:
	rm -rf __pycache__ .mypy_cache .pytest_cache .venv
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

## lint: Execute mandatory linting tools using uv run
lint:
	$(UV) run flake8 . --exclude=.venv
	$(UV) run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

## lint-strict: Execute enhanced strict linting using uv run
lint-strict:
	$(UV) run flake8 . --exclude=.venv
	$(UV) run mypy . --strict

## help: Show available commands
help:
	@echo "Available rules:"
	@echo "  install      - Install required dependencies into the uv environment"
	@echo "  run          - Execute the main simulation script with uv run"
	@echo "  debug        - Run the main script under PDB debugger with uv run"
	@echo "  clean        - Remove temporary files, caches, and .venv"
	@echo "  lint         - Run standard flake8 and mypy checks via uv run"
	@echo "  lint-strict  - Run strict mypy checks via uv run"
