# 🎯 Habit Tracker Analyzer

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Track daily habits, earn achievements, visualize streaks, and get AI-powered analysis of patterns using a local LLM via Ollama.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔥 **Streak Tracking** | Current, best, and total streaks for every habit |
| 🏅 **Achievement System** | Unlock badges for milestones (7-day, 30-day, 100-day streaks, and more) |
| 🔗 **Correlation Analysis** | Discover which habits you complete together |
| 🤖 **AI Insights** | LLM-powered analysis of your patterns with actionable advice |
| 📅 **Calendar Heatmap** | GitHub-style contribution calendar for each habit |
| 📊 **Weekly/Monthly Reports** | Auto-generated summary reports with progress bars |
| 🏷️ **Categories & Goals** | Organize habits by category with daily/weekly targets |
| 🖥️ **Web Dashboard** | Interactive Streamlit UI with Plotly charts |

## 🏗️ Architecture

```
68-habit-tracker-analyzer/
├── src/habit_tracker/
│   ├── __init__.py          # Package version
│   ├── core.py              # Business logic, analytics, AI
│   ├── cli.py               # Rich CLI (Click)
│   └── web_ui.py            # Streamlit web dashboard
├── tests/
│   ├── __init__.py
│   └── test_core.py         # Comprehensive test suite
├── config.yaml              # Configuration
├── setup.py                 # Package setup
├── Makefile                 # Dev targets
├── .env.example             # Environment template
├── requirements.txt
└── README.md
```

## 🚀 Installation

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) running locally (for AI analysis)

### Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Or install as a package (editable)
pip install -e ".[dev]"

# Copy and configure environment
cp .env.example .env
```

## 💻 CLI Usage

### Add a Habit

```bash
habit-tracker add --name "Exercise" --category fitness --target daily
habit-tracker add --name "Reading" --category learning
```

### Log a Habit

```bash
habit-tracker log --habit "Exercise" --done
habit-tracker log --habit "Reading" --done --notes "Read 30 pages"
habit-tracker log --habit "Meditation" --skip
```

### View Status

```bash
habit-tracker status
```

### View Achievements

```bash
habit-tracker achievements
```

### Generate Reports

```bash
habit-tracker report --type weekly
habit-tracker report --type monthly
```

### AI Analysis

```bash
habit-tracker analyze --period month
habit-tracker analyze --period week
habit-tracker analyze --period year
```

### Delete a Habit

```bash
habit-tracker delete --habit exercise
```

### Flags

| Flag | Description |
|------|-------------|
| `--verbose / -v` | Enable verbose output |
| `--config / -c` | Path to config YAML (default: `config.yaml`) |

## 🌐 Web UI

Launch the interactive Streamlit dashboard:

```bash
streamlit run src/habit_tracker/web_ui.py
```

**Pages:**

- **Log Habits** — Log existing habits or add new ones, view today's summary
- **Dashboard** — Streak calendar heatmap, completion rate bars, quick stats
- **Analytics** — Period-based charts, habit correlation matrix, AI analysis
- **Achievements** — Achievement gallery with progress bars

## 🏅 Achievement System

| Badge | Name | Requirement |
|-------|------|-------------|
| 🌱 | First Step | Log your first habit |
| 🔥 | Week Warrior | 7-day streak |
| ⭐ | Monthly Master | 30-day streak |
| 💯 | Century Club | 100-day streak |
| 🏆 | Perfect Week | All habits done for 7 consecutive days |
| 👑 | Consistency King | 90%+ completion rate over 30 days |

## ⚙️ Configuration

Edit `config.yaml`:

```yaml
llm:
  model: "llama3.2"
  temperature: 0.6
  max_tokens: 2000

habits_file: "habits.json"
default_target: "daily"

achievements:
  enabled: true
  notifications: true

reports:
  weekly: true
  monthly: true

logging:
  level: "INFO"
  file: "habit_tracker.log"
```

Environment variables (`.env`):

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama API endpoint |
| `OLLAMA_MODEL` | `llama3.2` | LLM model name |
| `LOG_LEVEL` | `INFO` | Logging level |
| `HABIT_TRACKER_CONFIG` | `config.yaml` | Config file path |

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --tb=short
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for new functionality
4. Ensure all tests pass (`pytest tests/ -v`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

MIT
