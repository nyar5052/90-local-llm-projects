.PHONY: install dev test lint run web clean help

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	pip install -e .

dev: ## Install development dependencies
	pip install -e ".[dev]"

test: ## Run tests with coverage
	pytest tests/ -v --tb=short --co -q 2>/dev/null || pytest tests/ -v --tb=short

coverage: ## Run tests with coverage report
	pytest tests/ -v --cov=src/math_solver --cov-report=term-missing

lint: ## Run linting checks
	python -m py_compile src/math_solver/core.py
	python -m py_compile src/math_solver/cli.py

run: ## Run CLI (use ARGS="solve --problem '2x+5=15'")
	python -m math_solver.cli $(ARGS)

web: ## Launch Streamlit web UI
	streamlit run src/math_solver/web_ui.py

clean: ## Clean build artifacts
	rm -rf __pycache__ .pytest_cache build dist *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
