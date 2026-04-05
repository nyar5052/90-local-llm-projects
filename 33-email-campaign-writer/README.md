# 📧 Email Campaign Writer

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code Style: PEP8](https://img.shields.io/badge/code%20style-pep8-orange.svg)](https://peps.python.org/pep-0008/)

> Generate professional, conversion-optimized marketing email sequences using a local LLM via Ollama.

---

## ✨ Features

- 📬 **Multi-Email Sequences** — Generate cohesive campaigns with 1–10 emails
- 🎯 **5 Campaign Types** — Welcome, promotional, nurture, re-engagement, product-launch
- 🔀 **A/B Subject Line Testing** — Generate multiple subject-line variants for split testing
- 🧩 **Personalization Tokens** — Auto-detect `{{first_name}}` style placeholders and render with real data
- 🌐 **HTML Email Preview** — Responsive HTML email template output
- 📅 **Sequence Timeline** — Visualize day-by-day send schedule
- 📊 **Campaign Metrics** — Estimated open & click rates per campaign type
- 🖥️ **Streamlit Web UI** — Full-featured browser-based campaign builder
- ⌨️ **Rich CLI** — Beautiful terminal output with tables, panels, and progress spinners
- ⚙️ **YAML Config** — Centralized configuration for LLM, campaign defaults, and metrics

## 🏗️ Architecture

```
33-email-campaign-writer/
├── src/
│   └── email_campaign/
│       ├── __init__.py        # Public API exports
│       ├── core.py            # Business logic, dataclasses, LLM interaction
│       ├── cli.py             # Click CLI interface
│       └── web_ui.py          # Streamlit web application
├── tests/
│   ├── conftest.py            # Pytest configuration & path setup
│   ├── test_core.py           # Core module tests
│   └── test_cli.py            # CLI integration tests
├── config.yaml                # App configuration
├── setup.py                   # Package setup with entry points
├── requirements.txt           # Python dependencies
├── Makefile                   # Dev shortcuts
├── .env.example               # Environment variable template
└── README.md
```

## 📋 Prerequisites

- **Python 3.10+**
- **[Ollama](https://ollama.ai/)** running locally with a model (e.g. `llama3`)

```bash
# Install & start Ollama, then pull a model
ollama serve
ollama pull llama3
```

## 🚀 Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or install as a package (editable mode)
pip install -e ".[dev]"
```

## ⌨️ CLI Usage

```bash
# Basic campaign generation
python src/email_campaign/cli.py --product "SaaS Tool" --audience "developers"

# Welcome campaign with 5 emails
python src/email_campaign/cli.py \
  --product "Fitness App" \
  --audience "health enthusiasts" \
  --type welcome --emails 5

# A/B subject line testing
python src/email_campaign/cli.py \
  --product "Online Course" --audience "marketers" --subject-test

# Show timeline + metrics
python src/email_campaign/cli.py \
  --product "SaaS Tool" --audience "developers" --timeline

# Personalize preview
python src/email_campaign/cli.py \
  --product "App" --audience "users" \
  --personalize '{"first_name":"Jane","company":"Acme"}'

# HTML preview output
python src/email_campaign/cli.py \
  --product "App" --audience "users" --html-preview

# Save to file
python src/email_campaign/cli.py \
  --product "Course" --audience "students" -o campaign.md
```

### CLI Options

| Option | Description | Default |
|--------|-------------|---------|
| `--product` | Product/service name **(required)** | — |
| `--audience` | Target audience **(required)** | — |
| `--emails` | Number of emails (1–10) | 3 |
| `--type` | Campaign type | promotional |
| `--subject-test` | Generate A/B subject variants | off |
| `--html-preview` | Save HTML email preview | off |
| `--timeline` | Show sequence timeline & metrics | off |
| `--personalize` | JSON user data for token replacement | — |
| `-o, --output` | Save campaign to file | — |

## 🖥️ Web UI

```bash
streamlit run src/email_campaign/web_ui.py
```

The Streamlit UI provides:
- **Campaign Builder** — Product, audience, type, and email count inputs
- **Subject A/B Testing** — Side-by-side subject line comparison
- **Email Preview** — Expandable email cards with personalization highlighting
- **HTML Preview** — Rendered HTML email in an embedded viewer
- **Timeline** — Day-by-day send schedule visualization
- **Metrics Dashboard** — Estimated open/click rate gauges
- **Token Editor** — Edit personalization values and preview results
- **JSON Export** — Download full campaign as structured JSON

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ -v --tb=short --cov=email_campaign
```

## ⚙️ Configuration

Edit `config.yaml` to customize:

```yaml
app:
  name: "Email Campaign Writer"
  version: "2.0.0"
llm:
  model: "llama3"
  temperature: 0.7
  max_tokens: 4096
campaign:
  default_type: "promotional"
  default_emails: 3
  max_emails: 10
  metrics:
    welcome:
      avg_open_rate: 0.82
      avg_click_rate: 0.26
    promotional:
      avg_open_rate: 0.21
      avg_click_rate: 0.025
```

## 📄 License

MIT
