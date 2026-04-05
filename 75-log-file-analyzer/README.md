# 📊 Log File Analyzer

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Powered by Ollama](https://img.shields.io/badge/LLM-Ollama-orange.svg)](https://ollama.ai)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)]()

> **Production-grade log analysis with a built-in pattern library, anomaly detection, error clustering, timeline visualization, and configurable alert rules — powered by local AI.**

---

## ✨ Features

| Feature | Description | LLM Required |
|---------|-------------|:---:|
| 🔍 **Pattern Library** | 10 built-in patterns: DB errors, auth failures, HTTP errors, timeouts, crashes, etc. | ❌ |
| ⚡ **Anomaly Detection** | Error bursts, repeated messages, timestamp gaps | ❌ |
| 📦 **Error Clustering** | Group similar errors by normalized pattern | ❌ |
| 📈 **Timeline Visualization** | Chronological event timeline with severity coloring | ❌ |
| 🚨 **Alert Rules** | Configurable thresholds for critical events, error rates, auth failures | ❌ |
| 🔬 **AI Analysis** | Deep LLM-powered log analysis with root cause suggestions | ✅ |
| 🔗 **AI Error Clustering** | LLM-powered semantic error grouping | ✅ |
| 🖥️ **Streamlit Web UI** | Interactive dashboard with 4 tabs | — |
| 💻 **Rich CLI** | Beautiful terminal tables and panels | — |

## 🏗️ Architecture

```
75-log-file-analyzer/
├── src/log_analyzer/
│   ├── __init__.py          # Package metadata
│   ├── core.py              # Business logic: patterns, anomalies, clustering
│   ├── cli.py               # Click CLI with Rich output
│   ├── web_ui.py            # Streamlit dashboard (4 tabs)
│   └── config.py            # YAML config management
├── tests/
│   ├── test_core.py         # Core logic tests (25+ test cases)
│   └── test_cli.py          # CLI integration tests
├── config.yaml              # Configuration
├── .env.example             # Environment variables
├── setup.py / Makefile      # Build & dev tools
└── README.md
```

### Built-in Pattern Library

| Pattern | Category | Severity | Description |
|---------|----------|----------|-------------|
| `database_error` | Database | 🟠 Error | DB connectivity/query errors |
| `auth_failure` | Security | 🟡 Warning | Auth/login failures |
| `http_error` | HTTP | 🟠 Error | HTTP 4xx/5xx responses |
| `timeout` | Performance | 🟠 Error | Operation timeouts |
| `memory_issue` | Resources | 🔴 Critical | OOM / memory exhaustion |
| `disk_issue` | Resources | 🔴 Critical | Disk space issues |
| `connection_error` | Network | 🟠 Error | Connection refused/reset |
| `ssl_tls_error` | Security | 🟠 Error | Certificate/TLS errors |
| `crash` | Application | 🔴 Critical | Segfault/panic/fatal |
| `rate_limit` | Performance | 🟡 Warning | Rate limiting triggered |

### Alert Rules

```
🚨 Critical Events    → Threshold: 1  (any critical = alert)
🚨 Error Rate         → Threshold: 10 (>10 errors = alert)
🚨 Auth Failures      → Threshold: 5  (>5 auth fails = alert)
🚨 Timeouts           → Threshold: 3  (>3 timeouts = alert)
```

## 🚀 Quick Start

### Installation

```bash
cd 75-log-file-analyzer
pip install -r requirements.txt
cp .env.example .env
```

### CLI Usage

```bash
# AI-powered log analysis
python -m src.log_analyzer.cli --file server.log --focus errors

# Pattern matching (no LLM — instant!)
python -m src.log_analyzer.cli --file server.log --patterns

# Anomaly detection (no LLM)
python -m src.log_analyzer.cli --file server.log --anomalies

# Build event timeline (no LLM)
python -m src.log_analyzer.cli --file server.log --timeline

# Evaluate alert rules (no LLM)
python -m src.log_analyzer.cli --file server.log --alerts

# AI error clustering
python -m src.log_analyzer.cli --file server.log --cluster

# Analyze last 500 lines with system context
python -m src.log_analyzer.cli --file server.log --last 500 --context "Production API server"

# Save results
python -m src.log_analyzer.cli --file server.log --focus all --output analysis.md
```

### 🖥️ Web UI

```bash
streamlit run src/log_analyzer/web_ui.py
```

| Tab | Description |
|-----|-------------|
| 📤 **Log Upload** | Upload/paste logs, run AI analysis, pattern matching, anomaly detection |
| ❌ **Error Table** | Clustered error view with example lines |
| 🔍 **Pattern Matches** | Pattern library matches with category breakdown chart |
| 📈 **Timeline Chart** | Chronological event timeline with severity icons |

## 🧪 Testing

```bash
python -m pytest tests/ -v
python -m pytest tests/ -v --cov=src/log_analyzer --cov-report=term-missing
```

## ⚙️ Configuration

```yaml
model:
  name: "llama3"
  temperature: 0.3
analysis:
  max_log_chars: 15000       # Truncate large files for LLM
  pattern_matching: true     # Enable pattern library
  anomaly_detection: true    # Enable anomaly detection
```

## 📦 Makefile Commands

| Command | Description |
|---------|-------------|
| `make install` | Install dependencies |
| `make test` | Run tests |
| `make run ARGS="--help"` | Run CLI |
| `make web` | Launch Streamlit UI |
| `make clean` | Clean artifacts |
