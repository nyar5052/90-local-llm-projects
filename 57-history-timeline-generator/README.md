# 📜 History Timeline Generator

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python&logoColor=white)
![LLM](https://img.shields.io/badge/LLM-Ollama-orange?logo=meta&logoColor=white)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-red?logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen?logo=pytest)

> 🏛️ **Generate rich historical timelines with era grouping, key figure profiles, and cause-effect chain analysis — powered by a local LLM.**

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📅 **Interactive Timelines** | Chronological events with category color-coding |
| 🏛️ **Era Grouping** | Events organized into historical eras |
| 👤 **Key Figure Profiles** | Detailed biographies of historical figures |
| 🔗 **Cause-Effect Chains** | Analyze how events led to consequences |
| 🎨 **Category Tagging** | Political, military, social, economic, cultural, scientific |
| 📊 **Detail Levels** | Brief (5-8), medium (10-15), detailed (15-25) events |
| 🌐 **Streamlit Web UI** | Beautiful interactive timeline interface |
| 💻 **Rich CLI** | Full-featured terminal with color tables |
| ⚙️ **YAML Config** | Centralized configuration management |

---

## 🏗️ Architecture

```
57-history-timeline-generator/
├── src/history_timeline/
│   ├── __init__.py          # Package metadata
│   ├── core.py              # Business logic, data models, LLM interaction
│   ├── cli.py               # Rich CLI with Click commands
│   └── web_ui.py            # Streamlit web interface
├── tests/
│   ├── test_core.py         # Core logic tests
│   └── test_cli.py          # CLI integration tests
├── config.yaml              # Application configuration
├── setup.py                 # Package installation
├── Makefile                 # Common development tasks
├── .env.example             # Environment variable template
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

---

## 🚀 Installation

```bash
cd 57-history-timeline-generator
pip install -e ".[dev]"
ollama serve
```

---

## 💻 CLI Usage

```bash
# Generate a timeline
history-timeline generate --topic "American Civil War" --detail medium

# With date range
history-timeline generate --topic "Space Race" --start 1957 --end 1972

# Get key figure profiles
history-timeline figures --topic "Renaissance"

# Analyze cause-effect chains
history-timeline cause-effect --topic "French Revolution"

# Save to file
history-timeline generate --topic "Industrial Revolution" --output timeline.json
```

---

## 🌐 Web UI

```bash
streamlit run src/history_timeline/web_ui.py
```

Features:
- 📅 **Timeline Display** — Expandable events with category icons
- 👤 **Figure Cards** — Detailed profiles of key historical figures
- 🔗 **Cause-Effect View** — Visual cause → event → effect chains
- 🏛️ **Era Navigator** — Browse events grouped by historical era

---

## 🧪 Testing

```bash
pytest tests/ -v
pytest tests/ -v --cov=src/history_timeline --cov-report=term-missing
```

---

## ⚙️ Configuration

Edit `config.yaml` to customize LLM settings, detail levels, and event categories.

---

## 📝 License

MIT
