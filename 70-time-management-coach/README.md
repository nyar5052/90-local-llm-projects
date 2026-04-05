# ⏱️ Time Management Coach

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Ollama](https://img.shields.io/badge/LLM-Ollama-orange.svg)](https://ollama.ai)

**AI-powered productivity analysis, Pomodoro planning, time blocking, and coaching — all from your terminal or browser.**

---

## ✨ Features

| Feature | Description |
|---|---|
| 🍅 **Pomodoro Integration** | Timer tracking, session logging, daily plan generation |
| 📅 **Time Blocking** | AI-generated optimal daily schedules based on energy levels |
| 📈 **Productivity Scoring** | 1–10 score with deep-work ratio, consistency, and balance factors |
| 📊 **Weekly Review** | Comprehensive weekly analysis with trends and goal tracking |
| 🎯 **Focus Tracking** | Deep-work hours, focus ratio, category breakdowns |
| 🤖 **AI Coaching** | Personalised tips, analysis, and schedule suggestions via local LLM |
| 🌐 **Web UI** | Full Streamlit dashboard with charts, timers, and interactive forms |

---

## 🏗️ Architecture

```
70-time-management-coach/
├── src/time_coach/
│   ├── __init__.py        # Package metadata
│   ├── core.py            # Business logic, computation, LLM calls
│   ├── cli.py             # Click CLI (review, tips, pomodoro, log-entry, weekly, score)
│   └── web_ui.py          # Streamlit web dashboard
├── tests/
│   ├── __init__.py
│   └── test_core.py       # Pytest suite
├── config.yaml            # YAML configuration
├── setup.py               # Package setup with entry points
├── Makefile               # Dev shortcuts
├── .env.example           # Environment variable template
├── requirements.txt       # Python dependencies
└── README.md
```

---

## 🚀 Installation

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. (Optional) Install as editable package
pip install -e ".[dev]"

# 3. Start Ollama
ollama serve
ollama pull llama3.2
```

Copy `.env.example` to `.env` and adjust values as needed.

---

## 💻 CLI Usage

All commands support `--verbose` and `--config` flags.

### Review time usage
```bash
python -m src.time_coach.cli review --log timelog.csv
python -m src.time_coach.cli review --log timelog.csv --analyze   # with AI analysis
```

### Get productivity tips
```bash
python -m src.time_coach.cli tips --goal "deep work"
```

### Generate Pomodoro plan
```bash
python -m src.time_coach.cli pomodoro --tasks "coding,design,emails" --hours 6
```

### Quick-log a time entry
```bash
python -m src.time_coach.cli log-entry --category coding --activity "Feature X" --duration 2.5
```

### Weekly review
```bash
python -m src.time_coach.cli weekly --log timelog.csv
```

### Productivity score
```bash
python -m src.time_coach.cli score --log timelog.csv
```

---

## 🌐 Web UI

Launch the Streamlit dashboard:

```bash
streamlit run src/time_coach/web_ui.py
```

### Pages

- **Time Log** — Quick entry form, today's entries table, category pie chart, CSV upload
- **Analysis** — Time breakdown table, daily totals line chart, productivity score gauge, AI analysis button, category trends
- **Pomodoro Timer** — Visual countdown timer, session counter, today's stats, full-day plan generator
- **Weekly Review** — Week selector, summary stats, this-week-vs-last comparison, productivity trend chart, AI weekly review, goals-vs-actual table

---

## 🍅 Pomodoro

Default settings (configurable in `config.yaml`):

| Setting | Default |
|---|---|
| Work session | 25 min |
| Short break | 5 min |
| Long break | 15 min |
| Sessions before long break | 4 |

Sessions are automatically logged to the time log when completed in the web UI.

---

## 📈 Productivity Score

The score (1–10) is computed from three weighted factors:

| Factor | Weight | Description |
|---|---|---|
| Deep Work | 40% | Hours of focused work vs target |
| Consistency | 30% | How close total hours are to daily target |
| Balance | 30% | Presence of adequate breaks |

Targets and weights are configurable in `config.yaml` under `productivity` and `scoring`.

---

## ⚙️ Configuration

Edit `config.yaml` to customise:

```yaml
llm:
  model: "llama3.2"
  temperature: 0.6

productivity:
  target_deep_work_hours: 4.0
  target_total_hours: 8.0
  categories:
    deep_work: ["coding", "writing", "design", "research"]
    shallow_work: ["email", "meetings", "admin"]
    breaks: ["lunch", "break", "exercise"]
```

---

## 🧪 Testing

```bash
python -m pytest tests/ -v
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for new functionality
4. Ensure all tests pass (`python -m pytest tests/ -v`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License.
