# 💊 Drug Interaction Checker

> ⚠️ **MEDICAL DISCLAIMER**: This tool is for **EDUCATIONAL and INFORMATIONAL purposes ONLY**. It is **NOT** a substitute for professional medical or pharmacological advice. **ALWAYS** consult a qualified healthcare provider or pharmacist before making any decisions about your medications. **NEVER** start, stop, or change medications based on this tool's output.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../LICENSE)
[![Ollama](https://img.shields.io/badge/LLM-Ollama-green.svg)](https://ollama.ai)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-red.svg)](https://streamlit.io)

An AI-powered medication interaction analysis tool that checks for drug-drug and drug-food interactions using local LLMs. Features severity classification, dosage notes, and alternative suggestions.

---

## 🚨 Important Medical Disclaimer

> **This tool is NOT a medical device. It does NOT provide medical or pharmacological advice.**
> 
> - ❌ Do NOT use this tool to make medication decisions
> - ❌ Do NOT start, stop, or modify medications based on this tool
> - ❌ This tool may MISS interactions or provide INCOMPLETE information
> - ✅ ALWAYS consult a qualified healthcare provider or pharmacist
> - ✅ Report any adverse reactions to your healthcare provider immediately
>
> By using this tool, you acknowledge that all information provided is for **educational purposes only**.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 💊 **Drug Interaction Check** | AI-powered analysis of potential drug-drug interactions |
| 🍎 **Food Interactions** | Database of common drug-food interactions |
| 📊 **Severity Classification** | 5-level severity system (None → Contraindicated) |
| 💡 **Alternative Suggestions** | Common alternatives for medications |
| 📋 **Dosage Notes** | Typical dosage information for common medications |
| 🌐 **Web UI** | Interactive Streamlit interface with visual interaction matrix |
| ⚡ **CLI Tool** | Fast command-line interface for quick checks |
| 🔒 **Privacy First** | All processing done locally via Ollama |

---

## 🏗️ Architecture

```
82-drug-interaction-checker/
├── src/
│   └── drug_checker/
│       ├── __init__.py          # Package initialization
│       ├── core.py              # Core logic, drug databases, severity system
│       ├── cli.py               # Click CLI interface
│       └── web_ui.py            # Streamlit web interface
├── tests/
│   ├── __init__.py
│   ├── test_core.py             # Core logic tests
│   └── test_cli.py              # CLI tests
├── config.yaml                  # Configuration
├── setup.py                     # Package setup
├── requirements.txt             # Dependencies
├── Makefile                     # Build automation
├── .env.example                 # Environment template
└── README.md                    # This file
```

---

## 🚀 Installation

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.ai) installed and running
- Gemma 4 model: `ollama pull gemma4`

### Setup
```bash
cd 82-drug-interaction-checker
make install
cp .env.example .env
```

---

## 💻 CLI Usage

### Check Drug Interactions
```bash
python -m drug_checker.cli check --medications "aspirin, ibuprofen, warfarin"
```

### Check Food Interactions
```bash
python -m drug_checker.cli food --medication warfarin
```

### Get Alternatives
```bash
python -m drug_checker.cli alternatives --medication ibuprofen
```

### Interactive Mode
```bash
python -m drug_checker.cli interactive
```

---

## 🌐 Web UI

```bash
make run-web
# OR
streamlit run src/drug_checker/web_ui.py
```

---

## 📊 Severity Levels

| Level | Label | Description |
|-------|-------|-------------|
| 🚫 5 | Contraindicated | Must NOT be taken together |
| 🔴 4 | Major | Significant risk, avoid combination |
| 🟡 3 | Moderate | Use with caution |
| 🟢 2 | Minor | Minimal significance |
| ✅ 1 | None | No known interaction |

---

## 🧪 Testing

```bash
make test
# OR
pytest tests/ -v
```

---

## ⚠️ Disclaimer

**This tool is for EDUCATIONAL and INFORMATIONAL purposes ONLY. It is NOT a substitute for professional medical or pharmacological advice. Always consult a qualified healthcare provider or pharmacist before making any decisions about your medications.**

---

*Part of the [90 Local LLM Projects](../../README.md) collection.*
