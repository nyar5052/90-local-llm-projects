.PHONY: install test lint run-cli run-web clean help

help:
	@echo "Smart Calendar Assistant - Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make test       - Run tests"
	@echo "  make run-cli    - Run CLI application"
	@echo "  make run-web    - Run Streamlit web UI"
	@echo "  make clean      - Clean build artifacts"

install:
	pip install -e ".[dev]"

test:
	pytest tests/ -v --tb=short

lint:
	python -m py_compile src/calendar_assistant/core.py
	python -m py_compile src/calendar_assistant/cli.py

run-cli:
	python -m calendar_assistant.cli

run-web:
	streamlit run src/calendar_assistant/web_ui.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	rm -rf *.egg-info build dist
