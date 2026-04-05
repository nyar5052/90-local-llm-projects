# 📔 Mood Journal Bot

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![LLM](https://img.shields.io/badge/LLM-Ollama%2FGemma4-orange.svg)
![UI](https://img.shields.io/badge/UI-Streamlit-red.svg)

> Private mood tracking with AI-powered insights, mood charts, gratitude prompts, and data export — all stored locally.

## ✨ Features

- **10 Mood Options** — Happy, calm, neutral, sad, angry, anxious, stressed, grateful, tired, excited
- **Energy Tracking** — Rate your energy level alongside mood
- **Gratitude Journaling** — Optional gratitude prompts with each entry
- **AI Analysis** — Get insights on mood patterns and trends
- **Mood Charts** — Visualize mood and energy trends over time
- **Weekly/Monthly Reports** — Automated report generation
- **Export** — Export entries to CSV or JSON
- **Local Storage** — All entries stored privately on your machine
- **Statistics** — Mood distributions and averages
- **Streamlit Web UI** — Full-featured browser interface with charts

## 📦 Installation

```bash
pip install -r requirements.txt
```

## 🚀 CLI Usage

```bash
# Write a new journal entry
python -m mood_journal.cli journal

# Analyze mood patterns (last 7 days)
python -m mood_journal.cli analyze --days 7

# View recent entries
python -m mood_journal.cli history --days 14

# View all-time statistics
python -m mood_journal.cli stats

# Generate reports
python -m mood_journal.cli weekly-report
python -m mood_journal.cli monthly-report

# Get a gratitude prompt
python -m mood_journal.cli gratitude

# Export entries
python -m mood_journal.cli export --output journal.csv --days 30
```

## 🌐 Web UI

```bash
streamlit run src/mood_journal/web_ui.py
```

The web UI provides:
- 📝 Journal entry form with mood selection and gratitude
- 📊 Interactive mood and energy charts
- 🧠 AI-powered mood analysis and insights
- 📊 Weekly and monthly reports
- 📤 Export to CSV and JSON download

## 🧪 Running Tests

```bash
python -m pytest tests/ -v
```

## 📁 Project Structure

```
10-mood-journal-bot/
├── src/
│   └── mood_journal/
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

## 🔒 Privacy

All journal entries are stored locally in `journal_entries.json`. No data is ever sent to external servers. The AI analysis runs entirely on your local machine via Ollama.
