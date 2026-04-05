# ✉️ Sales Email Generator

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](#-testing)

> **Production-grade** sales outreach email generator powered by local LLMs via Ollama.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📧 **Smart Email Generation** | Personalised emails tailored to prospect role, company & industry |
| 🎨 **Multiple Tones** | Professional, casual, persuasive, or consultative |
| 🔄 **Follow-Up Sequences** | Multi-step drip campaigns (intro → value-add → case-study → break-up) |
| 🧪 **A/B Variants** | Generate multiple variants for split testing |
| 🔍 **Prospect Research** | AI-powered prospect profiling with pain points & talking points |
| 📊 **Personalisation Scoring** | Score emails 0-100 with improvement suggestions |
| 📋 **Template Library** | Pre-built templates: cold outreach, follow-up, demo request, case study, break-up |
| 🖥️ **Web UI** | Full Streamlit dashboard with tabs for every workflow |
| ⚙️ **Config-Driven** | YAML configuration for models, tones, templates & sequences |
| 📝 **Logging** | Structured logging throughout the pipeline |

---

## 🏗️ Architecture

```
48-sales-email-generator/
├── src/sales_email_gen/
│   ├── __init__.py          # Package metadata
│   ├── core.py              # Business logic (no UI dependencies)
│   ├── cli.py               # Click CLI interface
│   └── web_ui.py            # Streamlit web dashboard
├── tests/
│   ├── test_core.py         # Core logic tests
│   └── test_cli.py          # CLI integration tests
├── config.yaml              # Configuration file
├── setup.py                 # Package setup
├── requirements.txt         # Dependencies
├── Makefile                 # Build targets
├── .env.example             # Environment template
└── README.md
```

---

## 📋 Prerequisites

- **Python 3.10+**
- **[Ollama](https://ollama.ai/)** running locally with a model (default: `gemma3`)

---

## 🚀 Installation

```bash
# Clone and enter the project
cd 48-sales-email-generator

# Install dependencies
pip install -r requirements.txt

# Or install as editable package (recommended for development)
pip install -e ".[dev]"
```

---

## 💻 CLI Usage

The CLI provides five commands via the `sales-email` entry point (or `python -m sales_email_gen.cli`):

### Generate a single email

```bash
# Professional email
sales-email generate -p "CTO at startup" -pr "AI Platform" -t professional

# Casual follow-up with context
sales-email generate -p "VP Engineering at Acme" -pr "Dev Tools" -t casual --follow-up -c "Met at conference"
```

### Generate A/B variants

```bash
sales-email variants -p "CMO at enterprise" -pr "Analytics Suite" -n 3
```

### Build a follow-up sequence

```bash
sales-email sequence -p "VP Sales at Corp" -pr "CRM Tool" -n 4
```

### List available templates

```bash
sales-email templates
```

### Research a prospect

```bash
sales-email research -p "CTO at AI startup, Series B, 200 employees"
```

### Help & version

```bash
sales-email --help
sales-email --version
```

---

## 🎨 Tone Options

| Tone | Description |
|------|-------------|
| `professional` | Formal, business-appropriate, respectful |
| `casual` | Friendly, conversational, approachable |
| `persuasive` | Compelling, benefit-focused, action-oriented |
| `consultative` | Advisory, problem-solving, thought-leadership |

---

## 📋 Template Library

| Template | Description | Words |
|----------|-------------|-------|
| `cold_outreach` | First contact with a new prospect | 150-200 |
| `follow_up` | Follow up after initial contact | 100-150 |
| `demo_request` | Invite prospect to a product demo | 120-180 |
| `case_study` | Share relevant case study | 150-200 |
| `break_up` | Final follow-up before closing | 80-120 |

---

## 🖥️ Web UI

Launch the Streamlit dashboard:

```bash
streamlit run src/sales_email_gen/web_ui.py
```

The web UI provides four tabs:

| Tab | Description |
|-----|-------------|
| **📝 Prospect Form** | Enter prospect details, choose tone, generate emails |
| **✉️ Generated Emails** | View generated emails, copy text, score personalisation |
| **📧 Sequence Builder** | Build multi-email drip sequences with timeline view |
| **📋 Template Browser** | Browse, preview & customise templates |

---

## ⚙️ Configuration

All settings live in `config.yaml`:

```yaml
model:
  name: "gemma3"
  temperature: 0.7
  max_tokens: 2000

sequence:
  default_emails: 4
  delay_days: [0, 3, 7, 14]

personalization:
  min_score: 60
  target_score: 80

logging:
  level: "INFO"
  file: "sales_email_gen.log"
```

Environment variables (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `gemma3` | Default model |
| `LOG_LEVEL` | `INFO` | Logging level |
| `CONFIG_PATH` | `config.yaml` | Path to config file |

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src/sales_email_gen --cov-report=term-missing

# Run specific test file
pytest tests/test_core.py -v
pytest tests/test_cli.py -v
```

---

## 📦 Development

```bash
# Install in dev mode
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Syntax check
python -m py_compile src/sales_email_gen/core.py
python -m py_compile src/sales_email_gen/cli.py
```

---

## 📄 License

MIT
