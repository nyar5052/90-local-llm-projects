.PHONY: help install dev test lint run-cli run-web clean

help: ## Show help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt

dev: ## Install with dev dependencies
	pip install -e ".[dev]"

test: ## Run tests
	python -m pytest tests/ -v --tb=short

lint: ## Run linting
	python -m py_compile src/ticket_classifier/core.py
	python -m py_compile src/ticket_classifier/cli.py
	python -m py_compile src/ticket_classifier/web_ui.py

run-cli: ## Run CLI classifier
	python -m ticket_classifier.cli --help

run-web: ## Launch Streamlit web UI
	streamlit run src/ticket_classifier/web_ui.py

clean: ## Clean build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null; true
	rm -rf *.egg-info build dist
