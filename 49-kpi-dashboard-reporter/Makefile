.PHONY: help install dev test test-cov lint format run dashboard goals anomalies web clean

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	pip install -r requirements.txt

dev: ## Install development dependencies
	pip install -r requirements.txt
	pip install -e ".[dev]"

test: ## Run all tests
	python -m pytest tests/ -v

test-cov: ## Run tests with coverage report
	python -m pytest tests/ -v --cov=src/kpi_reporter --cov-report=term-missing --cov-report=html

lint: ## Run linting checks
	python -m py_compile src/kpi_reporter/core.py
	python -m py_compile src/kpi_reporter/cli.py
	python -m py_compile src/kpi_reporter/web_ui.py

format: ## Format code with black (if installed)
	black src/ tests/

run: ## Run KPI report (usage: make run FILE=data.csv PERIOD=monthly)
	python -m src.kpi_reporter.cli report --file $(FILE) --period $(PERIOD)

dashboard: ## Show KPI dashboard (usage: make dashboard FILE=data.csv)
	python -m src.kpi_reporter.cli dashboard --file $(FILE)

goals: ## Show goal tracking (usage: make goals FILE=data.csv)
	python -m src.kpi_reporter.cli goals --file $(FILE)

anomalies: ## Detect anomalies (usage: make anomalies FILE=data.csv)
	python -m src.kpi_reporter.cli anomalies --file $(FILE)

web: ## Launch Streamlit web UI
	streamlit run src/kpi_reporter/web_ui.py

clean: ## Clean up generated files
	Remove-Item -Recurse -Force -ErrorAction SilentlyContinue __pycache__, .pytest_cache, htmlcov, *.egg-info, .coverage, kpi_reporter.log
	Get-ChildItem -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force
