.PHONY: install test lint run-cli run-web clean

install:
	pip install -e ".[dev]"

test:
	python -m pytest tests/ -v --tb=short

lint:
	python -m py_compile src/stress_manager/core.py
	python -m py_compile src/stress_manager/cli.py

run-cli:
	python -m stress_manager.cli

run-web:
	streamlit run src/stress_manager/web_ui.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
