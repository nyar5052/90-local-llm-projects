.PHONY: install dev test lint format clean run web

install:
	pip install -e .

dev:
	pip install -e ".[dev]"

test:
	python -m pytest tests/ -v --tb=short

test-cov:
	python -m pytest tests/ -v --cov=src/stock_reporter --cov-report=term-missing

lint:
	flake8 src/ tests/
	mypy src/

format:
	black src/ tests/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf *.egg-info build dist

run:
	python -m src.stock_reporter.cli --help

web:
	streamlit run src/stock_reporter/web_ui.py
