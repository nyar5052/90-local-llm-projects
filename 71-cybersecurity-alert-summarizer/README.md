# 🛡️ Cybersecurity Alert Summarizer

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Powered by Ollama](https://img.shields.io/badge/LLM-Ollama-orange.svg)](https://ollama.ai)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)]()

> **AI-powered cybersecurity alert analysis, CVE lookup, IOC extraction, and threat intelligence scoring — all running locally with complete data privacy.**

---

## ✨ Features

| Feature | Description | LLM Required |
|---------|-------------|:---:|
| 🔬 **Alert Summarization** | AI-powered analysis of security alerts with severity assessment | ✅ |
| 📊 **Threat Intelligence Scoring** | Automated scoring (0–10) based on CVEs, IOCs, and keywords | ❌ |
| 🔍 **IOC Extraction** | Auto-extract IPs, domains, emails, hashes, URLs from alert text | ❌ |
| 📛 **CVE Database Lookup** | Local CVE database with CVSS scores and affected systems | ❌ |
| 🔗 **Alert Correlation** | Find connections between multiple alerts via shared IOCs/CVEs | ❌ |
| ⚡ **Priority Ranking** | Rank multiple alerts by risk level with justification | ✅ |
| 🖥️ **Streamlit Web UI** | Interactive dashboard with severity meters and IOC tables | — |
| 💻 **Rich CLI** | Beautiful terminal output with tables and panels | — |

## 🏗️ Architecture

```
71-cybersecurity-alert-summarizer/
├── src/cyber_alert/
│   ├── __init__.py          # Package metadata
│   ├── core.py              # Business logic: IOC extraction, CVE lookup, scoring
│   ├── cli.py               # Click CLI with Rich output
│   ├── web_ui.py            # Streamlit dashboard (4 tabs)
│   └── config.py            # YAML config management with env overrides
├── tests/
│   ├── test_core.py         # Core logic tests (25+ test cases)
│   └── test_cli.py          # CLI integration tests
├── config.yaml              # Configuration file
├── .env.example             # Environment variables template
├── setup.py                 # Package installation
├── Makefile                 # Development commands
├── requirements.txt         # Dependencies
└── README.md
```

### Data Flow

```
Alert Text ──► IOC Extraction ──► IOC Table
     │              │
     ├──► CVE Extraction ──► CVE Lookup (local DB)
     │              │
     ├──► Keyword Analysis ──► Threat Score (0-10)
     │
     └──► LLM Analysis ──► Summary / Priority Ranking
```

## 🚀 Quick Start

### Installation

```bash
cd 71-cybersecurity-alert-summarizer
pip install -r requirements.txt
# Copy and edit environment config
cp .env.example .env
```

### CLI Usage

```bash
# Summarize an alert file
python -m src.cyber_alert.cli --alert alert.txt --severity critical

# Inline text analysis
python -m src.cyber_alert.cli --text "CVE-2024-3094: XZ Utils backdoor from 192.168.1.100" --severity all

# Extract IOCs (no LLM needed — instant!)
python -m src.cyber_alert.cli --alert alert.txt --iocs

# CVE lookup (no LLM needed)
python -m src.cyber_alert.cli --text "Found CVE-2024-3094 and CVE-2024-21762" --cves

# Threat intelligence scoring (no LLM needed)
python -m src.cyber_alert.cli --alert alert.txt --score

# Prioritize multiple alerts
python -m src.cyber_alert.cli --alert alerts.txt --prioritize

# Verbose mode
python -m src.cyber_alert.cli --alert alert.txt --score --verbose
```

### 🖥️ Web UI

```bash
streamlit run src/cyber_alert/web_ui.py
```

The Streamlit dashboard provides **4 interactive tabs**:

| Tab | Description |
|-----|-------------|
| 📥 **Alert Input** | Paste or upload alerts, choose analysis mode |
| 🔍 **IOC Table** | View extracted IOCs and CVE lookup results |
| 📊 **Severity Dashboard** | Threat score visualization with factor breakdown |
| 💡 **Recommendations** | AI-generated mitigation recommendations |

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ -v --cov=src/cyber_alert --cov-report=term-missing
```

## ⚙️ Configuration

Edit `config.yaml` or set environment variables (see `.env.example`):

```yaml
model:
  name: "llama3"           # Ollama model name
  temperature: 0.3         # Lower = more focused analysis
  max_tokens: 2048

analysis:
  ioc_extraction: true     # Enable IOC extraction
  cve_lookup: true         # Enable CVE database lookup
  threat_scoring: true     # Enable threat intelligence scoring
```

## 📦 Makefile Commands

| Command | Description |
|---------|-------------|
| `make install` | Install dependencies |
| `make test` | Run tests |
| `make test-cov` | Run tests with coverage |
| `make lint` | Run linter |
| `make format` | Format code with Black |
| `make run ARGS="--help"` | Run CLI |
| `make web` | Launch Streamlit UI |
| `make clean` | Clean build artifacts |
