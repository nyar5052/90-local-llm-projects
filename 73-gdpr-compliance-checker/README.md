# 🔒 GDPR Compliance Checker

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Powered by Ollama](https://img.shields.io/badge/LLM-Ollama-orange.svg)](https://ollama.ai)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)]()

> **Comprehensive GDPR compliance analysis with article-by-article checklists, data flow mapping, DPO recommendations, and audit trails — powered by local AI.**

---

## ✨ Features

| Feature | Description | LLM Required |
|---------|-------------|:---:|
| ✅ **Article-by-Article Checklist** | Check all 20+ GDPR articles (Art. 5–49) automatically | ❌ |
| 🔀 **Data Flow Mapping** | Detect data types, purposes, and cross-border transfers | ❌ |
| 🧑‍⚖️ **DPO Recommendations** | Priority-ranked recommendations based on compliance gaps | ❌ |
| 📋 **Audit Trail** | Timestamped audit log of all compliance checks | ❌ |
| 🔍 **AI Compliance Check** | Deep LLM analysis of documents against GDPR | ✅ |
| 📝 **AI Checklist Generation** | LLM-generated compliance checklist | ✅ |
| 🖥️ **Streamlit Web UI** | Interactive compliance dashboard with 4 tabs | — |
| 💻 **Rich CLI** | Terminal tables with compliance status icons | — |

## 🏗️ Architecture

```
73-gdpr-compliance-checker/
├── src/gdpr_checker/
│   ├── __init__.py          # Package metadata
│   ├── core.py              # Business logic: checklist, data flows, DPO recs
│   ├── cli.py               # Click CLI with Rich output
│   ├── web_ui.py            # Streamlit dashboard (4 tabs)
│   └── config.py            # YAML config management
├── tests/
│   ├── test_core.py         # Core logic tests
│   └── test_cli.py          # CLI integration tests
├── config.yaml              # Configuration
├── .env.example             # Environment variables
├── setup.py / Makefile      # Build & dev tools
└── README.md
```

### GDPR Articles Covered

```
Art. 5  – Principles               Art. 25 – Privacy by Design
Art. 6  – Lawfulness               Art. 28 – Data Processors
Art. 7  – Consent                  Art. 30 – Records of Processing
Art. 12 – Transparency             Art. 32 – Security Measures
Art. 13-14 – Information           Art. 33 – Breach Notification (DPA)
Art. 15 – Right of Access          Art. 34 – Breach Notification (Subject)
Art. 16 – Rectification            Art. 35 – DPIA
Art. 17 – Right to Erasure         Art. 37-39 – DPO
Art. 18 – Restriction              Art. 44-49 – International Transfers
Art. 20 – Data Portability
Art. 21 – Right to Object
Art. 22 – Automated Decisions
```

## 🚀 Quick Start

### Installation

```bash
cd 73-gdpr-compliance-checker
pip install -r requirements.txt
cp .env.example .env
```

### CLI Usage

```bash
# Full AI compliance check
python -m src.gdpr_checker.cli --file privacy_policy.txt --check all

# Article-by-article checklist (no LLM — instant!)
python -m src.gdpr_checker.cli --file policy.txt --articles

# DPO recommendations (no LLM)
python -m src.gdpr_checker.cli --file policy.txt --dpo

# Data flow mapping (no LLM)
python -m src.gdpr_checker.cli --file policy.txt --data-flows

# Focus on specific area
python -m src.gdpr_checker.cli --file policy.txt --check consent
```

### 🖥️ Web UI

```bash
streamlit run src/gdpr_checker/web_ui.py
```

| Tab | Description |
|-----|-------------|
| 📄 **Document Upload** | Upload/paste documents, run analysis |
| ✅ **Compliance Checklist** | Expandable article-by-article review with DPO recs |
| 🔀 **Data Flow Diagram** | Data type mapping with cross-border detection |
| 📋 **Audit Log** | Timestamped trail of all compliance checks |

## 🧪 Testing

```bash
python -m pytest tests/ -v
python -m pytest tests/ -v --cov=src/gdpr_checker --cov-report=term-missing
```

## ⚙️ Configuration

```yaml
model:
  name: "llama3"
  temperature: 0.2
compliance:
  default_check: "all"
  article_checklist: true
  data_flow_mapping: true
```

## 📦 Makefile Commands

| Command | Description |
|---------|-------------|
| `make install` | Install dependencies |
| `make test` | Run tests |
| `make run ARGS="--help"` | Run CLI |
| `make web` | Launch Streamlit UI |
| `make clean` | Clean artifacts |
