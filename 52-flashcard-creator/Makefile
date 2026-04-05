.PHONY: help install dev test lint run-cli run-web clean

help:
	@echo "Available targets:"
	@echo "  install    Install dependencies"
	@echo "  dev        Install dev dependencies"
	@echo "  test       Run tests"
	@echo "  run-cli    Run CLI"
	@echo "  run-web    Run Streamlit UI"
	@echo "  clean      Clean caches"

install:
	pip install -r requirements.txt

dev:
	pip install -e ".[dev]"

test:
	python -m pytest tests/ -v --tb=short

lint:
	python -m py_compile src/flashcard_creator/core.py
	python -m py_compile src/flashcard_creator/cli.py

run-cli:
	python -m flashcard_creator.cli create --topic "Python Basics" --count 10

run-web:
	streamlit run src/flashcard_creator/web_ui.py

clean:
	Remove-Item -Recurse -Force __pycache__, .pytest_cache, *.pyc -ErrorAction SilentlyContinue
