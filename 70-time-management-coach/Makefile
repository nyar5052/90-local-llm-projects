.PHONY: install dev test lint run-cli run-web clean

install:
	pip install -r requirements.txt

dev:
	pip install -e ".[dev]"

test:
	python -m pytest tests/ -v

lint:
	python -m py_compile src/time_coach/core.py
	python -m py_compile src/time_coach/cli.py
	python -m py_compile src/time_coach/web_ui.py

run-cli:
	python -m time_coach.cli --help

run-web:
	streamlit run src/time_coach/web_ui.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	rm -f time_coach.log
