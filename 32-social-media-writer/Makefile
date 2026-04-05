.PHONY: install test lint run web clean help

help: ## Show this help message
	@echo "Social Media Writer - Available targets:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt
	pip install -e .

test: ## Run all tests
	pytest tests/ -v --tb=short

lint: ## Run linting checks
	python -m py_compile src/social_writer/core.py
	python -m py_compile src/social_writer/cli.py
	python -m py_compile src/social_writer/web_ui.py

run: ## Run the CLI (use ARGS to pass arguments, e.g., make run ARGS="--platform twitter --topic AI")
	python -m social_writer.cli $(ARGS)

web: ## Launch the Streamlit web UI
	streamlit run src/social_writer/web_ui.py

clean: ## Clean up generated files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name *.egg-info -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
