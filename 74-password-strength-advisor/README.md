# 🔑 Password Strength Advisor

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Powered by Ollama](https://img.shields.io/badge/LLM-Ollama-orange.svg)](https://ollama.ai)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)]()

> **Enterprise-grade password analysis with Shannon entropy calculation, breach database checking, NIST SP 800-63B policy generation, and bulk analysis — all running locally.**

---

## ✨ Features

| Feature | Description | LLM Required |
|---------|-------------|:---:|
| 📊 **Entropy Calculation** | Shannon entropy with pattern detection and time-to-crack estimates | ❌ |
| 🛡️ **Breach Database Check** | Local dictionary check with l33tspeak variation detection | ❌ |
| 📋 **Policy Generator** | NIST SP 800-63B compliant policy with 10 rules | ❌ |
| 📦 **Bulk Analysis** | Analyze many passwords at once with masked output | ❌ |
| 🔐 **Secure Password Gen** | Cryptographically secure generation (Fisher-Yates shuffle) | ❌ |
| 🔬 **AI Analysis** | LLM-powered deep password and policy analysis | ✅ |
| 🖥️ **Streamlit Web UI** | Interactive strength meter, policy editor, bulk analyzer | — |
| 💻 **Rich CLI** | Subcommands: analyze, generate, policy, bulk | — |

## 🏗️ Architecture

```
74-password-strength-advisor/
├── src/password_advisor/
│   ├── __init__.py          # Package metadata
│   ├── core.py              # Business logic: entropy, breach check, policy
│   ├── cli.py               # Click CLI with subcommands
│   ├── web_ui.py            # Streamlit dashboard (4 tabs)
│   └── config.py            # YAML config management
├── tests/
│   ├── test_core.py         # Core logic tests (20+ test cases)
│   └── test_cli.py          # CLI integration tests
├── config.yaml              # Configuration
├── .env.example             # Environment variables
├── setup.py / Makefile      # Build & dev tools
└── README.md
```

### Strength Classification

| Entropy (bits) | Strength | Time to Crack | Color |
|----------------|----------|---------------|-------|
| ≥ 80 | 🟢 Very Strong | Centuries+ | Green |
| 60–79 | 🟢 Strong | Years | Green |
| 40–59 | 🟡 Fair | Days–Months | Yellow |
| 25–39 | 🟠 Weak | Minutes–Hours | Orange |
| < 25 | 🔴 Very Weak | Instant–Seconds | Red |

## 🚀 Quick Start

### Installation

```bash
cd 74-password-strength-advisor
pip install -r requirements.txt
cp .env.example .env
```

### CLI Usage

```bash
# Analyze password entropy (no LLM needed)
python -m src.password_advisor.cli --password "MyStr0ng!Pass#2024"

# Check against breach database
python -m src.password_advisor.cli --password "password123" --breach-check

# Full AI analysis
python -m src.password_advisor.cli --password "MyStr0ng!Pass#2024" --analyze

# Generate secure passwords
python -m src.password_advisor.cli generate --length 20 --count 10

# Show NIST-compliant policy
python -m src.password_advisor.cli policy

# Bulk analyze from file
python -m src.password_advisor.cli bulk --file passwords.txt

# Analyze policy document with AI
python -m src.password_advisor.cli --policy policy.txt --analyze
```

### 🖥️ Web UI

```bash
streamlit run src/password_advisor/web_ui.py
```

| Tab | Description |
|-----|-------------|
| 🔑 **Password Input** | Enter password, run entropy analysis and breach check |
| 📊 **Strength Meter** | Visual entropy bar, charset breakdown, breach status |
| 📋 **Policy Editor** | View NIST SP 800-63B policy rules |
| 📦 **Bulk Analyzer** | Paste or upload multiple passwords for batch analysis |

## 🧪 Testing

```bash
python -m pytest tests/ -v
python -m pytest tests/ -v --cov=src/password_advisor --cov-report=term-missing
```

## ⚙️ Configuration

```yaml
model:
  name: "llama3"
  temperature: 0.3
password:
  min_length: 12
  max_length: 128
  default_generate_length: 16
```

## 📦 Makefile Commands

| Command | Description |
|---------|-------------|
| `make install` | Install dependencies |
| `make test` | Run tests |
| `make run ARGS="--help"` | Run CLI |
| `make web` | Launch Streamlit UI |
| `make clean` | Clean artifacts |
