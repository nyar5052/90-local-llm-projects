.PHONY: install test lint run web clean

install:
	pip install -e ".[dev]"

test:
	python -m pytest tests/ -v --tb=short

lint:
	python -m py_compile src/blog_gen/core.py
	python -m py_compile src/blog_gen/cli.py

run:
	python -m blog_gen.cli --help

web:
	streamlit run src/blog_gen/web_ui.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
