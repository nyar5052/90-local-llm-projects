.PHONY: install dev test lint run web clean

install:
	pip install -r requirements.txt

dev:
	pip install -e ".[dev]"

test:
	pytest tests/ -v --tb=short

coverage:
	pytest tests/ -v --cov=src/reading_list --cov-report=term-missing

run:
	python src/reading_list/cli.py $(ARGS)

web:
	streamlit run src/reading_list/web_ui.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf *.egg-info build dist .coverage
