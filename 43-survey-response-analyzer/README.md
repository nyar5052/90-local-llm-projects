<div align="center">

# 📋 Survey Response Analyzer

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Powered by Ollama](https://img.shields.io/badge/LLM-Ollama-orange.svg)](https://ollama.ai)

**Extract themes, insights, and recommendations from survey data — powered by local LLM**

[Features](#-features) · [Installation](#-installation) · [CLI Usage](#-cli-usage) · [Web UI](#-web-ui) · [Architecture](#-architecture)

</div>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎯 **Theme clustering** | Automatically identify themes and group them into higher-level clusters |
| 📊 **Demographic cross-tabs** | Analyze responses by demographic groups (age, gender, department) |
| 📌 **Verbatim highlighting** | Surface the most impactful and representative quotes |
| 💡 **Recommendation engine** | Generate prioritized, actionable recommendations with effort/impact |
| 🔍 **Smart column detection** | Auto-detect text columns vs demographic/rating columns |
| 📈 **Visual insights** | Theme distribution charts and sentiment analysis |
| 🖥️ **Streamlit Web UI** | Interactive dashboard with theme cards, charts, and recommendations |
| ⚡ **100% Local** | All processing runs locally — your data never leaves your machine |

## 🏗️ Architecture

```
43-survey-response-analyzer/
├── src/survey_analyzer/
│   ├── __init__.py          # Package metadata
│   ├── core.py              # Core: themes, clusters, cross-tabs, verbatims, recommendations
│   ├── cli.py               # Rich CLI with theme tables and recommendation display
│   └── web_ui.py            # Streamlit dashboard with theme cards and insight charts
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
# Basic theme extraction
python -m src.survey_analyzer.cli --file survey.csv

# Detailed report with specific column
python -m src.survey_analyzer.cli --file survey.csv --column feedback --report detailed

# Show theme clusters and verbatim quotes
python -m src.survey_analyzer.cli --file survey.csv --show-clusters --show-verbatims

# Recommendations only
python -m src.survey_analyzer.cli --file survey.csv --show-recommendations
```

### CLI Options

| Option | Description |
|--------|-------------|
| `--file`, `-f` | Path to survey CSV file (**required**) |
| `--report`, `-r` | Report level: `brief` or `detailed` (default: brief) |
| `--column`, `-c` | Specific text column to analyze |
| `--show-clusters/--no-clusters` | Show theme clustering |
| `--show-verbatims/--no-verbatims` | Show notable verbatim quotes |
| `--show-recommendations/--no-recommendations` | Show recommendations (default: on) |
| `--verbose`, `-v` | Enable verbose logging |

## 🌐 Web UI

```bash
streamlit run src/survey_analyzer/web_ui.py
# Or
make web
```

**Web UI Features:**
- 📁 CSV file uploader with column selector
- 🎯 Theme cards with counts, sentiment, and representative quotes
- 📊 Theme distribution bar chart
- 💡 Recommendations panel with priority/effort/impact
- 📌 Notable verbatim quotes viewer
- 📈 Sentiment analysis per theme

## 🧪 Testing

```bash
python -m pytest tests/ -v
make test-cov
```

## ⚙️ Configuration

```yaml
llm:
  model: "gemma3:4b"
  temperature: 0.3
analysis:
  max_responses_for_themes: 50
clustering:
  enabled: true
```

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
