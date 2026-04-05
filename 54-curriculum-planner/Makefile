.PHONY: help install dev test lint run-cli run-web clean

help: ## Show this help message
	@echo Available targets:
	@echo   install   - Install production dependencies
	@echo   dev       - Install development dependencies
	@echo   test      - Run test suite
	@echo   lint      - Run linter (ruff)
	@echo   run-cli   - Run CLI (pass ARGS, e.g., make run-cli ARGS="design -c Python -w 8")
	@echo   run-web   - Launch Streamlit web UI
	@echo   clean     - Remove build artifacts and caches

install: ## Install production dependencies
	pip install -r requirements.txt

dev: ## Install development dependencies
	pip install -e ".[dev]"
	pip install -r requirements.txt

test: ## Run test suite with pytest
	python -m pytest tests/ -v --tb=short

lint: ## Run ruff linter
	ruff check src/ tests/

run-cli: ## Run CLI tool (use ARGS= to pass arguments)
	python -m src.curriculum_planner.cli $(ARGS)

run-web: ## Launch Streamlit web UI
	streamlit run src/curriculum_planner/web_ui.py

clean: ## Remove caches and build artifacts
	rm -rf __pycache__ .pytest_cache build dist *.egg-info
	rm -rf src/__pycache__ src/curriculum_planner/__pycache__
	rm -rf tests/__pycache__
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
