# 💪 Fitness Coach Bot

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![LLM](https://img.shields.io/badge/LLM-Gemma%204-orange)
![License](https://img.shields.io/badge/License-MIT-green)
![UI](https://img.shields.io/badge/UI-Streamlit-red?logo=streamlit)

> AI-powered personal fitness trainer that creates customized workout plans using a local LLM.

## ✨ Features

- **3 Fitness Levels** — Beginner, intermediate, and advanced programs
- **6 Goal Types** — Weight loss, muscle gain, endurance, flexibility, strength, general fitness
- **Equipment Aware** — Plans tailored to your available equipment
- **Workout Logging** — Track exercises, sets, reps, and weights
- **Progress Tracking** — Record body weight and body fat with charts
- **Exercise Library** — Built-in library with muscle groups and difficulty
- **Streamlit Web UI** — Interactive browser-based interface with tabs for plans, logging, and progress
- **Rich CLI Interface** — Beautiful formatted terminal output
- **Safety First** — Includes warm-ups, cool-downs, and injury prevention tips
- **Configurable** — YAML-based settings

## 📦 Installation

```bash
pip install -r requirements.txt
pip install -e .
```

## 🚀 Usage

### CLI

```bash
# Basic usage
python -m fitness_coach.cli --level beginner --goal "weight-loss" --equipment "dumbbells,mat"

# Advanced with custom schedule
python -m fitness_coach.cli --level advanced --goal "muscle-gain" --equipment "barbell,rack" --days 5 --duration 60
```

### Web UI (Streamlit)

```bash
streamlit run src/fitness_coach/web_ui.py
```

### CLI Commands

| Command       | Action                        |
|---------------|-------------------------------|
| `<exercise>`  | Get exercise form details     |
| `log`         | Log a workout                 |
| `progress`    | View progress summary         |
| `library`     | Browse exercise library       |
| `quit`        | Exit the session              |

## 🖼️ Screenshots

*Coming soon — screenshots of both CLI and Web UI.*

## 🧪 Running Tests

```bash
pytest tests/ -v
```

## ⚙️ Configuration

Edit `config.yaml` to customize model, workout defaults, and storage paths.

## 📁 Project Structure

```
04-fitness-coach-bot/
├── src/
│   └── fitness_coach/
│       ├── __init__.py      # Package metadata
│       ├── core.py          # Core business logic
│       ├── cli.py           # Click CLI interface
│       ├── web_ui.py        # Streamlit web interface
│       ├── config.py        # Configuration management
│       └── utils.py         # Workout logging, progress, exercise library
├── tests/
│   ├── __init__.py
│   ├── test_core.py         # Core logic tests
│   └── test_cli.py          # CLI tests
├── config.yaml              # Default configuration
├── setup.py                 # Package setup
├── requirements.txt         # Dependencies
├── Makefile                 # Common commands
├── .env.example             # Example environment variables
└── README.md                # This file
```
