# 🔄 Code Translator

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../LICENSE)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-green.svg)](https://ollama.ai)
[![Streamlit](https://img.shields.io/badge/Streamlit-Web%20UI-red.svg)](https://streamlit.io)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> **Translate code between programming languages using a local LLM.** Supports 10 languages with side-by-side comparison.

---

## 🏗️ Architecture

```
28-code-translator/
├── src/code_translator/      # Main package
│   ├── __init__.py           # Package metadata
│   ├── core.py               # 🧠 Translation, validation, batch processing
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
| 🌐 **10 Languages** | Python, JavaScript, TypeScript, Java, Go, Rust, C#, C++, Ruby, PHP |
| 📐 **Side-by-Side Comparison** | View source and translated code with metrics |
| ✅ **Syntax Validation** | Basic syntax checking for common languages |
| 📦 **Batch Translation** | Translate multiple files at once |
| 📝 **Translation Notes** | AI-generated notes about language differences |
| 🔍 **Auto-Detection** | Automatically detect source language from file extension |
| 🌐 **Web UI** | Split-pane Streamlit interface |
| 🖥️ **Rich CLI** | Beautiful terminal output with syntax highlighting |

## 🚀 Installation

```bash
pip install -r requirements.txt
pip install -e ".[dev]"  # Development mode
```

## 🖥️ CLI Usage

```bash
# Translate a file
python -m src.code_translator.cli translate --file script.py --target javascript

# Save translated output
python -m src.code_translator.cli translate --file main.go --target python --output main.py

# Batch translate
python -m src.code_translator.cli batch --files a.py --files b.py --target javascript

# Translation notes
python -m src.code_translator.cli notes --source python --target rust
```

## 🌐 Web UI

```bash
streamlit run src/code_translator/web_ui.py
```

Features:
- 📄 Split-pane source/target view
- 🔤 Language selectors with auto-detection
- 📊 Translation metrics (line count, character ratio)
- 📝 One-click translation notes

## 📋 Example Output

```
╭── 📄 Source (Python) ──────────────────╮
│ 1 │ def fibonacci(n):                  │
│ 2 │     if n <= 1:                     │
│ 3 │         return n                   │
│ 4 │     return fibonacci(n-1) + ...    │
╰────────────────────────────────────────╯

╭── 🔄 Translated to JavaScript ────────╮
│ function fibonacci(n) {                │
│   if (n <= 1) return n;                │
│   return fibonacci(n - 1) + ...;       │
│ }                                      │
╰────────────────────────────────────────╯
```

## 🧪 Testing

```bash
python -m pytest tests/ -v
python -m pytest tests/ -v --cov=src/code_translator --cov-report=term-missing
```

## 📋 Requirements

- Python 3.10+
- [Ollama](https://ollama.ai) running locally
- Gemma 3 1B model (or configure another model)

## 🤝 Part of [90 Local LLM Projects](../../README.md)
