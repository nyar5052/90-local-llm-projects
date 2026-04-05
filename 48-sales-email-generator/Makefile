.PHONY: install dev test test-cov lint run web clean help

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	pip install -r requirements.txt

dev: ## Install development dependencies and package in editable mode
	pip install -e ".[dev]"

test: ## Run tests
	pytest tests/ -v

test-cov: ## Run tests with coverage
	pytest tests/ -v --cov=src/sales_email_gen --cov-report=term-missing

lint: ## Run linting checks
	python -m py_compile src/sales_email_gen/core.py
	python -m py_compile src/sales_email_gen/cli.py
	python -m py_compile src/sales_email_gen/web_ui.py

run: ## Run CLI (use ARGS to pass arguments, e.g. make run ARGS="generate -p 'CTO' -pr 'Product'")
	python -m sales_email_gen.cli $(ARGS)

web: ## Launch Streamlit web UI
	streamlit run src/sales_email_gen/web_ui.py

clean: ## Remove build artifacts and caches
	rm -rf build/ dist/ *.egg-info .pytest_cache __pycache__
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
