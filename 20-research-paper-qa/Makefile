.PHONY: run test lint clean web

run:
	python -m src.research_qa.cli --help

test:
	python -m pytest tests/ -v

lint:
	python -m py_compile src/research_qa/core.py
	python -m py_compile src/research_qa/cli.py
	python -m py_compile src/research_qa/web_ui.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true

web:
	streamlit run src/research_qa/web_ui.py
