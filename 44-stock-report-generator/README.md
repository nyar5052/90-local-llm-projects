<div align="center">

# 📈 Stock Report Generator

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Powered by Ollama](https://img.shields.io/badge/LLM-Ollama-orange.svg)](https://ollama.ai)

**Professional stock analysis reports with technical indicators and risk assessment — powered by local LLM**

[Features](#-features) · [Installation](#-installation) · [CLI Usage](#-cli-usage) · [Web UI](#-web-ui) · [Architecture](#-architecture)

</div>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📊 **Multi-ticker comparison** | Compare metrics across multiple stocks side by side |
| 📈 **Technical indicators** | RSI, Bollinger Bands, MACD with signal interpretation |
| ⚠️ **Risk assessment** | Automated risk scoring with factor analysis |
| 📜 **Historical context** | Period analysis with start/end price, SMA, volatility |
| 🤖 **AI narrative reports** | LLM-generated professional analysis with outlook |
| 📉 **Price charts** | Interactive price visualization with trend lines |
| 🖥️ **Streamlit Web UI** | Interactive dashboard with metrics, indicators, and risk meter |
| ⚡ **100% Local** | All processing runs locally — your data never leaves your machine |

## 🏗️ Architecture

```
44-stock-report-generator/
├── src/stock_reporter/
│   ├── __init__.py          # Package metadata
│   ├── core.py              # Core: metrics, indicators, risk, comparison, reports
│   ├── cli.py               # Rich CLI with metrics tables and risk display
│   └── web_ui.py            # Streamlit dashboard with charts and risk meter
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
# Single stock analysis
python -m src.stock_reporter.cli --file aapl.csv --ticker AAPL

# Multi-ticker comparison
python -m src.stock_reporter.cli --file aapl.csv --ticker AAPL --file goog.csv --ticker GOOG

# With technical indicators and risk assessment
python -m src.stock_reporter.cli --file aapl.csv --ticker AAPL --show-indicators --show-risk

# Metrics only (no LLM report)
python -m src.stock_reporter.cli --file aapl.csv --ticker AAPL --no-indicators --no-risk
```

### CLI Options

| Option | Description |
|--------|-------------|
| `--file`, `-f` | Path to stock CSV file(s) — repeatable (**required**) |
| `--ticker`, `-t` | Stock ticker symbol(s) — must match file count (**required**) |
| `--show-indicators/--no-indicators` | Show RSI, Bollinger, MACD (default: on) |
| `--show-risk/--no-risk` | Show risk assessment (default: on) |
| `--verbose`, `-v` | Enable verbose logging |

## 🌐 Web UI

```bash
streamlit run src/stock_reporter/web_ui.py
# Or
make web
```

**Web UI Features:**
- 📊 Key metrics dashboard (price, change, SMA, volatility)
- 📉 Interactive price chart
- 📈 Technical indicators panel (RSI, Bollinger, MACD)
- ⚠️ Risk meter with score bar and risk factor list
- 🤖 AI-generated analysis report
- 📊 Multi-ticker comparison table

## 🧪 Testing

```bash
python -m pytest tests/ -v
make test-cov
```

## ⚙️ Configuration

```yaml
llm:
  model: "gemma3:4b"
  temperature: 0.4
analysis:
  rsi_period: 14
  bollinger_period: 20
risk:
  volatility_high_threshold: 5.0
```

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
