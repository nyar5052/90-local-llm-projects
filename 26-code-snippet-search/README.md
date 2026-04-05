# 🔎 Code Snippet Search

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../LICENSE)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-green.svg)](https://ollama.ai)
[![Streamlit](https://img.shields.io/badge/Streamlit-Web%20UI-red.svg)](https://streamlit.io)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> **Search your codebase using natural language queries powered by a local LLM.** No data leaves your machine.

---

## 🏗️ Architecture

```
26-code-snippet-search/
├── src/code_search/          # Main package
│   ├── __init__.py           # Package metadata
│   ├── core.py               # 🧠 Business logic (scanning, indexing, search)
│   ├── cli.py                # 🖥️  CLI interface (Rich + Click)
│   └── web_ui.py             # 🌐 Streamlit web interface
├── tests/                    # Test suite
│   ├── test_core.py          # Core logic tests
│   └── test_cli.py           # CLI tests
├── config.yaml               # ⚙️  Configuration
├── setup.py                  # 📦 Package setup
├── Makefile                  # 🔧 Task runner
├── .env.example              # 🔑 Environment template
├── requirements.txt          # 📋 Dependencies
└── README.md                 # 📖 This file
```

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔍 **Natural Language Search** | Search code using plain English queries |
| 📊 **Relevance Scoring** | Pre-LLM keyword scoring ranks files before AI analysis |
| 💾 **Index Caching** | Cache file indexes for faster repeated searches |
| 🎨 **Syntax Highlighting** | Beautiful code display in both CLI and web UI |
| ⭐ **Bookmarks** | Save and manage favorite search results |
| 🌐 **Web UI** | Full Streamlit interface with interactive search |
| 🖥️ **Rich CLI** | Beautiful terminal output with tables and panels |
| ⚙️ **Configurable** | YAML config for extensions, limits, and behavior |

## 🚀 Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or install as a package (development mode)
pip install -e ".[dev]"
```

## ⚙️ Configuration

Copy and customize the config file:
```bash
cp .env.example .env
# Edit config.yaml for advanced settings
```

## 🖥️ CLI Usage

```bash
# Search a directory
python -m src.code_search.cli search --dir ./my-project --query "authentication logic"

# Search with specific extensions
python -m src.code_search.cli search --dir . --query "database connection" --ext .py --ext .sql

# Search and bookmark results
python -m src.code_search.cli search --dir . --query "error handling" --bookmark

# View bookmarks
python -m src.code_search.cli bookmarks

# Remove a bookmark
python -m src.code_search.cli remove-bookmark 0

# Verbose mode
python -m src.code_search.cli --verbose search --dir . --query "test"
```

## 🌐 Web UI

```bash
# Launch Streamlit interface
streamlit run src/code_search/web_ui.py
```

Features:
- 🔍 Search box with auto-complete
- 📁 File browser with syntax highlighting
- ⭐ Bookmark management sidebar
- 📊 File statistics dashboard

## 📋 Example Output

```
╭──────────────────────────────────────────╮
│  🔎 Code Snippet Search                 │
│  Search code with natural language       │
╰──────────────────────────────────────────╯

Indexed 23 file(s)

╭── 🎯 Search Results ──────────────────╮
│ ## auth/login.py (HIGH)                │
│ Lines 15-30: JWT token validation      │
│                                        │
│ ## middleware/auth.py (MEDIUM)          │
│ Lines 5-12: Authentication middleware  │
╰────────────────────────────────────────╯
```

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ -v --cov=src/code_search --cov-report=term-missing
```

## 📋 Requirements

- Python 3.10+
- [Ollama](https://ollama.ai) running locally
- Gemma 3 1B model (or configure another model)

## 🤝 Part of [90 Local LLM Projects](../../README.md)
