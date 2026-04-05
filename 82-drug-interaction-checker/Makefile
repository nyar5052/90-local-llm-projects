.PHONY: install test lint run run-web clean help

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt

test: ## Run tests
	pytest tests/ -v

lint: ## Run linting
	python -m py_compile src/drug_checker/core.py
	python -m py_compile src/drug_checker/cli.py
	python -m py_compile src/drug_checker/web_ui.py

run: ## Run CLI interactive mode
	python -m drug_checker.cli interactive

run-web: ## Run Streamlit web UI
	streamlit run src/drug_checker/web_ui.py

clean: ## Clean up cache files
	Remove-Item -Recurse -Force __pycache__, .pytest_cache, src/drug_checker/__pycache__ -ErrorAction SilentlyContinue
