.PHONY: install dev test lint run web clean help

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt

dev: ## Install in development mode
	pip install -e ".[dev]"

test: ## Run tests
	pytest tests/ -v

lint: ## Run linting
	python -m py_compile src/standup_gen/core.py
	python -m py_compile src/standup_gen/cli.py
	python -m py_compile src/standup_gen/web_ui.py

run: ## Run CLI (use ARGS for options, e.g. make run ARGS="generate -t tasks.json")
	python -m standup_gen.cli $(ARGS)

web: ## Launch Streamlit web UI
	streamlit run src/standup_gen/web_ui.py

clean: ## Clean generated files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	rm -f standup_gen.log
