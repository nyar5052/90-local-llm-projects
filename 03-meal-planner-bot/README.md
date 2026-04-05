# 🍽️ Meal Planner Bot

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![LLM](https://img.shields.io/badge/LLM-Gemma%204-orange)
![License](https://img.shields.io/badge/License-MIT-green)
![UI](https://img.shields.io/badge/UI-Streamlit-red?logo=streamlit)

> Generate personalized weekly meal plans with detailed recipes using a local LLM.

## ✨ Features

- **10 Diet Types** — Omnivore, vegetarian, vegan, keto, paleo, and more
- **Allergy Aware** — Specify allergies to exclude dangerous ingredients
- **Calorie Targets** — Set daily calorie goals with automatic tracking
- **Shopping List Generation** — Consolidated grocery list from your meal plan
- **Recipe Saving** — Save favorite recipes to JSON for future reference
- **Detailed Recipes** — Get full recipes with ingredients, steps, and nutrition info
- **Streamlit Web UI** — Interactive browser-based interface with tabs
- **Rich CLI Interface** — Beautiful formatted terminal output
- **Configurable** — YAML-based settings

## 📦 Installation

```bash
pip install -r requirements.txt
pip install -e .
```

## 🚀 Usage

### CLI

```bash
# Basic 7-day vegetarian plan
python -m meal_planner.cli --diet vegetarian --days 7

# Keto plan with allergies
python -m meal_planner.cli --diet keto --days 5 --allergies "nuts,dairy"

# Vegan plan with calorie target
python -m meal_planner.cli --diet vegan --days 7 --calories 1800
```

### Web UI (Streamlit)

```bash
streamlit run src/meal_planner/web_ui.py
```

### CLI Commands

| Command          | Action                      |
|------------------|-----------------------------|
| `<meal name>`    | Get detailed recipe         |
| `shop`           | Generate shopping list      |
| `quit`           | Exit the session            |

## 🖼️ Screenshots

*Coming soon — screenshots of both CLI and Web UI.*

## 🧪 Running Tests

```bash
pytest tests/ -v
```

## ⚙️ Configuration

Edit `config.yaml` to customize model, storage paths, and defaults.

## 📁 Project Structure

```
03-meal-planner-bot/
├── src/
│   └── meal_planner/
│       ├── __init__.py      # Package metadata
│       ├── core.py          # Core business logic
│       ├── cli.py           # Click CLI interface
│       ├── web_ui.py        # Streamlit web interface
│       ├── config.py        # Configuration management
│       └── utils.py         # Shopping list, calorie tracking, recipe saving
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
