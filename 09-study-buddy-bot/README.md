# 📚 Study Buddy Bot

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![LLM](https://img.shields.io/badge/LLM-Ollama%2FGemma4-orange.svg)
![UI](https://img.shields.io/badge/UI-Streamlit-red.svg)

> AI-powered exam preparation assistant with quizzes, flashcards, study plans, progress tracking, and a Pomodoro timer.

## ✨ Features

- **5 Study Modes** — Quiz, explain, study plan, summarize, flashcards
- **Any Subject** — Works with any academic subject and topic
- **Interactive Q&A** — Ask follow-up questions for deeper understanding
- **Pomodoro Timer** — Built-in study session timer
- **Flashcard Storage** — Save and review flashcard sets
- **Progress Tracking** — Track study time by subject and topic
- **Adaptive Teaching** — Uses Feynman technique and analogies
- **Practice Tests** — Mix of multiple choice, true/false, and short answer
- **Streamlit Web UI** — Full-featured browser interface

## 📦 Installation

```bash
pip install -r requirements.txt
```

## 🚀 CLI Usage

```bash
# Start a study session
python -m study_buddy.cli study --subject "Biology" --topic "Cell Division" --mode explain

# Generate a quiz
python -m study_buddy.cli study --subject "History" --topic "World War 2" --mode quiz

# Start a Pomodoro timer
python -m study_buddy.cli timer --minutes 25

# View study statistics
python -m study_buddy.cli stats

# List saved flashcard sets
python -m study_buddy.cli flashcard-list
```

## 🌐 Web UI

```bash
streamlit run src/study_buddy/web_ui.py
```

The web UI provides:
- 📖 Study sessions with multiple modes
- 📝 Quiz generation with configurable questions
- 🃏 Flashcard creation and review
- ⏱️ Built-in Pomodoro study timer
- 📊 Progress tracking dashboard

## 🧪 Running Tests

```bash
python -m pytest tests/ -v
```

## 📁 Project Structure

```
09-study-buddy-bot/
├── src/
│   └── study_buddy/
│       ├── __init__.py       # Package metadata
│       ├── core.py           # Core business logic
│       ├── cli.py            # Click CLI interface
│       ├── web_ui.py         # Streamlit web interface
│       ├── config.py         # Configuration management
│       └── utils.py          # Helper utilities
├── tests/
│   ├── __init__.py
│   ├── test_core.py          # Core logic tests
│   └── test_cli.py           # CLI tests
├── config.yaml               # Default configuration
├── setup.py                  # Package setup
├── requirements.txt          # Dependencies
├── Makefile                  # Common commands
├── .env.example              # Example environment variables
└── README.md                 # This file
```
