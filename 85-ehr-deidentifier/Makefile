# EHR De-Identifier Makefile
# ⚠️ EDUCATIONAL USE ONLY - NOT HIPAA CERTIFIED

.PHONY: install test lint run-web clean help

help: ## Show this help
	@echo ============================================
	@echo  EHR De-Identifier - EDUCATIONAL USE ONLY
	@echo  NOT certified for HIPAA compliance
	@echo ============================================
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt

install-dev: ## Install with dev dependencies
	pip install -r requirements.txt
	pip install pytest pytest-cov

test: ## Run tests
	python -m pytest tests/ -v

test-cov: ## Run tests with coverage
	python -m pytest tests/ -v --cov=src/ehr_deidentifier --cov-report=term-missing

run-web: ## Launch Streamlit web UI
	streamlit run src/ehr_deidentifier/web_ui.py

run-cli: ## Show CLI help
	python -m src.ehr_deidentifier.cli --help

clean: ## Remove temporary files
	rm -rf __pycache__ .pytest_cache .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
