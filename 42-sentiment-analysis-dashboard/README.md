<div align="center">

# 💬 Sentiment Analysis Dashboard

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Powered by Ollama](https://img.shields.io/badge/LLM-Ollama-orange.svg)](https://ollama.ai)

**Analyze sentiment of text data with batch processing, trends, and export — powered by local LLM**

[Features](#-features) · [Installation](#-installation) · [CLI Usage](#-cli-usage) · [Web UI](#-web-ui) · [Architecture](#-architecture)

</div>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📁 **Batch file processing** | Analyze multiple text files in a single run |
| 📈 **Trend over time** | Track sentiment shifts across entries with configurable windows |
| ☁️ **Word cloud data** | Extract key phrase frequencies for word cloud generation |
| 🔄 **Compare across sources** | Side-by-side sentiment comparison of different data sources |
| 📥 **Export reports** | Comprehensive JSON reports with summary, trend, and detail data |
| 📊 **Sentiment gauge** | Real-time distribution overview with confidence scores |
| 🖥️ **Streamlit Web UI** | Interactive dashboard with upload, gauges, charts, and export |
| ⚡ **100% Local** | All processing runs locally — your data never leaves your machine |

## 🏗️ Architecture

```
42-sentiment-analysis-dashboard/
├── src/sentiment_analyzer/
│   ├── __init__.py          # Package metadata
│   ├── core.py              # Core: analyze, batch, trend, word cloud, compare, export
│   ├── cli.py               # Rich CLI with progress bars and tables
│   └── web_ui.py            # Streamlit dashboard with gauges and charts
├── tests/
│   ├── conftest.py          # Shared fixtures
│   ├── test_core.py         # Core logic tests
│   └── test_cli.py          # CLI integration tests
├── config.yaml              # Application configuration
├── setup.py                 # Package setup
├── Makefile                 # Development commands
├── .env.example             # Environment template
├── requirements.txt         # Dependencies
└── README.md                # This file
```

## 📦 Installation

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai) running locally with `gemma3:4b` model

### Quick Start

```bash
pip install -r requirements.txt
# Or
pip install -e .
```

## 🖥️ CLI Usage

```bash
# Analyze a single file
python -m src.sentiment_analyzer.cli --file reviews.txt

# Batch analyze multiple files
python -m src.sentiment_analyzer.cli --file reviews.txt --file feedback.txt

# Show sentiment trend
python -m src.sentiment_analyzer.cli --file reviews.txt --show-trend

# JSON output
python -m src.sentiment_analyzer.cli --file reviews.txt --format json

# Export report
python -m src.sentiment_analyzer.cli --file reviews.txt --export report.json
```

### CLI Options

| Option | Description |
|--------|-------------|
| `--file`, `-f` | Path to text file(s) — repeatable for batch (**required**) |
| `--format`, `-fmt` | Output format: `table`, `json`, `summary` (default: table) |
| `--show-trend/--no-trend` | Show sentiment trend over entries |
| `--export`, `-e` | Export full report to JSON file |
| `--verbose`, `-v` | Enable verbose logging |

## 🌐 Web UI

```bash
streamlit run src/sentiment_analyzer/web_ui.py
# Or
make web
```

**Web UI Features:**
- 📁 Multi-file uploader (TXT/CSV)
- 📊 Sentiment gauge with distribution metrics
- 📋 Detailed results table with emoji indicators
- 📈 Configurable sentiment trend chart
- ☁️ Key phrases bar chart (word cloud data)
- 📥 One-click JSON report download

## 🧪 Testing

```bash
python -m pytest tests/ -v
make test-cov
```

## ⚙️ Configuration

```yaml
llm:
  model: "gemma3:4b"
  temperature: 0.2
analysis:
  trend_window: 5
  word_cloud_max_words: 50
```

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
