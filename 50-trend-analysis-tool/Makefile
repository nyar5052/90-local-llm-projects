.PHONY: help install dev test test-cov lint format clean run-cli run-web

PYTHON ?= python
PIP ?= pip

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	$(PIP) install -r requirements.txt

dev: ## Install dev dependencies
	$(PIP) install -r requirements.txt
	$(PIP) install -e ".[dev]"

test: ## Run tests
	$(PYTHON) -m pytest tests/ -v

test-cov: ## Run tests with coverage
	$(PYTHON) -m pytest tests/ -v --cov=src/trend_analyzer --cov-report=term-missing

lint: ## Run linter (ruff if available, else flake8)
	-ruff check src/ tests/ || flake8 src/ tests/

format: ## Format code (ruff or black)
	-ruff format src/ tests/ || black src/ tests/

clean: ## Remove build artifacts
	Remove-Item -Recurse -Force -ErrorAction SilentlyContinue build, dist, *.egg-info, .pytest_cache, __pycache__
	Get-ChildItem -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

run-cli: ## Run CLI (usage: make run-cli ARGS="analyze -d ./articles")
	$(PYTHON) -m src.trend_analyzer.cli $(ARGS)

run-web: ## Launch Streamlit web UI
	streamlit run src/trend_analyzer/web_ui.py
