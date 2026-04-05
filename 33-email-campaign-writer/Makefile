.PHONY: help install dev test lint run web clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	pip install -r requirements.txt

dev: ## Install dev dependencies
	pip install -e ".[dev]"

test: ## Run tests with pytest
	pytest tests/ -v --tb=short

lint: ## Run basic linting
	python -m py_compile src/email_campaign/core.py
	python -m py_compile src/email_campaign/cli.py
	python -m py_compile src/email_campaign/web_ui.py

run: ## Run CLI (use ARGS="--product X --audience Y")
	python src/email_campaign/cli.py $(ARGS)

web: ## Launch Streamlit web UI
	streamlit run src/email_campaign/web_ui.py

clean: ## Remove build artifacts
	rm -rf build/ dist/ *.egg-info .pytest_cache __pycache__
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
