# 🏥 Symptom Checker Bot

> ⚠️ **MEDICAL DISCLAIMER**: This tool is for **EDUCATIONAL and INFORMATIONAL purposes ONLY**. It is **NOT** a substitute for professional medical advice, diagnosis, or treatment. **ALWAYS** consult a qualified healthcare provider for any health concerns. If you are experiencing a medical emergency, **call emergency services immediately**.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../LICENSE)
[![Ollama](https://img.shields.io/badge/LLM-Ollama-green.svg)](https://ollama.ai)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-red.svg)](https://streamlit.io)

An AI-powered symptom analysis tool that provides **educational** health information using local LLMs. Features urgency scoring, body region mapping, medical history tracking, and both CLI and web interfaces.

---

## 🚨 Important Medical Disclaimer

> **This tool is NOT a medical device. It does NOT provide medical advice, diagnosis, or treatment.**
> 
> - ❌ Do NOT use this tool to make medical decisions
> - ❌ Do NOT delay seeking professional medical care based on this tool's output
> - ✅ ALWAYS consult a qualified healthcare professional for health concerns
> - ✅ Call emergency services (911) for medical emergencies
>
> By using this tool, you acknowledge that all information provided is for **educational purposes only**.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔍 **Symptom Analysis** | AI-powered analysis of described symptoms using local LLMs |
| 📊 **Urgency Scoring** | 5-level urgency assessment (Low → Emergency) with color coding |
| 🗺️ **Body Region Mapping** | Automatic categorization of symptoms by body region |
| 📋 **Medical History** | Session-based symptom tracking and history review |
| 💬 **Interactive Chat** | Multi-turn conversational symptom checking |
| 🌐 **Web UI** | Beautiful Streamlit interface with visual urgency meters |
| ⚡ **CLI Tool** | Fast command-line interface for quick checks |
| 🔒 **Privacy First** | All processing done locally via Ollama - no data leaves your machine |

---

## 🏗️ Architecture

```
81-symptom-checker-bot/
├── src/
│   └── symptom_checker/
│       ├── __init__.py          # Package initialization
│       ├── core.py              # Core logic, symptom DB, urgency scoring
│       ├── cli.py               # Click CLI interface
│       └── web_ui.py            # Streamlit web interface
├── tests/
│   ├── __init__.py
│   ├── test_core.py             # Core logic tests
│   └── test_cli.py              # CLI integration tests
├── config.yaml                  # Configuration file
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
- Gemma 4 model pulled: `ollama pull gemma4`

### Setup

```bash
# Navigate to project directory
cd 81-symptom-checker-bot

# Install dependencies
make install
# OR manually:
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Verify Ollama is running
ollama list
```

---

## 💻 CLI Usage

### Quick Symptom Check
```bash
python -m symptom_checker.cli check --symptoms "headache, fever, sore throat"
```

### Interactive Chat Mode
```bash
python -m symptom_checker.cli chat
```

### View Body Regions
```bash
python -m symptom_checker.cli regions
```

### View Symptom History
```bash
python -m symptom_checker.cli history
```

---

## 🌐 Web UI

Launch the Streamlit web interface:

```bash
make run-web
# OR
streamlit run src/symptom_checker/web_ui.py
```

### Web UI Features:
- 🎯 **Symptom Selector**: Multi-select from categorized symptom database
- 📊 **Urgency Meter**: Visual color-coded urgency assessment
- 🗺️ **Body Region Display**: See which body regions are affected
- 📋 **History Tracker**: Review past symptom checks in the session
- ⚠️ **Disclaimer Banner**: Prominent medical disclaimer always visible

---

## ⚙️ Configuration

Edit `config.yaml` to customize:

```yaml
model: "gemma4"           # LLM model to use
temperature: 0.3          # Response creativity (0.0-1.0)
max_tokens: 1024          # Maximum response length
log_level: "INFO"         # Logging level
```

---

## 🧪 Testing

```bash
make test
# OR
pytest tests/ -v
```

---

## 📊 Urgency Levels

| Level | Label | Action |
|-------|-------|--------|
| 🟢 1 | Low | Self-care likely sufficient |
| 🟡 2 | Mild | Schedule routine appointment if persistent |
| 🟠 3 | Moderate | See your healthcare provider soon |
| 🔴 4 | High | Seek medical attention today |
| 🚨 5 | Emergency | Call emergency services immediately |

---

## ⚠️ Disclaimer

**This tool is for EDUCATIONAL and INFORMATIONAL purposes ONLY. It is NOT a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of a qualified healthcare provider with any questions you have regarding a medical condition. Never disregard professional medical advice or delay in seeking it because of something you have read or received from this tool.**

---

*Part of the [90 Local LLM Projects](../../README.md) collection.*
