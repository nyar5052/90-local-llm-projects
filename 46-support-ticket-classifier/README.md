# 🎫 Support Ticket Classifier

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)
![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen)
![AI Powered](https://img.shields.io/badge/AI-Ollama%20%2F%20Gemma-orange?logo=ai)

**AI-powered support ticket classification with priority queue management, SLA tracking, team routing, and analytics — all running locally via Ollama.**

---

## ✨ Features

- 🤖 **AI Classification** — Categorize tickets into custom categories using a local LLM
- 🚨 **Priority Queue** — Tickets sorted by urgency with weighted priority scoring
- ⏱️ **SLA Tracking** — Automatic deadline computation per priority level
- 🏢 **Team Routing** — Route tickets to the right team based on category
- 💬 **Auto-Response Drafts** — Generate customer-facing responses instantly
- 📊 **Analytics Dashboard** — Category/priority distribution, confidence metrics, SLA compliance
- 🖥️ **CLI + Web UI** — Full-featured Click CLI and Streamlit web dashboard
- ⚙️ **Config-Driven** — YAML-based configuration for categories, SLA, routing, and model settings
- 📈 **Batch Processing** — Classify hundreds of tickets from CSV with progress tracking
- 🔒 **100% Local** — All data stays on your machine via Ollama

---

## 🏗️ Architecture

```
46-support-ticket-classifier/
├── src/ticket_classifier/
│   ├── __init__.py          # Package metadata
│   ├── core.py              # Business logic (classification, SLA, routing, analytics)
│   ├── cli.py               # Click CLI interface
│   └── web_ui.py            # Streamlit web dashboard
├── tests/
│   ├── test_core.py         # Core logic tests
│   └── test_cli.py          # CLI integration tests
├── config.yaml              # Runtime configuration
├── setup.py                 # Package setup
├── requirements.txt         # Dependencies
├── Makefile                 # Dev workflow commands
└── .env.example             # Environment template
```

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                        │
│          ┌──────────┐    ┌──────────────┐               │
│          │   CLI    │    │  Streamlit   │               │
│          │ (Click)  │    │   Web UI     │               │
│          └────┬─────┘    └──────┬───────┘               │
│               │                 │                        │
│          ┌────▼─────────────────▼───────┐               │
│          │        core.py               │               │
│          │  ┌───────────────────────┐   │               │
│          │  │ classify_ticket()     │   │               │
│          │  │ build_priority_queue()│   │               │
│          │  │ compute_sla_deadlines│   │               │
│          │  │ route_to_team()      │   │               │
│          │  │ compute_analytics()  │   │               │
│          │  └───────────┬───────────┘   │               │
│          └──────────────┼───────────────┘               │
│                         │                                │
│          ┌──────────────▼───────────────┐               │
│          │     Ollama (Local LLM)       │               │
│          │        Gemma 3               │               │
│          └──────────────────────────────┘               │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Installation

### Prerequisites

- **Python 3.10+**
- **[Ollama](https://ollama.ai/)** running locally with a model (e.g., `gemma3`)

### Quick Start

```bash
# Clone and navigate to the project
cd 46-support-ticket-classifier

# Install dependencies
pip install -r requirements.txt

# Or install as editable package with dev tools
pip install -e ".[dev]"
```

### Verify Ollama

```bash
# Start Ollama
ollama serve

# Pull a model (if not already available)
ollama pull gemma3
```

---

## 💻 CLI Usage

The CLI provides three commands: `classify`, `analytics`, and `priority-queue`.

### Classify Tickets

```bash
# Basic classification
python -m ticket_classifier.cli classify --file tickets.csv --categories "billing,technical,account"

# Use config file categories (from config.yaml)
python -m ticket_classifier.cli classify -f tickets.csv

# Specify text column explicitly
python -m ticket_classifier.cli classify -f tickets.csv -c "billing,technical" --column description

# Custom config file
python -m ticket_classifier.cli --config my_config.yaml classify -f tickets.csv
```

### View Analytics

```bash
python -m ticket_classifier.cli analytics --file tickets.csv --categories "billing,technical,account"
```

### Priority Queue

```bash
python -m ticket_classifier.cli priority-queue --file tickets.csv --categories "billing,technical,account"
```

### Example Output

```
🎫 Support Ticket Classifier
✓ Loaded 50 tickets from tickets.csv
Categories: billing, technical, account, feature_request, general
Text column: description

┌────┬──────────────────────┬───────────┬──────────┬────────────┬──────────────┬────────────────────┐
│ #  │ Ticket               │ Category  │ Priority │ Confidence │ Team         │ Suggested Response │
├────┼──────────────────────┼───────────┼──────────┼────────────┼──────────────┼────────────────────┤
│ 1  │ Cannot access my ... │ technical │ 🟠 High  │ 92%        │ engineering  │ We're investigating│
│ 2  │ Charged twice for .. │ billing   │ 🔴 Crit  │ 95%        │ finance-team │ Reviewing charge.. │
│ 3  │ Add dark mode to ... │ feature   │ 🟢 Low   │ 88%        │ product-team │ Feature request..  │
└────┴──────────────────────┴───────────┴──────────┴────────────┴──────────────┴────────────────────┘

📊 Classification Summary
  Total Tickets: 50
  By Category:
    billing: 18 | technical: 22 | account: 10
  By Priority:
    🟢 Low: 10 | 🟡 Medium: 20 | 🟠 High: 15 | 🔴 Critical: 5
  Average Confidence: 87.3%
  SLA Compliance: 90.0%
```

---

## 🌐 Web UI

Launch the Streamlit dashboard:

```bash
streamlit run src/ticket_classifier/web_ui.py
```

The web UI provides four tabs:

| Tab | Description |
|-----|-------------|
| 📥 **Ticket Input** | Upload CSV files or paste individual tickets for classification |
| 📋 **Results** | View classification results in a color-coded table |
| 🚨 **Priority Queue** | See tickets sorted by priority with SLA countdown |
| 📊 **Analytics** | Interactive charts for category/priority distribution and metrics |

### Sidebar Controls

- **Config file** — Load custom YAML configuration
- **Categories** — Edit classification categories on the fly
- **Temperature** — Adjust LLM creativity (0.0 = deterministic, 1.0 = creative)
- **SLA Hours** — Configure SLA deadlines per priority level
- **Ollama Status** — Live connection indicator

---

## ⚙️ Configuration

All settings are managed via `config.yaml`:

```yaml
model:
  name: "gemma3"            # Ollama model name
  temperature: 0.2          # LLM temperature (0.0–1.0)
  max_tokens: 2000          # Max response tokens

categories:                 # Classification categories
  - billing
  - technical
  - account
  - feature_request
  - general

sla_hours:                  # SLA deadlines (hours)
  critical: 1
  high: 4
  medium: 8
  low: 24

team_routing:               # Category → team mapping
  billing: "finance-team"
  technical: "engineering-team"
  account: "account-management"
  feature_request: "product-team"
  general: "support-team"

priority_weights:           # Queue sorting weights
  critical: 4
  high: 3
  medium: 2
  low: 1
```

---

## 📚 API Reference

### Core Functions (`ticket_classifier.core`)

| Function | Description |
|----------|-------------|
| `load_config(path)` | Load YAML config with defaults |
| `load_tickets(file_path)` | Load tickets from CSV file |
| `find_text_column(data)` | Auto-detect the text column |
| `classify_ticket(text, categories)` | Classify a single ticket via LLM |
| `classify_tickets_batch(tickets, categories, text_col)` | Batch-classify tickets with progress |
| `build_priority_queue(tickets, classifications, text_col)` | Build priority-sorted queue |
| `compute_sla_deadlines(classifications)` | Compute SLA deadlines per ticket |
| `route_to_team(classification, routing_rules)` | Route ticket to team |
| `generate_auto_response(ticket_text, classification)` | Draft customer auto-response |
| `compute_analytics(classifications, categories)` | Compute analytics summary |

### CLI Commands (`ticket_classifier.cli`)

| Command | Description |
|---------|-------------|
| `classify` | Classify tickets from a CSV file |
| `analytics` | Show analytics summary |
| `priority-queue` | Display priority-sorted queue |

---

## 📁 Input Format

CSV file with at least one text column (auto-detected):

```csv
id,subject,description,customer
1,Login issue,Cannot access my account,john@test.com
2,Billing error,Charged twice this month,jane@test.com
3,Feature request,Please add dark mode,bob@test.com
```

---

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ -v --cov=ticket_classifier --cov-report=term-missing

# Run specific test file
python -m pytest tests/test_core.py -v
python -m pytest tests/test_cli.py -v
```

---

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/my-feature`
3. **Make** your changes and add tests
4. **Run** the test suite: `python -m pytest tests/ -v`
5. **Commit** with a descriptive message
6. **Push** and open a Pull Request

### Development Setup

```bash
# Install in development mode
pip install -e ".[dev]"

# Run linting
python -m py_compile src/ticket_classifier/core.py
python -m py_compile src/ticket_classifier/cli.py

# Run tests
python -m pytest tests/ -v --tb=short
```

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

<p align="center">
  Built with ❤️ using <a href="https://ollama.ai">Ollama</a> and local LLMs
</p>
