<div align="center">

# 🏢 Competitor Analysis Tool

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Powered by Ollama](https://img.shields.io/badge/LLM-Ollama-orange.svg)](https://ollama.ai)

**SWOT analysis, feature comparison, and market positioning — powered by local LLM**

[Features](#-features) · [Installation](#-installation) · [CLI Usage](#-cli-usage) · [Web UI](#-web-ui) · [Architecture](#-architecture)

</div>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📊 **SWOT analysis** | Comprehensive strengths, weaknesses, opportunities, and threats |
| 📋 **Feature matrix** | Detailed feature-by-feature comparison with ✅/❌/🔶 |
| 💰 **Pricing comparison** | Pricing model, tier, and value proposition analysis |
| 🗺️ **Market positioning** | Visual positioning map on Price vs Quality axes |
| 🎯 **Action items** | Prioritized strategic action items with timeline and category |
| 📝 **Full reports** | LLM-generated competitive comparison and strategic recommendations |
| 🖥️ **Streamlit Web UI** | Interactive dashboard with SWOT cards, matrix, and positioning chart |
| ⚡ **100% Local** | All processing runs locally — your data never leaves your machine |

## 🏗️ Architecture

```
45-competitor-analysis-tool/
├── src/competitor_analyzer/
│   ├── __init__.py          # Package metadata
│   ├── core.py              # Core: SWOT, features, pricing, positioning, actions
│   ├── cli.py               # Rich CLI with SWOT grid and feature matrix
│   └── web_ui.py            # Streamlit dashboard with cards and charts
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
# Full analysis
python -m src.competitor_analyzer.cli --company "Acme" --competitors "Comp1,Comp2,Comp3" --industry "SaaS"

# SWOT only
python -m src.competitor_analyzer.cli -c "Acme" -comp "Comp1,Comp2" -i "SaaS" --swot-only

# With feature matrix and pricing
python -m src.competitor_analyzer.cli -c "Acme" -comp "Comp1" -i "tech" --show-features --show-pricing

# With action items
python -m src.competitor_analyzer.cli -c "Acme" -comp "Comp1" -i "tech" --show-actions
```

### CLI Options

| Option | Description |
|--------|-------------|
| `--company`, `-c` | Your company/product name (**required**) |
| `--competitors`, `-comp` | Comma-separated competitor names (**required**) |
| `--industry`, `-i` | Industry sector (**required**) |
| `--full-report/--swot-only` | Full report vs SWOT only (default: full) |
| `--show-features/--no-features` | Show feature comparison matrix (default: on) |
| `--show-pricing/--no-pricing` | Show pricing comparison (default: on) |
| `--show-actions/--no-actions` | Show action items (default: on) |
| `--verbose`, `-v` | Enable verbose logging |

## 🌐 Web UI

```bash
streamlit run src/competitor_analyzer/web_ui.py
# Or
make web
```

**Web UI Features:**
- 🏢 Company & competitor input form
- 📊 SWOT analysis cards (color-coded quadrants)
- 📋 Feature comparison matrix table
- 💰 Pricing comparison with tier analysis
- 🗺️ Market positioning scatter chart
- 🎯 Prioritized action items with timeline/category

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
  max_competitors: 10
  feature_matrix_max_features: 15
```

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
