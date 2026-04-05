# 🔍 Research Paper Q&A

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![LLM](https://img.shields.io/badge/LLM-Ollama%2FGemma4-green)
![CLI](https://img.shields.io/badge/CLI-Click-orange)
![Web](https://img.shields.io/badge/Web-Streamlit-red)
![Tests](https://img.shields.io/badge/tests-pytest-yellow)

Interactive question answering over research papers with multi-paper support, citation tracking, follow-up question suggestions, and notes export. Includes both an interactive CLI and a Streamlit chat interface.

## Features

- **Multi-Paper Support** — Load and query across multiple papers simultaneously
- **Citation Tracking** — Automatic extraction and display of paper citations
- **Follow-up Suggestions** — AI-generated follow-up question recommendations
- **Notes Export** — Export conversation to Markdown, JSON, or plain text
- **Contextual Q&A** — Full conversation memory for coherent multi-turn dialogue
- **Streamlit Chat UI** — Paper upload, chat interface, citation sidebar, notes export
- **Interactive CLI** — Rich terminal interface with history and suggest commands
- **YAML Configuration** — Customizable settings via `config.yaml`

## Installation

```bash
cd 20-research-paper-qa
pip install -r requirements.txt
ollama serve && ollama pull gemma4
```

## Usage

### CLI

```bash
# Single paper
python -m src.research_qa.cli --paper paper.txt

# Multiple papers
python -m src.research_qa.cli --paper paper1.txt --paper paper2.txt
```

### Web UI

```bash
streamlit run src/research_qa/web_ui.py
```

### Interactive Commands

| Command            | Description                           |
|--------------------|---------------------------------------|
| *(question text)*  | Ask a question about the paper(s)     |
| `suggest`          | Get follow-up question suggestions    |
| `history`          | View conversation history             |
| `export [file]`    | Export notes to file                  |
| `clear`            | Reset conversation context            |
| `quit`             | Exit the application                  |

### CLI Options

| Option      | Required | Default | Description                      |
|-------------|----------|---------|----------------------------------|
| `--paper`   | Yes      | —       | Path to paper file (repeatable)  |
| `--config`  | No       | —       | Path to config.yaml              |
| `--verbose` | No       | —       | Enable debug logging             |

## Testing

```bash
python -m pytest tests/ -v
```

## Project Structure

```
20-research-paper-qa/
├── src/research_qa/
│   ├── __init__.py
│   ├── core.py              # Q&A and citation logic
│   ├── cli.py               # Click CLI interface
│   ├── web_ui.py            # Streamlit chat interface
│   ├── config.py            # Configuration management
│   └── utils.py             # Export and logging helpers
├── tests/
│   ├── __init__.py
│   ├── test_core.py
│   └── test_cli.py
├── config.yaml
├── setup.py
├── requirements.txt
├── Makefile
├── .env.example
└── README.md
```
