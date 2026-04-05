# 🖥️ IT Helpdesk Bot

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![LLM](https://img.shields.io/badge/LLM-Gemma%204-orange)
![License](https://img.shields.io/badge/License-MIT-green)
![UI](https://img.shields.io/badge/UI-Streamlit-red?logo=streamlit)

> AI-powered IT support chatbot for diagnosing and resolving common tech issues using a local LLM.

## ✨ Features

- **Category-Based Support** — 7 categories (hardware, software, network, security, email, printer, general)
- **Ticket Tracking** — Create and track support tickets (JSON-backed)
- **Knowledge Base** — Built-in searchable knowledge base with common solutions
- **Solution Templates** — Quick-start templates for common issue types
- **Conversational Troubleshooting** — Multi-turn dialogue with context awareness
- **Streamlit Web UI** — Browser-based chat with ticket history and KB viewer
- **Rich CLI Interface** — Beautiful formatted terminal output
- **Configurable** — YAML-based settings

## 📦 Installation

```bash
pip install -r requirements.txt
pip install -e .
```

## 🚀 Usage

### CLI

```bash
# Interactive mode
python -m helpdesk_bot.cli

# Pre-select a category
python -m helpdesk_bot.cli --category 3
```

### Web UI (Streamlit)

```bash
streamlit run src/helpdesk_bot/web_ui.py
```

### CLI Commands

| Command       | Action                              |
|---------------|-------------------------------------|
| `quit`        | Exit the session                    |
| `new`         | Start a new issue                   |
| `ticket`      | Create a support ticket             |
| `kb <query>`  | Search the knowledge base           |
| `history`     | View ticket history                 |

## 🖼️ Screenshots

*Coming soon — screenshots of both CLI and Web UI.*

## 🧪 Running Tests

```bash
pytest tests/ -v
```

## ⚙️ Configuration

Edit `config.yaml` to customize model, ticket storage, and knowledge base settings.

## 📁 Project Structure

```
02-it-helpdesk-bot/
├── src/
│   └── helpdesk_bot/
│       ├── __init__.py      # Package metadata
│       ├── core.py          # Core business logic
│       ├── cli.py           # Click CLI interface
│       ├── web_ui.py        # Streamlit web interface
│       ├── config.py        # Configuration management
│       └── utils.py         # Ticket tracking, KB, templates
├── tests/
│   ├── __init__.py
│   ├── test_core.py         # Core logic tests
│   └── test_cli.py          # CLI tests
├── config.yaml              # Default configuration
├── setup.py                 # Package setup
├── requirements.txt         # Dependencies
├── Makefile                 # Common commands
├── .env.example             # Example environment variables
└── README.md                # This file
```
