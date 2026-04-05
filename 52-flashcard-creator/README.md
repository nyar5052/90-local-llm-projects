# 🗂️ Flashcard Creator

![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![License MIT](https://img.shields.io/badge/License-MIT-green)
![Version 1.0.0](https://img.shields.io/badge/Version-1.0.0-orange)
![Spaced Repetition](https://img.shields.io/badge/Algorithm-SM--2-purple)

> **Production-grade flashcard creation and review system powered by a local LLM with spaced repetition (SM-2), deck management, import/export, CLI, and Streamlit web UI.**

---

## 📋 Description

Flashcard Creator turns any topic into study-ready flashcards using a local LLM
(via Ollama). It goes far beyond simple Q&A generation — cards are organised into
decks, reviewed with the proven SM-2 spaced-repetition algorithm, and tracked
over time so you study *what you need, when you need it*.

---

## 🏛️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                   User Interface                     │
│  ┌──────────────┐          ┌──────────────────────┐  │
│  │   CLI (Click)│          │  Web UI (Streamlit)  │  │
│  └──────┬───────┘          └──────────┬───────────┘  │
│         │                             │              │
│  ┌──────┴─────────────────────────────┴───────────┐  │
│  │              Core Business Logic               │  │
│  │  ┌───────────┐ ┌────────────┐ ┌─────────────┐  │  │
│  │  │ Flashcard │ │   Deck     │ │   Spaced    │  │  │
│  │  │ Generator │ │  Manager   │ │ Repetition  │  │  │
│  │  └─────┬─────┘ └────────────┘ │   (SM-2)    │  │  │
│  │        │                      └─────────────┘  │  │
│  └────────┼───────────────────────────────────────┘  │
│           │                                          │
│  ┌────────┴──────────┐     ┌──────────────────────┐  │
│  │  LLM Client       │     │  Storage (JSON/CSV) │  │
│  │  (Ollama / local) │     │  ./decks/            │  │
│  └───────────────────┘     └──────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 **LLM Generation** | Generate flashcards from any topic using a local LLM |
| 🧠 **Spaced Repetition (SM-2)** | Science-backed review scheduling for optimal retention |
| 📚 **Deck Management** | Create, delete, merge, and browse decks |
| 📤 **Import / Export** | JSON and CSV support for portability |
| 🎯 **Difficulty Tagging** | Easy, medium, and hard difficulty levels |
| 💻 **CLI Interface** | Full-featured command-line tool with Click |
| 🌐 **Streamlit Web UI** | Beautiful browser-based interface |
| 🔄 **Interactive Review** | Flip-card experience with quality ratings (0-5) |
| 📊 **Statistics** | Track progress, mastery, ease factors, and intervals |
| ⚙️ **Configurable** | YAML-based configuration for all settings |

---

## 🚀 Quick Start

```bash
# 1. Make sure Ollama is running
ollama serve

# 2. Install dependencies
pip install -r requirements.txt

# 3. Generate flashcards
python -m flashcard_creator.cli create --topic "Python Decorators" --count 10

# 4. Or launch the web UI
streamlit run src/flashcard_creator/web_ui.py
```

---

## 📦 Installation

### From source

```bash
git clone <repo-url>
cd 52-flashcard-creator

# Install in development mode
pip install -e ".[dev]"
```

### Requirements

- **Python 3.10+**
- **Ollama** running locally (`ollama serve`)
- A pulled model (e.g. `ollama pull llama3`)

---

## 💻 CLI Usage

The CLI is built with [Click](https://click.palletsprojects.com/) and offers
six commands:

### Create flashcards

```bash
# Basic usage
flashcard-creator create --topic "Machine Learning" --count 15

# Specify difficulty and save to a deck
flashcard-creator create -t "SQL Joins" -c 10 -d hard --deck-name "SQL Mastery"

# Export to a specific file
flashcard-creator create -t "Docker" -o docker_cards.json
```

### Review a deck

```bash
# Interactive review session
flashcard-creator review --deck "SQL Mastery"

# Review only cards due for review (spaced repetition)
flashcard-creator review --deck "SQL Mastery" --due-only

# Disable shuffling
flashcard-creator review --deck "SQL Mastery" --no-shuffle
```

### List decks

```bash
flashcard-creator decks
```

### Import a deck

```bash
flashcard-creator import-deck --file cards.json --format json
flashcard-creator import-deck --file cards.csv --format csv
```

### Export a deck

```bash
flashcard-creator export-deck --deck "My Deck" --format json --output export.json
flashcard-creator export-deck --deck "My Deck" --format csv --output export.csv
```

### View statistics

```bash
flashcard-creator stats --deck "SQL Mastery"
```

---

## 🌐 Web UI

Launch the Streamlit-based web interface:

```bash
streamlit run src/flashcard_creator/web_ui.py
```

The Web UI offers four modes accessible from the sidebar:

| Mode | Description |
|------|-------------|
| **Create Cards** | Enter a topic, choose count and difficulty, generate cards, edit inline, save to deck |
| **Review Mode** | Select a deck, flip cards, rate recall (0-5), view session summary |
| **Deck Browser** | Browse all decks, search cards by keyword, filter by tag |
| **Statistics** | Cards-per-deck chart, difficulty breakdown, mastery progress, SM-2 metrics |

---

## 🧠 Spaced Repetition — SM-2 Algorithm

The SM-2 algorithm optimises your review schedule so you spend time on cards you
find hardest while letting well-known cards rest longer.

### How it works

After each card review, you rate your recall quality on a **0–5** scale:

| Grade | Meaning |
|-------|---------|
| 0 | Complete blackout |
| 1 | Incorrect — remembered after seeing answer |
| 2 | Incorrect — answer seemed easy to recall |
| 3 | Correct with serious difficulty |
| 4 | Correct with some hesitation |
| 5 | Perfect recall |

### SM-2 Formulas

```
New EF = EF + (0.1 − (5 − q) × (0.08 + (5 − q) × 0.02))

If quality ≥ 3 (pass):
  rep 0 → interval = 1 day
  rep 1 → interval = 6 days
  rep n → interval = prev_interval × EF

If quality < 3 (fail):
  repetitions reset to 0
  interval reset to 1 day
```

The **ease factor** (EF) never drops below `1.3` (configurable).

---

## ⚙️ Configuration

All settings live in `config.yaml`:

```yaml
llm:
  temperature: 0.7          # LLM creativity
  max_tokens: 4096           # Max response length

flashcards:
  default_count: 10          # Cards per generation
  default_difficulty: medium # Default difficulty level
  max_cards_per_deck: 500    # Safety limit

spaced_repetition:
  algorithm: sm2
  initial_ease_factor: 2.5   # Starting ease factor
  minimum_ease_factor: 1.3   # Floor for ease factor
  initial_interval: 1        # Days before first review
  graduating_interval: 6     # Days after second correct answer

storage:
  decks_dir: ./decks         # Where decks are saved
  stats_file: review_stats.json

logging:
  level: INFO                # DEBUG, INFO, WARNING, ERROR
  file: flashcard_creator.log
```

Environment variables (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `llama3` | Model to use |
| `LOG_LEVEL` | `INFO` | Logging level |
| `DECKS_DIR` | `./decks` | Deck storage directory |

---

## 🏗️ Project Structure

```
52-flashcard-creator/
├── src/
│   └── flashcard_creator/
│       ├── __init__.py        # Package metadata & version
│       ├── core.py            # Business logic, SM-2, deck management
│       ├── cli.py             # Click CLI commands
│       └── web_ui.py          # Streamlit web interface
├── tests/
│   ├── __init__.py
│   ├── test_core.py           # Core logic & SM-2 tests
│   └── test_cli.py            # CLI command tests
├── config.yaml                # Application configuration
├── setup.py                   # Package setup
├── requirements.txt           # Python dependencies
├── Makefile                   # Common tasks
├── .env.example               # Environment variable template
└── README.md                  # This file
```

---

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v --tb=short

# Run with coverage
python -m pytest tests/ --cov=src/flashcard_creator --cov-report=term-missing

# Run only core tests
python -m pytest tests/test_core.py -v

# Run only CLI tests
python -m pytest tests/test_cli.py -v
```

Tests mock the LLM client so they run **without Ollama**.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
