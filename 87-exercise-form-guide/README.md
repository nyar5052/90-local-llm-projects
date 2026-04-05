# 🏋️ Exercise Form Guide

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](#testing)

**AI-powered exercise form instructions, muscle databases, progression paths, and warm-up/cool-down routines — powered by a local LLM via Ollama.**

---

> ⚠️ **IMPORTANT MEDICAL DISCLAIMER**
>
> This tool provides AI-generated exercise guidance for **educational purposes only**. It is **NOT medical advice**. Always consult a qualified fitness professional or physician before starting any exercise program. Improper form can lead to **serious injury**. The creators of this tool assume **no liability** for injuries or health issues resulting from the use of this information.

---

## ✨ Features

- 🏋️ **Exercise Guides** — Step-by-step form instructions with target muscles, common mistakes, breathing cues, progressions/regressions, and safety tips
- 💪 **Muscle Group Database** — Detailed info on 7 muscle groups with muscles, descriptions, and common exercises
- 📈 **Progression Paths** — Beginner-to-advanced exercise progressions for push-ups, squats, pull-ups, planks, and deadlifts
- 🔥 **Warm-up Routines** — Targeted warm-up exercises for each muscle group
- 🧘 **Cool-down Stretches** — Post-workout stretching routines by muscle group
- 🎯 **Goal-based Routines** — Weekly workout plans for strength, hypertrophy, endurance, or flexibility
- 🖥️ **Rich CLI** — Beautiful terminal output with panels, tables, and Markdown
- 🌐 **Streamlit Web UI** — Browser-based interface for all features

## 🏗️ Architecture

```
User ─── CLI (click) ──── core.py ──── Ollama LLM
     └── Web UI (streamlit) ──┘           │
                                    Local Model
                                   (e.g. llama3)
```

## 📋 Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) running locally with a model pulled (e.g., `ollama pull llama3`)

## 🚀 Installation

```bash
# Clone and navigate to the project
cd 87-exercise-form-guide

# Install in development mode
pip install -e ".[dev]"

# Or install dependencies directly
pip install -r requirements.txt
```

## 💻 CLI Usage

### Get Exercise Form Guide

```bash
exercise-guide guide --exercise "deadlift" --level intermediate
exercise-guide guide --exercise "bench press" --level beginner
exercise-guide guide --exercise "pull-up" --level advanced
```

### List Exercises by Muscle Group

```bash
exercise-guide list --muscle-group legs
exercise-guide list --muscle-group chest
exercise-guide list --muscle-group core
```

### Generate Workout Routine

```bash
exercise-guide routine --goal strength --level beginner
exercise-guide routine --goal hypertrophy --level intermediate
exercise-guide routine --goal flexibility --level advanced
```

### Show Warm-up Routine

```bash
exercise-guide warmup --muscle-group chest
exercise-guide warmup --muscle-group legs
```

### Show Cool-down Stretches

```bash
exercise-guide cooldown --muscle-group back
exercise-guide cooldown --muscle-group shoulders
```

### Show Exercise Progression

```bash
exercise-guide progression --exercise push-up
exercise-guide progression --exercise squat
exercise-guide progression --exercise pull-up
```

### Show Muscle Group Info

```bash
exercise-guide muscles --group chest
exercise-guide muscles --group legs
```

**Available options:**
- Levels: `beginner`, `intermediate`, `advanced`
- Muscle groups: `legs`, `chest`, `back`, `shoulders`, `arms`, `core`, `full body`
- Goals: `strength`, `hypertrophy`, `endurance`, `flexibility`
- Progressions: `push-up`, `squat`, `pull-up`, `plank`, `deadlift`

## 🌐 Web UI

Launch the Streamlit web interface:

```bash
streamlit run src/exercise_guide/web_ui.py
```

The web UI provides four pages:
- **🏋️ Exercise Guide** — Enter any exercise and get AI-powered form instructions
- **💪 Muscle Groups** — Browse the muscle group database
- **📈 Progression Paths** — Visualize exercise progressions from beginner to advanced
- **🔥 Warm-up/Cool-down** — View warm-up and cool-down routines in table format

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v --tb=short

# Run with coverage
python -m pytest tests/ -v --cov=exercise_guide --cov-report=term-missing
```

## 📁 Project Structure

```
87-exercise-form-guide/
├── src/
│   └── exercise_guide/
│       ├── __init__.py        # Package init with version
│       ├── core.py            # Core logic, data, LLM functions
│       ├── cli.py             # Click CLI interface
│       └── web_ui.py          # Streamlit web interface
├── tests/
│   ├── __init__.py
│   ├── test_core.py           # Core logic and data tests
│   └── test_cli.py            # CLI command tests
├── app.py                     # Legacy CLI entry point
├── test_app.py                # Legacy tests
├── config.yaml                # Application configuration
├── setup.py                   # Package setup
├── requirements.txt           # Python dependencies
├── Makefile                   # Common tasks
├── .env.example               # Environment variable template
└── README.md                  # This file
```

## ⚙️ Configuration

Copy `.env.example` to `.env` and adjust:

```bash
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3
LOG_LEVEL=INFO
```

See `config.yaml` for additional configuration options.

## 📄 License

Part of the 90 Local LLM Projects collection.

---

> ⚠️ **DISCLAIMER**: This tool is for **educational purposes only** and is **NOT medical advice**. Always consult a qualified fitness professional or physician before starting any exercise program. Improper form can lead to serious injury. Use at your own risk.
