# 🏋️ Health Plan Generator

> ⚠️ **MEDICAL DISCLAIMER**: This tool is for **INFORMATIONAL and EDUCATIONAL PURPOSES ONLY**. It does **NOT** provide medical advice, diagnosis, or treatment. The plans generated are general wellness suggestions and are **NOT** a substitute for professional medical guidance. **ALWAYS** consult a qualified healthcare professional before starting any new health, diet, or exercise program.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../LICENSE)
[![Ollama](https://img.shields.io/badge/LLM-Ollama-green.svg)](https://ollama.ai)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-red.svg)](https://streamlit.io)

An AI-powered personalized wellness plan generator with goal milestones, weekly check-ins, progress tracking, and adaptive recommendations.

---

## 🚨 Important Medical Disclaimer

> **This tool does NOT provide medical advice.**
>
> - ❌ Plans are NOT a substitute for professional guidance
> - ❌ Do NOT start a new program without consulting your doctor
> - ✅ ALWAYS consult a healthcare professional first
> - ✅ Use this as a supplement to professional advice only
>
> Generated plans are for **educational and informational purposes only**.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📋 **Plan Generation** | AI-powered personalized wellness plans |
| 🎯 **Goal Milestones** | Week-by-week milestones for common health goals |
| 📊 **Weekly Check-ins** | Structured weekly progress questionnaires |
| 📈 **Progress Tracking** | Track energy, sleep, and overall progress |
| 🔄 **Adaptive Recommendations** | AI adjusts suggestions based on your progress |
| 🌐 **Web UI** | Interactive Streamlit interface |
| ⚡ **CLI Tool** | Fast command-line plan generation |

---

## 🏗️ Architecture

```
84-health-plan-generator/
├── src/
│   └── health_planner/
│       ├── __init__.py      # Package init & version
│       ├── core.py          # Core logic, milestones, progress tracking
│       ├── cli.py           # Click CLI interface
│       └── web_ui.py        # Streamlit web interface
├── tests/
│   ├── __init__.py
│   ├── test_core.py         # Core logic tests
│   └── test_cli.py          # CLI command tests
├── config.yaml              # Model & generation settings
├── setup.py                 # Package setup
├── requirements.txt         # Python dependencies
├── Makefile                 # Common tasks
├── .env.example             # Environment template
└── README.md                # This file
```

---

## 🚀 Installation

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com/) running locally with a model pulled (e.g., `ollama pull gemma4`)

### Setup

```bash
cd 84-health-plan-generator
pip install -e ".[dev]"
cp .env.example .env
```

Or without editable install:

```bash
pip install -r requirements.txt
```

---

## 💻 CLI Usage

### Generate a Plan

```bash
python -m health_planner.cli generate --goal "lose weight" --age 30 --lifestyle moderate --duration 1month
```

| Option | Values | Description |
|---|---|---|
| `--goal` | Any text (required) | Your wellness goal |
| `--age` | Integer (optional) | Your age, for tailored recommendations |
| `--lifestyle` | `sedentary`, `moderate`, `active` | Current activity level |
| `--duration` | `1week`, `1month`, `3months` | How long the plan should cover |

### Interactive Mode

```bash
python -m health_planner.cli interactive
```

### View Milestones

```bash
python -m health_planner.cli milestones --goal "better sleep"
```

### Weekly Check-in

```bash
python -m health_planner.cli checkin
```

### View Progress

```bash
python -m health_planner.cli progress
```

---

## 🌐 Web UI

Launch the Streamlit web interface:

```bash
streamlit run src/health_planner/web_ui.py
```

The web UI features four tabs:

1. **Plan Generator** — Generate and display AI wellness plans
2. **Milestone Tracker** — View week-by-week milestones with progress indicators
3. **Weekly Check-in** — Submit structured weekly check-in questionnaires
4. **Progress Dashboard** — Charts and metrics for energy, sleep, and stress trends

---

## 🧪 Testing

```bash
pytest tests/ -v --tb=short
```

---

## ⚙️ Configuration

Edit `config.yaml` to adjust LLM settings:

```yaml
model: "gemma4"
temperature: 0.4
max_tokens: 3000
```

---

## ⚠️ Disclaimer

**This tool is for INFORMATIONAL and EDUCATIONAL PURPOSES ONLY. The wellness plans generated are general suggestions and may not be appropriate for your specific health situation. Do NOT use this tool as a substitute for professional medical advice, diagnosis, or treatment. ALWAYS consult a qualified healthcare professional before starting any new health, diet, or exercise program.**

---

*Part of the [90 Local LLM Projects](../../README.md) collection.*
