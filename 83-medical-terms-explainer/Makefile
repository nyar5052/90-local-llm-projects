.PHONY: install test lint run run-web clean help

help: ## Show this help
	@echo Available targets:
	@echo   install   - Install dependencies
	@echo   test      - Run test suite
	@echo   run       - Run CLI (use ARGS= to pass arguments)
	@echo   run-web   - Start Streamlit web UI
	@echo   clean     - Remove build artifacts

install: ## Install project dependencies
	pip install -r requirements.txt
	pip install -e ".[dev]"

test: ## Run test suite with pytest
	python -m pytest tests/ -v --tb=short

run: ## Run CLI tool (e.g. make run ARGS="explain --term hypertension")
	python -m medical_terms.cli $(ARGS)

run-web: ## Start Streamlit web interface
	streamlit run src/medical_terms/web_ui.py

clean: ## Remove build artifacts and caches
	if exist __pycache__ rmdir /s /q __pycache__
	if exist src\medical_terms\__pycache__ rmdir /s /q src\medical_terms\__pycache__
	if exist tests\__pycache__ rmdir /s /q tests\__pycache__
	if exist .pytest_cache rmdir /s /q .pytest_cache
	if exist *.egg-info rmdir /s /q *.egg-info
