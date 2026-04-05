# 📔 Diary Journal Organizer

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)
![Ollama](https://img.shields.io/badge/LLM-Ollama-orange)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-red?logo=streamlit)
![Tests](https://img.shields.io/badge/Tests-Pytest-yellow?logo=pytest)

Private diary with **AI-powered insights**, mood tracking, theme discovery, and streak analytics — powered by a **local LLM** via Ollama. Your data never leaves your machine.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| ✍️ **Daily Journal Entries** | Write and store private diary entries with mood and tags |
| 🎭 **Mood Tracking** | 16 mood states with emoji visualization |
| 🔍 **Theme Discovery** | AI + keyword frequency analysis of recurring themes |
| 📊 **Mood Statistics** | Counts, percentages, and distribution charts |
| ☁️ **Word Cloud Data** | Word frequency analysis for visual exploration |
| 📅 **Monthly Reflections** | AI-generated monthly summaries |
| 🔥 **Writing Streaks** | Track consecutive writing days |
| 🌐 **Web Dashboard** | Streamlit UI with charts and interactive views |
| 🖥️ **CLI Interface** | Full-featured Click CLI |
| 🔒 **Privacy First** | 100% local — data + AI on your machine |

### 🎭 Supported Moods

| Mood | Emoji | Mood | Emoji |
|------|-------|------|-------|
| Happy | 😊 | Nostalgic | 🥹 |
| Sad | 😢 | Inspired | ✨ |
| Anxious | 😰 | Peaceful | 🕊️ |
| Calm | 😌 | Loved | ❤️ |
| Excited | 🎉 | Proud | 🏆 |
| Angry | 😤 | Confused | 😕 |
| Grateful | 🙏 | Hopeful | 🌅 |
| Tired | 😴 | Creative | 🎨 |

---

## 🏗️ Architecture

```
63-diary-journal-organizer/
├── src/
│   └── diary_organizer/
│       ├── __init__.py          # Package metadata
│       ├── core.py              # Core logic, AI functions, analytics
│       ├── cli.py               # Click CLI interface
│       └── web_ui.py            # Streamlit web dashboard
├── tests/
│   ├── __init__.py
│   └── test_core.py             # Comprehensive test suite
├── data/                        # Diary JSON storage (auto-created)
├── config.yaml                  # App configuration
├── setup.py                     # Package setup with entry point
├── requirements.txt             # Dependencies
├── Makefile                     # Dev workflow shortcuts
├── .env.example                 # Environment variables template
└── README.md
```

---

## 📋 Prerequisites

- **Python 3.10+**
- **[Ollama](https://ollama.ai/)** running locally
  ```bash
  ollama serve
  ollama pull llama3
  ```

---

## 🚀 Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or install as package (with CLI entry point)
pip install -e .

# For development
pip install -e ".[dev]"
```

---

## 🖥️ CLI Usage

### Write a New Entry
```bash
python src/diary_organizer/cli.py write --content "Had a wonderful day hiking" --mood happy --tags "outdoors,friends"
```

### Interactive Writing
```bash
python src/diary_organizer/cli.py write
```

### View Recent Entries
```bash
python src/diary_organizer/cli.py view --period week --last 5
```

### Get AI Insights
```bash
python src/diary_organizer/cli.py insights --period month
python src/diary_organizer/cli.py insights --period week --mood-only
python src/diary_organizer/cli.py insights --period month --themes-only
```

### Mood Statistics
```bash
python src/diary_organizer/cli.py mood-stats --period month
```

### Word Cloud
```bash
python src/diary_organizer/cli.py word-cloud --period month --top 20
```

### Monthly Reflection
```bash
python src/diary_organizer/cli.py reflection --year 2024 --month 6
```

### Writing Streak
```bash
python src/diary_organizer/cli.py streak
```

### Using the Installed Entry Point
```bash
diary-organizer write --content "Great day!" --mood happy
diary-organizer mood-stats --period week
diary-organizer streak
```

---

## 🌐 Web UI

Launch the Streamlit dashboard:

```bash
streamlit run src/diary_organizer/web_ui.py
```

### Pages

| Page | Description |
|------|-------------|
| ✍️ **Write Entry** | Text area, mood selector with emojis, tag input |
| 📅 **Calendar View** | Browse entries grouped by date |
| 🎭 **Mood Chart** | Bar chart of mood distribution, streak metrics |
| ✨ **Insights Dashboard** | Themes, word cloud, streak info, monthly reflection |

---

## ⚙️ Configuration

All settings are in `config.yaml`:

```yaml
app:
  name: "Diary Journal Organizer"
  version: "1.0.0"
  log_level: "INFO"       # DEBUG, INFO, WARNING, ERROR
  data_dir: "./data"       # Where diary.json is stored

diary:
  moods: [happy, sad, anxious, ...]  # Available mood options
  default_period: "week"             # Default time filter
  entries_per_page: 10               # Pagination

llm:
  model: "llama3"                    # Ollama model name
  temperature: 0.6                   # AI creativity level
  system_prompt: "You are a compassionate journal therapist."
```

Environment variables can also be set via `.env` (see `.env.example`).

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src/diary_organizer --cov-report=term-missing

# Using Makefile
make test
make coverage
```

---

## 📊 Mood Tracking & Analytics

### Mood Stats
Get counts and percentages for each mood over any time period. Displayed as tables in CLI and charts in Web UI.

### Word Cloud Data
Pure-Python word frequency analysis — stop words are filtered, and words are ranked by occurrence. Visualized as bar charts in the dashboard.

### Theme Analysis
Combines keyword frequency from entry content (weighted normally) and tags (weighted 3×) to surface the topics you write about most.

### Writing Streaks
Tracks consecutive days with at least one entry. Shows current streak, longest streak, and total days written.

### Monthly Reflections
AI-generated summaries for any month — covering mood journey, highlights, challenges, and intentions.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Run tests: `pytest tests/ -v`
4. Commit changes: `git commit -m "Add amazing feature"`
5. Push: `git push origin feature/amazing-feature`
6. Open a Pull Request

---

## 📄 License

MIT
