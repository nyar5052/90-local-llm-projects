# 📈 Trend Analysis Tool

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Tests](https://img.shields.io/badge/tests-pytest-brightgreen.svg)](https://docs.pytest.org/)

> **Production-grade** trend analysis system powered by local LLMs via Ollama.
> Extract topics, track sentiment, detect emerging trends, and generate comprehensive reports from your text data.

---

## 🏗️ Architecture

```
50-trend-analysis-tool/
├── src/trend_analyzer/
│   ├── __init__.py          # Package metadata & version
│   ├── core.py              # Business logic — topics, sentiment, evolution, scheduling
│   ├── cli.py               # Click CLI with rich terminal output
│   └── web_ui.py            # Streamlit interactive dashboard
├── tests/
│   ├── test_core.py         # Unit tests for all core functions
│   └── test_cli.py          # CLI integration tests
├── config.yaml              # Central YAML configuration
├── setup.py                 # Installable package with entry point
├── requirements.txt         # Pinned dependencies
├── Makefile                 # Dev workflow shortcuts
├── .env.example             # Environment variable reference
└── README.md                # You are here
```

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔍 **Topic Extraction** | LLM-powered identification of key topics with frequency & trend direction |
| 💭 **Sentiment Analysis** | Document-level sentiment tracking with distribution & shift detection |
| 📊 **Topic Evolution** | Track how topics change over time across analysis runs |
| 🔗 **Sentiment-Topic Correlation** | Automatically correlate sentiment with specific topics |
| 🚨 **Emerging Topic Detection** | Configurable threshold-based alerts for new / suddenly popular topics |
| 📋 **Comprehensive Reports** | LLM-generated markdown reports with executive summary & predictions |
| 📅 **Report Scheduling** | Daily / weekly / monthly schedule metadata generation |
| 🖥️ **Streamlit Web UI** | Interactive dashboard with charts, cards, and alert panels |
| ⚙️ **Config-Driven** | All knobs exposed via `config.yaml` — model, thresholds, schedule, logging |
| 📝 **Proper Logging** | Structured logging throughout with configurable level & file output |

---

## 🚀 Prerequisites

- **Python 3.10+**
- **[Ollama](https://ollama.ai/)** running locally with a supported model (default: `gemma3`)

```bash
# Install & start Ollama
ollama serve
ollama pull gemma3
```

---

## 📦 Installation

```bash
# Clone / navigate to the project
cd 50-trend-analysis-tool

# Install dependencies
pip install -r requirements.txt

# (Optional) Install as editable package
pip install -e ".[dev]"
```

---

## 🖥️ CLI Usage

The CLI is powered by [Click](https://click.palletsprojects.com/) with [Rich](https://rich.readthedocs.io/) terminal output.

### Full Analysis

```bash
# Analyze a directory of articles
python -m src.trend_analyzer.cli analyze --dir ./articles --timeframe "last month"

# Skip sentiment analysis
python -m src.trend_analyzer.cli analyze -d ./reports -t "Q1-2024" --no-sentiment

# Use a custom config
python -m src.trend_analyzer.cli -c my_config.yaml analyze -d ./data
```

### Topics Only

```bash
python -m src.trend_analyzer.cli topics --dir ./articles
```

### Sentiment Only

```bash
python -m src.trend_analyzer.cli sentiment --dir ./articles
```

### Emerging Topic Detection

```bash
python -m src.trend_analyzer.cli emerging --dir ./articles --threshold 0.6
```

### Report Scheduling

```bash
python -m src.trend_analyzer.cli schedule
```

### Installed Entry Point

After `pip install -e .`:

```bash
trend-analyzer analyze -d ./articles -t "last week"
trend-analyzer topics -d ./reports
trend-analyzer schedule
```

---

## 🌐 Web UI

Launch the Streamlit dashboard:

```bash
streamlit run src/trend_analyzer/web_ui.py
```

### Dashboard Tabs

| Tab | What It Shows |
|-----|---------------|
| 📂 **Source Input** | Folder path input, file listing with sizes, document count metric |
| 🔍 **Topic Cards** | Card-style display for each topic with trend badges (🟢🔵🟡🔴) |
| 📊 **Timeline Chart** | Bar charts for topic frequency & sentiment distribution |
| 🚨 **Emerging Alerts** | Highlighted emerging topics with alert cards & full markdown report |

Use the **sidebar** to set the source folder, timeframe, sentiment toggle, and emerging threshold, then click **▶️ Run Analysis**.

---

## ⚙️ Configuration

All settings live in `config.yaml`:

```yaml
model:
  name: "gemma3"          # Ollama model name
  temperature: 0.3        # LLM creativity (0.0 – 1.0)
  max_tokens: 4000        # Max response tokens

file_extensions:           # Supported document formats
  - .txt
  - .md
  - .text
  - .csv
  - .log

analysis:
  max_documents: 50        # Cap on documents loaded
  preview_chars: 500       # Characters sent per document
  topic_limit: 20          # Max topics to extract

emerging_detection:
  threshold: 0.7           # Score cutoff (0–1)
  min_frequency: "medium"  # Minimum frequency rank

sentiment:
  enabled: true
  granularity: "document"

schedule:
  enabled: false
  frequency: "weekly"      # daily | weekly | monthly
  day: "monday"
  time: "09:00"

logging:
  level: "INFO"            # DEBUG | INFO | WARNING | ERROR
  file: "trend_analyzer.log"
```

Environment variables (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `gemma3` | Model to use |
| `LOG_LEVEL` | `INFO` | Logging level |
| `CONFIG_PATH` | `config.yaml` | Config file path |
| `MAX_DOCUMENTS` | `50` | Max documents to load |

---

## 📁 Input Format

Place text files in a directory:

```
articles/
├── ai-in-healthcare.txt
├── cybersecurity-trends.txt
├── remote-work-update.txt
├── market-analysis.md
└── server-logs.log
```

---

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# With coverage
python -m pytest tests/ -v --cov=src/trend_analyzer --cov-report=term-missing

# Specific test class
python -m pytest tests/test_core.py::TestDetectEmergingTopics -v
```

---

## 📊 Example Output

```
📈 Trend Analysis Tool
✓ Loaded 15 documents from articles/
Timeframe: last month

┌───┬──────────────────────┬───────────┬──────────┬─────────────────────────────┐
│ # │ Topic                │ Frequency │ Trend    │ Description                 │
├───┼──────────────────────┼───────────┼──────────┼─────────────────────────────┤
│ 1 │ AI in Healthcare     │ 🔥 High   │ Emerging │ AI applications in medical  │
│ 2 │ Cybersecurity        │ 📈 Medium │ Growing  │ Rising security threats     │
│ 3 │ Remote Work          │ 📊 Low    │ Stable   │ Hybrid work models          │
└───┴──────────────────────┴───────────┴──────────┴─────────────────────────────┘

💭 Sentiment Overview
  Overall: Mixed
  😊 Positive: 8 | 😞 Negative: 4 | 😐 Neutral: 3

🚨 Emerging Topic Alerts
  • AI in Healthcare (score: 0.87) — Emerging, High frequency
```

---

## 📄 License

MIT
