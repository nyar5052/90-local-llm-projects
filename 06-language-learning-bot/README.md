# 🌍 Language Learning Bot

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![LLM](https://img.shields.io/badge/LLM-Ollama%2FGemma4-orange.svg)
![UI](https://img.shields.io/badge/UI-Streamlit-red.svg)

> Practice conversations in 15+ languages with an AI tutor that corrects grammar, teaches vocabulary, and tracks your progress.

## ✨ Features

- **15 Languages** — Spanish, French, German, Japanese, Korean, and more
- **3 Proficiency Levels** — Beginner, intermediate, and advanced
- **Conversational Practice** — Natural dialogue with corrections
- **Grammar Explanations** — Learn rules as you practice
- **Mini Lessons** — On-demand lessons on specific topics
- **Vocabulary Tracker** — Save, review, and quiz on learned words
- **Pronunciation Tips** — Get phonetic breakdowns and mouth positioning
- **Lesson Plan Generator** — Multi-week structured learning plans
- **Progress Tracking** — Session history and time tracking
- **Streamlit Web UI** — Full-featured browser interface
- **Translation Help** — Quick translations on demand

## 📦 Installation

```bash
pip install -r requirements.txt
```

## 🚀 CLI Usage

```bash
# Start a conversation practice session
python -m language_learner.cli chat-cmd --language spanish --level beginner

# Generate a lesson plan
python -m language_learner.cli lesson-plan --language french --level intermediate --weeks 4

# Take a vocabulary quiz
python -m language_learner.cli quiz --language spanish

# View learning progress
python -m language_learner.cli progress-cmd --language spanish
```

### Chat Commands

| Command | Description |
|---------|-------------|
| `/lesson <topic>` | Get a mini lesson on a topic |
| `/translate <text>` | Translate text |
| `/vocab` | Get useful vocabulary |
| `/pronounce <word>` | Get pronunciation tips |
| `/add <word> = <translation>` | Add to vocabulary tracker |
| `/my-vocab` | Show saved vocabulary |
| `/progress` | Show learning progress |
| `quit` | Exit the app |

## 🌐 Web UI

```bash
streamlit run src/language_learner/web_ui.py
```

The web UI provides:
- 💬 Interactive chat with language tutor
- 📖 Vocabulary management and quizzes
- 📚 Lesson and lesson plan generation
- 📊 Progress tracking dashboard

## 🧪 Running Tests

```bash
python -m pytest tests/ -v
```

## 📁 Project Structure

```
06-language-learning-bot/
├── src/
│   └── language_learner/
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
