.PHONY: help install test lint run web clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt

test: ## Run tests
	python -m pytest tests/ -v

lint: ## Run linter
	python -m py_compile src/gift_recommender/core.py
	python -m py_compile src/gift_recommender/cli.py

run: ## Run CLI (use ARGS for options)
	python -m gift_recommender.cli $(ARGS)

web: ## Launch Streamlit web UI
	streamlit run src/gift_recommender/web_ui.py

clean: ## Clean temporary files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
