.PHONY: install test run run-web lint clean

install:
	pip install -r requirements.txt
	pip install -e .

test:
	pytest tests/ -v

run:
	python -m poem_gen.cli --theme "ocean sunset" --style sonnet

run-web:
	streamlit run src/poem_gen/web_ui.py

lint:
	python -m py_compile src/poem_gen/core.py
	python -m py_compile src/poem_gen/cli.py
	python -m py_compile src/poem_gen/web_ui.py
	python -m py_compile src/poem_gen/config.py

clean:
	Get-ChildItem -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force
	Get-ChildItem -Recurse -Directory -Filter .pytest_cache | Remove-Item -Recurse -Force
	Remove-Item -Recurse -Force *.egg-info, build, dist -ErrorAction SilentlyContinue
