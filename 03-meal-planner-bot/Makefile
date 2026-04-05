.PHONY: install test run run-web lint clean

install:
	pip install -r requirements.txt
	pip install -e .

test:
	pytest tests/ -v

run:
	python -m meal_planner.cli --diet vegetarian --days 7

run-web:
	streamlit run src/meal_planner/web_ui.py

lint:
	python -m py_compile src/meal_planner/core.py
	python -m py_compile src/meal_planner/cli.py
	python -m py_compile src/meal_planner/web_ui.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf *.egg-info build dist
