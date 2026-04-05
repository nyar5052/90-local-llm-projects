<div align="center">

# 📊 CSV Data Analyzer

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Powered by Ollama](https://img.shields.io/badge/LLM-Ollama-orange.svg)](https://ollama.ai)

**Ask natural language questions about any CSV dataset — powered by local LLM**

[Features](#-features) · [Installation](#-installation) · [CLI Usage](#-cli-usage) · [Web UI](#-web-ui) · [Architecture](#-architecture)

</div>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔍 **Auto-detect column types** | Automatically identifies numeric, categorical, datetime, text, and boolean columns |
| 📈 **Statistical summaries** | Descriptive statistics, skewness, kurtosis, null analysis |
| 🔗 **Correlation analysis** | Pearson correlation matrix with strong/moderate correlation detection |
| 📊 **Chart suggestions** | Intelligent chart type recommendations based on data characteristics |
| 💬 **Natural language queries** | Ask questions about your data in plain English |
| 📥 **Export insights** | Export comprehensive analysis to JSON |
| 🖥️ **Streamlit Web UI** | Interactive browser-based interface with upload, preview, and charts |
| ⚡ **100% Local** | All processing runs locally — your data never leaves your machine |

## 🏗️ Architecture

```
41-csv-data-analyzer/
├── src/csv_analyzer/
│   ├── __init__.py          # Package metadata
│   ├── core.py              # Core logic: load, analyze, detect types, correlations
│   ├── cli.py               # Rich CLI interface with Click
│   └── web_ui.py            # Streamlit web dashboard
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
# Install dependencies
pip install -r requirements.txt

# Or install as package
pip install -e .

# Or use make
make install
```

### Development Setup

```bash
# Install with dev dependencies
pip install -e ".[dev]"
# Or
make dev
```

## 🖥️ CLI Usage

```bash
# Basic analysis with question
python -m src.csv_analyzer.cli --file data.csv --query "What are the top 5 months by revenue?"

# Show all analysis features
python -m src.csv_analyzer.cli --file data.csv --show-types --show-correlations --show-charts

# Export insights to JSON
python -m src.csv_analyzer.cli --file data.csv --export insights.json

# Minimal output — just the question
python -m src.csv_analyzer.cli --file data.csv -q "Summarize trends" --no-preview --no-types
```

### CLI Options

| Option | Description |
|--------|-------------|
| `--file`, `-f` | Path to CSV file (**required**) |
| `--query`, `-q` | Natural language question about the data |
| `--show-preview/--no-preview` | Show data preview table (default: on) |
| `--show-types/--no-types` | Show detected column types (default: on) |
| `--show-correlations/--no-correlations` | Show correlation analysis (default: on) |
| `--show-charts/--no-charts` | Show chart suggestions (default: on) |
| `--export`, `-e` | Export insights to JSON file |
| `--verbose`, `-v` | Enable verbose logging |

## 🌐 Web UI

Launch the interactive Streamlit dashboard:

```bash
streamlit run src/csv_analyzer/web_ui.py
# Or
make web
```

**Web UI Features:**
- 📁 CSV file uploader with drag-and-drop
- 📋 Interactive data preview table
- 🔍 Auto-detected column type cards
- 📈 Statistical summary tabs (numeric + categorical)
- 🔗 Correlation heatmap with strong correlation highlights
- 📊 Smart chart suggestions with interactive visualizations
- 💬 Natural language query box with LLM-powered answers
- 📥 One-click JSON export

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
make test-cov
```

## ⚙️ Configuration

Edit `config.yaml` to customize:

```yaml
llm:
  model: "gemma3:4b"
  temperature: 0.3
analysis:
  correlation_threshold: 0.5
```

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
