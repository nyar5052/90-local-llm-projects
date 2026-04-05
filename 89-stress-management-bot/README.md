# 🧘 Stress Management Bot

![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)
![LLM: Ollama](https://img.shields.io/badge/LLM-Ollama-orange)

An AI-powered, production-grade stress management companion with CLI and web interfaces. Built on a local LLM via Ollama — **all data stays on your machine**.

---

> ## ⚠️ IMPORTANT MENTAL HEALTH DISCLAIMER
>
> **This tool is NOT a substitute for professional mental health care.**
> It provides general wellness suggestions only and is **NOT medical advice**.
>
> ### 🆘 If you are in crisis, please contact immediately:
>
> | Service | Contact |
> |---------|---------|
> | **988 Suicide & Crisis Lifeline** | **Call or text 988** |
> | **Crisis Text Line** | **Text HOME to 741741** |
> | **Emergency Services** | **Call 911** |
> | **International Association for Suicide Prevention** | https://www.iasp.info/resources/Crisis_Centres/ |

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📊 **Stress Assessment** | Detailed scoring with severity breakdown and recommendations |
| 🌬️ **Breathing Exercises** | Guided Box Breathing and 4-7-8 with animated progress |
| 📝 **Journaling** | AI-generated prompts with free-writing space |
| 📋 **CBT Worksheets** | Thought Record, Behavioral Activation, Worry Time |
| 🛠️ **Coping Toolkit** | Physical, cognitive, social, and creative techniques |
| 🤖 **AI Chat** | CBT-based interactive stress management conversation |

### 📊 Stress Assessment
Answer 5 questions (stress, sleep, energy, anxiety, concentration) and receive a detailed score with severity rating (low/moderate/high/critical), category breakdown, and personalised recommendations.

### 🌬️ Breathing Exercises
- **Box Breathing** (4-4-4-4) — used by Navy SEALs for stress reduction
- **4-7-8 Breathing** — promotes calm and sleep

### 📝 Journaling
Receive a thoughtful AI-generated prompt and write freely. Entries are displayed back for reflection.

### 📋 CBT Worksheets
- **Thought Record** — identify and challenge automatic negative thoughts
- **Behavioral Activation** — schedule and track uplifting activities
- **Worry Time** — contain worry with a structured process

### 🛠️ Coping Toolkit
Evidence-based techniques in four categories: Physical, Cognitive, Social, and Creative.

### 🤖 AI Chat
Interactive conversation powered by CBT, mindfulness, and positive psychology.

---

## 🏗️ Architecture

```
89-stress-management-bot/
├── src/
│   ├── __init__.py
│   └── stress_manager/
│       ├── __init__.py          # Package metadata
│       ├── core.py              # Core logic, constants, scoring
│       ├── cli.py               # Click CLI interface
│       └── web_ui.py            # Streamlit web interface
├── tests/
│   ├── __init__.py
│   ├── test_core.py             # Core logic tests
│   └── test_cli.py              # CLI command tests
├── app.py                       # Legacy entry point
├── test_app.py                  # Legacy tests
├── config.yaml                  # Configuration
├── setup.py                     # Package setup
├── requirements.txt             # Dependencies
├── Makefile                     # Build automation
├── .env.example                 # Environment template
└── README.md
```

---

## 🚀 Installation

### Prerequisites

- **Python 3.10+**
- [Ollama](https://ollama.ai/) running locally with a model pulled:
  ```bash
  ollama pull llama3
  ```

### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Or install as editable package (recommended)
pip install -e ".[dev]"
```

---

## 💻 CLI Usage

```bash
# Interactive AI chat
stress-manager chat

# Guided breathing exercise
stress-manager breathe
stress-manager breathe --technique box
stress-manager breathe --technique 478

# Journaling with AI prompt
stress-manager journal

# Stress assessment (with LLM recommendations)
stress-manager assess

# Detailed stress scoring (no LLM required)
stress-manager score

# CBT worksheets
stress-manager worksheet --type thought_record
stress-manager worksheet --type behavioral_activation
stress-manager worksheet --type worry_time

# Coping suggestions by stress level
stress-manager coping --level low
stress-manager coping --level moderate
stress-manager coping --level high

# Full coping toolkit
stress-manager toolkit
```

Or run directly:

```bash
python -m stress_manager.cli chat
python -m stress_manager.cli score
```

---

## 🌐 Web UI

Launch the Streamlit web interface:

```bash
streamlit run src/stress_manager/web_ui.py
```

The web UI provides:
- Interactive sliders for stress assessment with live scoring
- Animated breathing exercise countdown
- Coping toolkit with category filters
- Journal with persistent entries
- CBT worksheet forms

---

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v --tb=short

# With coverage
python -m pytest tests/ -v --cov=stress_manager --tb=short
```

---

## ⚙️ Configuration

Edit `config.yaml` to customise LLM model, temperature, and logging.

Environment variables (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama API endpoint |
| `OLLAMA_MODEL` | `llama3` | LLM model name |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

---

## 🔒 Privacy

All processing happens **locally** on your machine. No data is sent to external servers. The LLM runs via Ollama on localhost.

---

## ⚠️ Disclaimer

**This tool is for educational and wellness purposes only. It is NOT a substitute for professional mental health care and does NOT provide medical advice.**

### 🆘 Crisis Resources

If you or someone you know is in crisis:

- **988 Suicide & Crisis Lifeline**: Call or text **988**
- **Crisis Text Line**: Text **HOME** to **741741**
- **Emergency Services**: Call **911**
- **NAMI Helpline**: 1-800-950-NAMI (6264)
- **SAMHSA Helpline**: 1-800-662-4357

*Always consult a licensed mental health professional for clinical care.*
