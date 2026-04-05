.PHONY: install test lint run-cli run-web clean

install:
	pip install -e ".[dev]"

test:
	python -m pytest tests/ -v --tb=short

lint:
	python -m py_compile src/first_aid/core.py
	python -m py_compile src/first_aid/cli.py

run-cli:
	python -m first_aid.cli

run-web:
	streamlit run src/first_aid/web_ui.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
