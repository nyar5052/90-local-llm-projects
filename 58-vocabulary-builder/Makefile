.PHONY: install dev test lint run web clean help

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	pip install -e .

dev: ## Install development dependencies
	pip install -e ".[dev]"

test: ## Run tests
	pytest tests/ -v --tb=short

coverage: ## Run tests with coverage report
	pytest tests/ -v --cov=src/vocab_builder --cov-report=term-missing

lint: ## Run linting checks
	python -m py_compile src/vocab_builder/core.py
	python -m py_compile src/vocab_builder/cli.py

run: ## Run CLI (use ARGS="learn --topic 'SAT words'")
	python -m vocab_builder.cli $(ARGS)

web: ## Launch Streamlit web UI
	streamlit run src/vocab_builder/web_ui.py

clean: ## Clean build artifacts
	rm -rf __pycache__ .pytest_cache build dist *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
