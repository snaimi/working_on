# Define package manager, interpreter, and entrypoint
UV := uv
PYTHON := python3
ENTRYPOINT := simulation.py
map ?= default.txt

.PHONY: all install run debug clean lint lint-strict help

# Default target
all: help

## Install project dependencies
install:
	@$(UV) add pydantic flake8 mypy

## Execute the main simulation script
run:
	@$(UV) run $(PYTHON) $(ENTRYPOINT) $(map) || true

## Run the main script under python's built-in debugger
debug:
	@$(UV) run $(PYTHON) -m pdb $(ENTRYPOINT)

## Remove cache directories, virtual environments, and temporary files
clean:
	@rm -rf __pycache__ .mypy_cache .pytest_cache .venv
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete

## Execute mandatory linting tools using uv run
lint:
	@$(UV) run flake8 . --exclude=.venv
	@$(UV) run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

## Execute enhanced strict linting using uv run
lint-strict:
	@$(UV) run flake8 . --exclude=.venv
	@$(UV) run mypy . --strict

## Show available commands
help:
	@echo "Available rules:"
	@echo "  install      - Install required dependencies into the uv environment"
	@echo "  run          - Execute the main simulation script with uv run"
	@echo "  debug        - Run the main script under PDB debugger with uv run"
	@echo "  clean        - Remove temporary files, caches, and .venv"
	@echo "  lint         - Run standard flake8 and mypy checks via uv run"
	@echo "  lint-strict  - Run strict mypy checks via uv run"
