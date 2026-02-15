# default action: show task list by `just` command
default:
    @just --list

# run main
run:
    uv run main.py

# format code
fmt:
    uv run ruff format .

# lint with fixing
lint:
    uv run ruff check . --fix

# run test
test:
    uv run pytest

# update package and sync
update:
    uv lock --upgrade
    uv sync

# initial setup for development environment
setup:
    uv sync
    @echo "Setup complete. Virtual environment is ready."

# all check for CI
check-all: fmt lint test