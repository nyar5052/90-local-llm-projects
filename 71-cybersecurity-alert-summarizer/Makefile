.PHONY: help install dev test lint format run web clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt

dev: ## Install dev dependencies
	pip install -r requirements.txt
	pip install pytest pytest-cov black ruff mypy

test: ## Run tests
	python -m pytest tests/ -v --tb=short

test-cov: ## Run tests with coverage
	python -m pytest tests/ -v --cov=src/cyber_alert --cov-report=term-missing

lint: ## Run linter
	python -m ruff check src/ tests/

format: ## Format code
	python -m black src/ tests/

run: ## Run CLI (use ARGS="--help" for options)
	python -m src.cyber_alert.cli $(ARGS)

web: ## Launch Streamlit Web UI
	streamlit run src/cyber_alert/web_ui.py

clean: ## Clean build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null; true
	rm -rf *.egg-info build dist .coverage
