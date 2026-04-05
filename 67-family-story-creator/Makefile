.PHONY: install test lint run web clean

install:
	pip install -e ".[dev]"
	pip install -r requirements.txt

test:
	pytest tests/ -v

lint:
	python -m py_compile src/family_story/core.py
	python -m py_compile src/family_story/cli.py
	python -m py_compile src/family_story/web_ui.py

run:
	python -m family_story.cli create --help

web:
	streamlit run src/family_story/web_ui.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name *.egg-info -exec rm -rf {} + 2>/dev/null || true
	rm -f family_story.log
