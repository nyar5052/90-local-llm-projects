.PHONY: help install dev test lint run-cli run-web clean

help: ## Show this help message
	@echo Available targets:
	@echo   install   - Install production dependencies
	@echo   dev       - Install development dependencies
	@echo   test      - Run test suite
	@echo   lint      - Run linter
	@echo   run-cli   - Run CLI (use ARGS="explain -e volcano")
	@echo   run-web   - Launch Streamlit web UI
	@echo   clean     - Remove build artifacts

install: ## Install production dependencies
	pip install -r requirements.txt

dev: ## Install development dependencies
	pip install -r requirements.txt
	pip install pytest pytest-cov ruff

test: ## Run test suite with pytest
	pytest tests/ -v --tb=short

lint: ## Run ruff linter
	ruff check src/ tests/

run-cli: ## Run CLI tool (pass ARGS="explain -e 'volcano'")
	python -m src.science_explainer.cli $(ARGS)

run-web: ## Launch Streamlit web UI
	streamlit run src/science_explainer/web_ui.py

clean: ## Remove build artifacts and caches
	del /s /q *.pyc 2>nul
	rmdir /s /q __pycache__ 2>nul
	rmdir /s /q .pytest_cache 2>nul
	rmdir /s /q *.egg-info 2>nul
	rmdir /s /q build dist 2>nul
