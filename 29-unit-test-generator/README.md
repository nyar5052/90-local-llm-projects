# 🧪 Unit Test Generator

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../LICENSE)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-green.svg)](https://ollama.ai)
[![Streamlit](https://img.shields.io/badge/Streamlit-Web%20UI-red.svg)](https://streamlit.io)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> **Automatically generate comprehensive unit tests for Python code using a local LLM.** Supports pytest & unittest.

---

## 🏗️ Architecture

```
29-unit-test-generator/
├── src/test_gen/             # Main package
│   ├── __init__.py           # Package metadata
│   ├── core.py               # 🧠 AST analysis, coverage, edge case detection
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
| 🔬 **AST Analysis** | Deep code parsing to extract functions, classes, and signatures |
| 📊 **Coverage Analysis** | Estimate test coverage requirements before generating |
| 🎯 **Edge Case Detection** | Auto-detect None handling, zero values, empty collections |
| 🧪 **Multiple Frameworks** | Generate pytest or unittest tests |
| 📐 **Test Organization** | Suggested test file structure per class/module |
| 📥 **Download Tests** | Download generated tests as .py files |
| 🌐 **Web UI** | Streamlit interface with code input and metrics |
| 🖥️ **Rich CLI** | Beautiful terminal output with code structure tables |

## 🚀 Installation

```bash
pip install -r requirements.txt
pip install -e ".[dev]"  # Development mode
```

## 🖥️ CLI Usage

```bash
# Generate pytest tests (default)
python -m src.test_gen.cli generate --file module.py

# Generate unittest tests
python -m src.test_gen.cli generate --file module.py --framework unittest

# Save to a file
python -m src.test_gen.cli generate --file module.py --output test_module.py

# Analyze coverage requirements
python -m src.test_gen.cli analyze --file module.py

# Show source code before generating
python -m src.test_gen.cli generate --file module.py --show-source
```

## 🌐 Web UI

```bash
streamlit run src/test_gen/web_ui.py
```

Features:
- 📄 Code input with file upload
- 📊 Coverage metrics dashboard
- 🧪 Generated tests with syntax highlighting
- 📥 One-click test download
- 🔧 Framework selector (pytest/unittest)

## 📋 Example Output

```
╭── 📊 Code Structure ──────────────────────────╮
│ Type     │ Name     │ Details  │ Edge Cases    │
│ Function │ add      │ (a, b)   │ —             │
│ Function │ divide   │ (a, b)   │ Zero handling │
│ Class    │ Utils    │ 2 methods│               │
╰────────────────────────────────────────────────╯

Testable units: 4 | Estimated tests: 12 | Edge cases: 2
```

## 🧪 Testing

```bash
python -m pytest tests/ -v
python -m pytest tests/ -v --cov=src/test_gen --cov-report=term-missing
```

## 📋 Requirements

- Python 3.10+
- [Ollama](https://ollama.ai) running locally
- Gemma 3 1B model (or configure another model)

## 🤝 Part of [90 Local LLM Projects](../../README.md)
