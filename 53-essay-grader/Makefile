.PHONY: help install dev test lint run-cli run-web clean

help: ## Show this help message
	@echo Available targets:
	@echo   install   - Install production dependencies
	@echo   dev       - Install development dependencies
	@echo   test      - Run test suite with pytest
	@echo   lint      - Run linter (ruff)
	@echo   run-cli   - Run the CLI tool
	@echo   run-web   - Launch Streamlit web UI
	@echo   clean     - Remove build artifacts and caches

install: ## Install production dependencies
	pip install -r requirements.txt

dev: ## Install development dependencies
	pip install -r requirements.txt
	pip install pytest pytest-cov ruff

test: ## Run test suite
	python -m pytest tests/ -v --tb=short

lint: ## Run linter
	python -m ruff check src/ tests/

run-cli: ## Run the CLI (pass ARGS, e.g. make run-cli ARGS="grade -e essay.txt")
	python -m src.essay_grader.cli $(ARGS)

run-web: ## Launch the Streamlit web UI
	streamlit run src/essay_grader/web_ui.py

clean: ## Remove build artifacts and caches
	rm -rf __pycache__ .pytest_cache build dist *.egg-info
	rm -rf src/__pycache__ src/essay_grader/__pycache__
	rm -rf tests/__pycache__
	rm -f essay_grader.log
