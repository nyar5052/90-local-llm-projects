.PHONY: install dev test lint run web clean help

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	pip install -r requirements.txt

dev: ## Install in development mode
	pip install -e ".[dev]"

test: ## Run tests
	pytest tests/ -v

lint: ## Run linter
	python -m py_compile src/habit_tracker/core.py
	python -m py_compile src/habit_tracker/cli.py
	python -m py_compile src/habit_tracker/web_ui.py

run: ## Run CLI status
	python -m habit_tracker.cli status

web: ## Launch Streamlit web UI
	streamlit run src/habit_tracker/web_ui.py

clean: ## Remove build artifacts
	rm -rf build/ dist/ *.egg-info __pycache__ .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
