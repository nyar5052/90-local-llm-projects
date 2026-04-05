.PHONY: install test lint run web clean

install:
	pip install -e ".[dev]"

test:
	python -m pytest tests/ -v

lint:
	python -m flake8 src/ tests/

run:
	python -m home_automation.cli

web:
	streamlit run src/home_automation/web_ui.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
