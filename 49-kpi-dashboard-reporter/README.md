# 📊 KPI Dashboard Reporter

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](#testing)
[![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen.svg)](#testing)

> **Production-grade KPI reporting system** with trend analysis, goal tracking, anomaly detection, and LLM-powered narrative insights — powered by a local Ollama LLM.

---

## 🏗️ Architecture

```
49-kpi-dashboard-reporter/
├── src/kpi_reporter/
│   ├── __init__.py          # Package metadata & version
│   ├── core.py              # Business logic (trends, goals, anomalies, reports)
│   ├── cli.py               # Click CLI with report/dashboard/goals/anomalies commands
│   └── web_ui.py            # Streamlit web dashboard
├── tests/
│   ├── test_core.py         # Core logic unit tests
│   └── test_cli.py          # CLI integration tests
├── config.yaml              # Configuration (targets, thresholds, model settings)
├── setup.py                 # Package installer
├── requirements.txt         # Python dependencies
├── Makefile                 # Build/test/run shortcuts
├── .env.example             # Environment variable template
└── README.md                # This file
```

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📈 **Trend Analysis** | Automatic period-over-period comparison with ↑↓→ indicators |
| 🎯 **Goal Tracking** | Compare KPI actuals vs configured targets with status labels |
| 🔍 **Anomaly Detection** | Flag values > N standard deviations from the mean |
| 📊 **Moving Averages** | Configurable sliding-window smoothing for trend charts |
| 🔔 **Alert System** | Flags KPIs with changes exceeding configurable thresholds |
| 📋 **Narrative Reports** | LLM-generated professional insights and recommendations |
| 🏢 **Executive Summaries** | C-suite–ready bullet-point summaries |
| 🌐 **Web Dashboard** | Interactive Streamlit UI with metric cards, charts, and progress bars |
| ⚙️ **Config-Driven** | YAML-based configuration for targets, thresholds, and model settings |
| 📝 **Structured Logging** | File and console logging with configurable levels |

---

## 📋 Prerequisites

- **Python 3.10+**
- **[Ollama](https://ollama.ai/)** running locally with the `gemma3` model (or configured model)
- The `common/` shared module (from the parent project)

---

## 🚀 Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or install as a package (editable mode)
pip install -e ".[dev]"
```

### Environment Setup

```bash
cp .env.example .env
# Edit .env with your settings
```

---

## 💻 CLI Usage

The CLI provides four commands via a Click command group:

### `report` — Full Narrative KPI Report

```bash
# Monthly report with alerts
python -m src.kpi_reporter.cli report --file kpis.csv --period monthly

# Quarterly report without alerts
python -m src.kpi_reporter.cli report -f kpis.csv -p Q1-2024 --no-alerts

# With custom config
python -m src.kpi_reporter.cli --config custom.yaml report -f kpis.csv
```

### `dashboard` — KPI Dashboard Table

```bash
python -m src.kpi_reporter.cli dashboard --file kpis.csv
```

### `goals` — Goal Tracking Progress

```bash
python -m src.kpi_reporter.cli goals --file kpis.csv
```

Shows each KPI's actual vs target with progress bars and status indicators:
- ✅ **Achieved** (≥100% of target)
- 📈 **On Track** (≥80%)
- ⚠️ **At Risk** (≥50%)
- 🔴 **Behind** (<50%)

### `anomalies` — Anomaly Detection

```bash
# Default threshold (2.0σ)
python -m src.kpi_reporter.cli anomalies --file kpis.csv

# Custom threshold
python -m src.kpi_reporter.cli anomalies -f kpis.csv --threshold 1.5
```

### Global Options

| Option | Description |
|--------|-------------|
| `--config`, `-c` | Path to config YAML (default: `config.yaml`) |
| `--help` | Show help message |

---

## 🌐 Web UI (Streamlit)

Launch the interactive web dashboard:

```bash
streamlit run src/kpi_reporter/web_ui.py
```

### Web UI Tabs

| Tab | Description |
|-----|-------------|
| 📄 **KPI Upload** | Upload CSV, preview raw data |
| 📊 **Metric Cards** | `st.metric` cards with delta indicators for each KPI |
| 🎯 **Goal Progress** | Progress bars showing actual vs target for each KPI |
| 📈 **Trend Charts** | Line charts with moving averages and anomaly warnings |

### Sidebar Controls

- **File Upload**: Drag-and-drop CSV upload
- **Period Selection**: Monthly / Quarterly / Yearly
- **Target Inputs**: Set/override KPI targets dynamically
- **Anomaly Threshold**: Adjustable σ slider (1.0 – 4.0)

---

## 📊 Input Format

CSV with a period column and numeric KPI columns:

```csv
month,revenue,customers,churn_rate,nps_score
Jan,100000,500,5.2,72
Feb,110000,520,4.8,75
Mar,105000,510,5.5,70
Apr,120000,550,4.2,78
```

The period column is auto-detected (looks for `period`, `month`, `date`, `week`, `quarter`, `year` in column names).

---

## ⚙️ Configuration

Edit `config.yaml` to customize behavior:

```yaml
model:
  name: "gemma3"          # Ollama model name
  temperature: 0.3        # LLM creativity (0.0-1.0)
  max_tokens: 3500        # Max response length

targets:                  # KPI target values for goal tracking
  revenue: 120000
  customers: 600
  churn_rate: 3.0
  nps_score: 80

anomaly_detection:
  enabled: true           # Enable/disable anomaly detection
  threshold: 2.0          # Standard deviations for flagging

moving_average:
  window: 3               # Sliding window size

alert_threshold_pct: 10   # % change threshold for alerts

logging:
  level: "INFO"           # DEBUG, INFO, WARNING, ERROR
  file: "kpi_reporter.log"
```

---

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ -v --cov=src/kpi_reporter --cov-report=term-missing

# Run specific test class
python -m pytest tests/test_core.py::TestTrackGoals -v
```

### Test Coverage

| Module | Tests |
|--------|-------|
| `core.py` | SafeFloat, LoadKpiData, ComputeKpiTrends, TrackGoals, DetectAnomalies, ComputeMovingAverage, GenerateAlertSummary, GenerateExecutiveSummary, GenerateKpiReport, ComputeAnalytics, LoadConfig |
| `cli.py` | Report, Dashboard, Goals, Anomalies, MainGroup |

---

## 📋 Example Output

```
📊 KPI Dashboard Reporter - monthly
✓ Loaded 4 periods from kpis.csv

┌──────────────┬──────────┬──────────┬──────────┬─────────┬───────┬──────────┐
│ KPI          │   Latest │ Previous │   Change │ Change% │ Trend │      Avg │
├──────────────┼──────────┼──────────┼──────────┼─────────┼───────┼──────────┤
│ revenue      │ 120,000  │ 105,000  │ +15,000  │ +14.3%  │  ↑    │ 108,750  │
│ customers    │     550  │     510  │     +40  │  +7.8%  │  ↑    │     520  │
│ churn_rate   │    4.20  │    5.50  │   -1.30  │ -23.6%  │  ↓    │    4.93  │
│ nps_score    │   78.00  │   70.00  │   +8.00  │ +11.4%  │  ↑    │   73.75  │
└──────────────┴──────────┴──────────┴──────────┴─────────┴───────┴──────────┘

🔔 Alerts
  ⚠️ revenue increased by 14.3%
  ⚠️ churn_rate decreased by 23.6%
  ⚠️ nps_score increased by 11.4%

🎯 Goal Tracking
  revenue:    ✅ Achieved (100.0%)
  customers:  📈 On Track (91.7%)
  churn_rate:  🔴 Behind (140.0% — lower is better)
  nps_score:  📈 On Track (97.5%)
```

---

## 📜 License

MIT License
