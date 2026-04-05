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
	python -m pytest tests/ -v --cov=src/code_translator --cov-report=term-missing

lint: ## Run linting
	python -m py_compile src/code_translator/core.py
	python -m py_compile src/code_translator/cli.py

run-cli: ## Run CLI (use ARGS="translate --file test.py --target javascript")
	python -m src.code_translator.cli $(ARGS)

run-web: ## Run Streamlit web UI
	streamlit run src/code_translator/web_ui.py

clean: ## Clean build artifacts
	rm -rf __pycache__ .pytest_cache build dist *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
