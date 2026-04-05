.PHONY: install test run run-web lint clean

install:
	pip install -r requirements.txt
	pip install -e .

test:
	pytest tests/ -v

run:
	python -m travel_planner.cli --destination "Tokyo" --days 5 --budget moderate

run-web:
	streamlit run src/travel_planner/web_ui.py

lint:
	python -m py_compile src/travel_planner/core.py
	python -m py_compile src/travel_planner/cli.py
	python -m py_compile src/travel_planner/web_ui.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf *.egg-info build dist
