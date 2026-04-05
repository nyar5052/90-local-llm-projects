.PHONY: help install dev test lint run-cli run-web clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt

dev: ## Install in development mode
	pip install -e ".[dev]"

test: ## Run tests with pytest
	python -m pytest tests/ -v --tb=short

test-cov: ## Run tests with coverage
	python -m pytest tests/ -v --cov=src/test_gen --cov-report=term-missing

lint: ## Run linting
	python -m py_compile src/test_gen/core.py
	python -m py_compile src/test_gen/cli.py

run-cli: ## Run CLI (use ARGS="generate --file mycode.py")
	python -m src.test_gen.cli $(ARGS)

run-web: ## Run Streamlit web UI
	streamlit run src/test_gen/web_ui.py

clean: ## Clean build artifacts
	rm -rf __pycache__ .pytest_cache build dist *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
