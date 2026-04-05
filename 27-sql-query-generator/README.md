# 🗃️ SQL Query Generator

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../LICENSE)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-green.svg)](https://ollama.ai)
[![Streamlit](https://img.shields.io/badge/Streamlit-Web%20UI-red.svg)](https://streamlit.io)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> **Convert natural language questions into SQL queries using a local LLM.** Supports PostgreSQL, MySQL & SQLite.

---

## 🏗️ Architecture

```
27-sql-query-generator/
├── src/sql_gen/              # Main package
│   ├── __init__.py           # Package metadata
│   ├── core.py               # 🧠 Schema parsing, SQL generation, optimization
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
| 🗣️ **Natural Language to SQL** | Describe what you want in plain English |
| 📊 **Schema Visualization** | Visual representation of database tables and columns |
| 🔄 **Multi-Dialect** | PostgreSQL, MySQL, SQLite, and standard SQL |
| 📜 **Query History** | Track and re-use previous queries |
| 💡 **Optimization Suggestions** | AI-powered query performance analysis |
| 🌐 **Web UI** | Full Streamlit interface with schema editor |
| 🖥️ **Rich CLI** | Beautiful terminal output with syntax highlighting |
| ⚙️ **Schema-Free Mode** | Works even without a schema definition |

## 🚀 Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or install as a package (development mode)
pip install -e ".[dev]"
```

## ⚙️ Configuration

```bash
cp .env.example .env
# Edit config.yaml for advanced settings
```

## 🖥️ CLI Usage

```bash
# Generate SQL with schema file
python -m src.sql_gen.cli generate --schema schema.sql --query "top customers by revenue"

# Specific dialect
python -m src.sql_gen.cli generate --schema schema.sql --query "monthly sales" --dialect postgresql

# Without schema (infers table structure)
python -m src.sql_gen.cli generate --query "find users who signed up last month"

# View query history
python -m src.sql_gen.cli history

# Clear history
python -m src.sql_gen.cli clear-history
```

## 🌐 Web UI

```bash
streamlit run src/sql_gen/web_ui.py
```

Features:
- 📊 Interactive schema editor with table visualization
- 💬 Natural language query input
- 🎨 Syntax-highlighted SQL output
- 📜 Query history sidebar
- 💡 One-click optimization analysis

## 📋 Example Output

```
╭──────────────────────────────────────────╮
│  🗃️ SQL Query Generator                │
│  Convert natural language to SQL         │
╰──────────────────────────────────────────╯

Tables found: customers, orders, products

╭── 📝 Generated SQL ───────────────────╮
│ SELECT c.name,                         │
│        SUM(o.amount) as total_revenue  │
│ FROM customers c                       │
│ JOIN orders o ON c.id = o.customer_id  │
│ GROUP BY c.name                        │
│ ORDER BY total_revenue DESC            │
│ LIMIT 10;                              │
╰────────────────────────────────────────╯
```

## 🧪 Testing

```bash
python -m pytest tests/ -v
python -m pytest tests/ -v --cov=src/sql_gen --cov-report=term-missing
```

## 📋 Requirements

- Python 3.10+
- [Ollama](https://ollama.ai) running locally
- Gemma 3 1B model (or configure another model)

## 🤝 Part of [90 Local LLM Projects](../../README.md)
