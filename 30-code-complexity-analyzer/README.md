# 📊 Code Complexity Analyzer

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../LICENSE)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-green.svg)](https://ollama.ai)
[![Streamlit](https://img.shields.io/badge/Streamlit-Web%20UI-red.svg)](https://streamlit.io)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> **Analyze code complexity, track trends, and get AI-powered refactoring suggestions.** All local, all private.

---

## 🏗️ Architecture

```
30-code-complexity-analyzer/
├── src/complexity_analyzer/  # Main package
│   ├── __init__.py           # Package metadata
│   ├── core.py               # 🧠 Metrics, dependencies, trends
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
| 📐 **Cyclomatic Complexity** | Independent paths through code |
| 🧠 **Cognitive Complexity** | How difficult code is to understand |
| 📊 **Maintainability Index** | Overall maintainability score (0-100) |
| 📈 **Halstead Volume** | Code vocabulary and length metrics |
| 🔍 **Function-Level Metrics** | Detailed per-function complexity breakdown |
| 📦 **Dependency Graph** | Import dependency analysis |
| 💡 **Refactoring Suggestions** | AI-powered improvement recommendations |
| 📈 **Trend Tracking** | Track complexity over time |
| 🌐 **Web UI** | Streamlit dashboard with charts |
| 🖥️ **Rich CLI** | Beautiful terminal output with tables |

## 🚀 Installation

```bash
pip install -r requirements.txt
pip install -e ".[dev]"  # Development mode
```

## 🖥️ CLI Usage

```bash
# Summary report (default)
python -m src.complexity_analyzer.cli analyze --file script.py

# Detailed report with AI suggestions
python -m src.complexity_analyzer.cli analyze --file script.py --report detailed

# Metrics only (no AI)
python -m src.complexity_analyzer.cli analyze --file script.py --no-ai

# Track trends
python -m src.complexity_analyzer.cli analyze --file script.py --no-ai --track

# View trends
python -m src.complexity_analyzer.cli trends
```

## 🌐 Web UI

```bash
streamlit run src/complexity_analyzer/web_ui.py
```

Features:
- 📂 File uploader with instant analysis
- 📊 Metrics dashboard with charts
- 🔍 Function-level complexity breakdown
- 📦 Dependency visualization
- 💡 One-click AI suggestions
- 📈 Trend tracking

## 📋 Example Output

```
╭── 📊 Overall Metrics ─────────────────╮
│ Metric                    │ Value      │
│ Maintainability Index     │ 62/100     │
│ Avg Cyclomatic Complexity │ 4.5        │
│ Halstead Volume           │ 245.3      │
│ Dependencies              │ 3          │
╰────────────────────────────────────────╯

╭── 🔍 Function Complexity ─────────────╮
│ Function    │ CC │ Cognitive │ Rating   │
│ process()   │ 8  │ 12        │ MEDIUM   │
│ validate()  │ 12 │ 18        │ HIGH     │
│ helper()    │ 2  │ 1         │ LOW      │
╰────────────────────────────────────────╯
```

## 🧪 Testing

```bash
python -m pytest tests/ -v
python -m pytest tests/ -v --cov=src/complexity_analyzer --cov-report=term-missing
```

## 📋 Requirements

- Python 3.10+
- [Ollama](https://ollama.ai) running locally
- Gemma 3 1B model (or configure another model)

## 🤝 Part of [90 Local LLM Projects](../../README.md)
