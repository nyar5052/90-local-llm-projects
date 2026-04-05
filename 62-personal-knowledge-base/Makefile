.PHONY: install test run run-web lint clean

install:
	pip install -r requirements.txt
	pip install -e .

test:
	pytest tests/ -v

run:
	python -m knowledge_base.cli list

run-web:
	streamlit run src/knowledge_base/web_ui.py

lint:
	python -m py_compile src/knowledge_base/core.py
	python -m py_compile src/knowledge_base/cli.py
	python -m py_compile src/knowledge_base/web_ui.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf *.egg-info build dist
