.PHONY: install dev test lint run-cli run-web clean help

help: ## Show this help
	@echo Available targets:
	@echo   install   - Install production dependencies
	@echo   dev       - Install dev dependencies
	@echo   test      - Run tests with coverage
	@echo   lint      - Run linter
	@echo   run-cli   - Run CLI help
	@echo   run-web   - Launch Streamlit web UI
	@echo   clean     - Remove caches and build artifacts

install: ## Install production dependencies
	pip install -r requirements.txt

dev: ## Install dev dependencies
	pip install -r requirements.txt
	pip install -e ".[dev]"

test: ## Run tests with coverage
	pytest tests/ -v --tb=short --cov=src/budget_analyzer --cov-report=term-missing

lint: ## Run linter (ruff if available)
	python -m py_compile src/budget_analyzer/core.py
	python -m py_compile src/budget_analyzer/cli.py
	python -m py_compile src/budget_analyzer/web_ui.py

run-cli: ## Show CLI help
	python -m budget_analyzer.cli --help

run-web: ## Launch Streamlit web UI
	streamlit run src/budget_analyzer/web_ui.py

clean: ## Remove caches and build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ *.egg-info src/*.egg-info 2>/dev/null || true
