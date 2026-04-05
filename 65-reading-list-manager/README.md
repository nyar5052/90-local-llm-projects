# 📚 Reading List Manager

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)]()
[![Code style: PEP8](https://img.shields.io/badge/code%20style-pep8-orange.svg)]()

> AI-powered reading list management with book summaries, personalized recommendations, reading goals, and a Streamlit web UI — all powered by a local LLM via Ollama.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📖 **Book Management** | Add, list, rate, and track books with rich status indicators |
| 🤖 **AI Summaries** | Comprehensive AI-generated book summaries via Ollama |
| 🔮 **Smart Recommendations** | AI + pure-Python genre/rating-based recommendations |
| 📊 **Reading Analysis** | AI-driven insights into your reading habits |
| 📈 **Progress Tracking** | Track pages read and percent complete per book |
| ⭐ **Ratings & Reviews** | Rate books 1-5 and leave written reviews |
| 🎯 **Reading Goals** | Set yearly goals and track progress |
| 🏃 **Reading Speed** | Pages-per-day calculator per book |
| 📋 **TBR Management** | Prioritize your to-be-read list |
| 🌐 **Web UI** | Full Streamlit dashboard with charts and forms |
| ⚙️ **YAML Config** | Centralized configuration via `config.yaml` |

---

## 🏗️ Architecture

```
65-reading-list-manager/
├── src/
│   └── reading_list/
│       ├── __init__.py        # Package metadata & version
│       ├── core.py            # All business logic & data functions
│       ├── cli.py             # Click CLI interface
│       └── web_ui.py          # Streamlit web dashboard
├── tests/
│   ├── __init__.py
│   └── test_core.py           # Comprehensive test suite
├── data/                      # JSON data storage (auto-created)
├── config.yaml                # Application configuration
├── setup.py                   # Package installer (entry point)
├── Makefile                   # Common dev tasks
├── requirements.txt           # Python dependencies
├── .env.example               # Environment template
└── README.md
```

---

## 🚀 Installation

### Prerequisites

- **Python 3.10+**
- **[Ollama](https://ollama.ai/)** running locally with a model (e.g. `llama3`)

### Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Or install as a package (includes CLI entry point)
pip install -e ".[dev]"

# Verify Ollama is running
ollama list
```

---

## 💻 CLI Usage

All commands are available via the CLI:

### Add a Book
```bash
python src/reading_list/cli.py add -t "Clean Code" -a "Robert Martin" -g "Technical" -p 464
```

### List Books
```bash
python src/reading_list/cli.py list
python src/reading_list/cli.py list --status reading
```

### Update Reading Progress
```bash
python src/reading_list/cli.py progress --book-id 1 --pages 150
```

### Rate a Book
```bash
python src/reading_list/cli.py rate --book-id 1 --rating 5 --review "Essential for developers"
```

### Get AI Recommendations
```bash
python src/reading_list/cli.py recommend --genre "Science Fiction"
```

### Get Book Summary
```bash
python src/reading_list/cli.py summary -t "Dune" -a "Frank Herbert"
```

### Analyze Reading Habits
```bash
python src/reading_list/cli.py analyze
```

### Genre Statistics
```bash
python src/reading_list/cli.py stats
```

### Reading Goals
```bash
# Set a goal
python src/reading_list/cli.py goal --year 2025 --target 30

# Check progress
python src/reading_list/cli.py goal
```

---

## 🌐 Web UI

Launch the Streamlit dashboard:

```bash
streamlit run src/reading_list/web_ui.py
```

### Pages

| Page | What it does |
|---|---|
| **➕ Add Book** | Form to add books with title, author, genre, pages, status |
| **📖 My Library** | Filterable book list with inline progress & rating controls |
| **🔮 Recommendations** | AI recommendations + similarity-based suggestions |
| **📊 Reading Stats** | Goal tracker, genre bar chart, rating distribution, speed stats |

---

## 🎯 Reading Goals Guide

1. **Set a goal**: `python src/reading_list/cli.py goal -y 2025 -t 24`
2. **Track progress**: `python src/reading_list/cli.py goal` shows a progress bar
3. **Mark books complete**: Use `progress` command to hit 100%
4. **Web dashboard**: See real-time goal progress with pace calculations

---

## ⚙️ Configuration

Edit `config.yaml` to customize:

- **Statuses**: to-read, reading, completed, dropped, on-hold
- **Genres**: Fiction, Sci-Fi, Technical, etc.
- **LLM settings**: model, temperature, system prompt
- **Goals**: default yearly target, pages per session

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=src/reading_list --cov-report=term-missing
```

---

## 📝 Status Emojis

| Status | Emoji |
|---|---|
| to-read | 📋 |
| reading | 📖 |
| completed | ✅ |
| dropped | ❌ |
| on-hold | ⏸️ |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests (`pytest tests/ -v`)
4. Commit your changes (`git commit -m "Add amazing feature"`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

---

## 📄 License

MIT
