.PHONY: install test lint run-cli run-web clean

install:
	pip install -e ".[dev]"

test:
	python -m pytest tests/ -v --tb=short

lint:
	python -m py_compile src/sleep_advisor/core.py
	python -m py_compile src/sleep_advisor/cli.py

run-cli:
	python -m sleep_advisor.cli

run-web:
	streamlit run src/sleep_advisor/web_ui.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
