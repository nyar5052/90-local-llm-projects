.PHONY: help install dev test lint format run-cli run-web clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt

dev: ## Install with dev dependencies
	pip install -e ".[dev]"

test: ## Run tests
	python -m pytest tests/ -v --tb=short

test-cov: ## Run tests with coverage
	python -m pytest tests/ -v --cov=src/env_manager --cov-report=term-missing

lint: ## Run linter
	flake8 src/ tests/
	mypy src/

format: ## Format code
	black src/ tests/

run-cli: ## Run CLI (use ARGS="validate --file .env")
	python -m src.env_manager.cli $(ARGS)

run-web: ## Run Streamlit Web UI
	streamlit run src/env_manager/web_ui.py

clean: ## Clean build artifacts
	rm -rf __pycache__ .pytest_cache build dist *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
