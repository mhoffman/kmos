.PHONY: help install install-dev test test-verbose test-coverage clean lint format type-check docs docs-serve build all pre-commit

help:  ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install the package in development mode
	uv sync

install-dev:  ## Install package with all development dependencies
	uv sync --all-extras

test:  ## Run tests
	PYTHONPATH=. uv run pytest tests/

test-verbose:  ## Run tests with verbose output
	PYTHONPATH=. uv run pytest tests/ -v

test-coverage:  ## Run tests with coverage report
	PYTHONPATH=. uv run pytest tests/ --cov=kmos --cov-report=html --cov-report=term

clean:  ## Clean build artifacts and caches
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete
	find . -type f -name '*~' -delete

lint:  ## Lint code with ruff
	uv run ruff check kmos/ tests/

format:  ## Format code with ruff
	uv run ruff format kmos/ tests/

format-check:  ## Check code formatting without modifying files
	uv run ruff format --check kmos/ tests/

type-check:  ## Run type checking with mypy
	uv run mypy kmos/

docs:  ## Build documentation
	cd doc && uv run make html

docs-serve:  ## Build and serve documentation locally
	cd doc && uv run make html && python -m http.server 8000 --directory build/html

build:  ## Build distribution packages
	uv build

all: clean install-dev lint format type-check test  ## Run full CI pipeline locally

pre-commit:  ## Run pre-commit checks on all files
	uv run pre-commit run --all-files
