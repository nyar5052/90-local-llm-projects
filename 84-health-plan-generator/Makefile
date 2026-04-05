.PHONY: install test lint run run-web clean

install:
	pip install -e ".[dev]"

test:
	pytest tests/ -v --tb=short

lint:
	python -m py_compile src/health_planner/core.py
	python -m py_compile src/health_planner/cli.py

run:
	python -m health_planner.cli generate --goal "general wellness" --duration 1month

run-web:
	streamlit run src/health_planner/web_ui.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -f .health_progress.json
