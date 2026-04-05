.PHONY: install test lint run-cli run-web clean

install:
	pip install -e ".[dev]"

test:
	python -m pytest tests/ -v --tb=short

lint:
	python -m py_compile src/nutrition_analyzer/core.py
	python -m py_compile src/nutrition_analyzer/cli.py

run-cli:
	python -m nutrition_analyzer.cli

run-web:
	streamlit run src/nutrition_analyzer/web_ui.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
