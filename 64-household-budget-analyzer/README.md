# 💰 Household Budget Analyzer

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)]()
[![Code Style](https://img.shields.io/badge/code%20style-production-blueviolet.svg)]()

> **AI-powered household expense analysis**, budgeting, and savings tracking — powered by a local LLM via Ollama.

---

## 🏗️ Architecture

```
64-household-budget-analyzer/
├── src/budget_analyzer/      # Main package
│   ├── __init__.py           # Package metadata & version
│   ├── core.py               # Business logic & analysis engine
│   ├── cli.py                # Click CLI interface
│   └── web_ui.py             # Streamlit web dashboard
├── tests/
│   ├── __init__.py
│   └── test_core.py          # Comprehensive test suite
├── config.yaml               # Budget limits, category rules, LLM settings
├── setup.py                  # Package installation & entry points
├── Makefile                  # Development shortcuts
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variable template
└── README.md
```

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📊 **Category Breakdown** | Visual spending analysis by category with percentage bars |
| 🤖 **AI Analysis** | Intelligent budget analysis & savings suggestions via local LLM |
| 📋 **Budget vs Actual** | Compare spending against configurable budget limits |
| 🏷️ **Auto-Categorization** | Rule-based expense categorization using keyword matching |
| 🐷 **Savings Goals** | Track progress toward savings targets with completion estimates |
| 🔄 **Recurring Detection** | Automatically find expenses that repeat monthly |
| 📈 **Monthly Trends** | Spending trends over time with visual charts |
| 💸 **Top Expenses** | Identify highest individual transactions |
| 📅 **Month Filtering** | Analyze specific months or all-time data |
| 🌐 **Web Dashboard** | Interactive Streamlit UI with charts and upload |

---

## 📋 Prerequisites

- **Python 3.10+**
- **[Ollama](https://ollama.ai/)** running locally with a model (e.g., llama3)
  ```bash
  ollama serve          # Start the server
  ollama pull llama3    # Pull the model
  ```

---

## 🚀 Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install as editable package (development)
pip install -e ".[dev]"
```

---

## 💻 CLI Usage

The CLI provides a `budget-analyzer` command group with multiple sub-commands.

### Analyze (AI-powered)
```bash
python -m budget_analyzer.cli analyze --file expenses.csv --month "March 2024"
```

### Category Breakdown
```bash
python -m budget_analyzer.cli breakdown --file expenses.csv --month "March 2024"
```

### Compare Months
```bash
python -m budget_analyzer.cli compare --file expenses.csv
```

### Auto-Categorize Expenses
```bash
python -m budget_analyzer.cli categorize --file expenses.csv
```

### Budget Check (vs limits)
```bash
python -m budget_analyzer.cli budget-check --file expenses.csv --month "March 2024"
```

### Savings Goal Tracker
```bash
python -m budget_analyzer.cli savings --name "Emergency Fund" --target 5000 --current 1200 --monthly 300
```

### Recurring Expense Detection
```bash
python -m budget_analyzer.cli recurring --file expenses.csv
```

### Monthly Trends & Top Expenses
```bash
python -m budget_analyzer.cli trends --file expenses.csv --top 5
```

---

## 🌐 Web UI

Launch the interactive Streamlit dashboard:

```bash
streamlit run src/budget_analyzer/web_ui.py
```

**Features:**
- 📁 Upload CSV via sidebar
- ⚙️ Adjust budget limits per category
- 🐷 Configure savings goals
- 📊 Interactive charts (bar, line, pie)
- 📋 Budget vs actual comparison table
- 🔄 Recurring expense list
- 🤖 AI analysis with one click

---

## ⚙️ Budget Configuration

Edit `config.yaml` to customize budget limits and category rules:

```yaml
budget:
  currency: "USD"
  categories:
    Groceries: 500       # Monthly budget limit
    Utilities: 200
    Entertainment: 150
  category_rules:
    Groceries: ["grocery", "supermarket", "walmart", "costco"]
    Utilities: ["electric", "water", "gas", "internet"]
```

### Savings Goals
```yaml
savings:
  default_goal: 1000
  emergency_fund_months: 6
```

### LLM Settings
```yaml
llm:
  model: "llama3"
  temperature: 0.5
  system_prompt: "You are an expert financial advisor."
```

---

## 📄 CSV Format

```csv
date,category,description,amount
2024-03-01,Groceries,Weekly shopping,150.00
2024-03-05,Utilities,Electric bill,95.50
2024-03-10,Entertainment,Movie tickets,35.00
```

**Supported date formats:** `YYYY-MM-DD`, `MM/DD/YYYY`, `DD/MM/YYYY`, `YYYY/MM/DD`

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src/budget_analyzer --cov-report=term-missing
```

---

## 📁 Project Structure

```
src/budget_analyzer/
├── __init__.py          # Version: 1.0.0
├── core.py              # All business logic
│   ├── load_expenses()           # CSV loading
│   ├── filter_by_month()         # Month filtering
│   ├── compute_category_breakdown()  # Category totals
│   ├── compute_total()           # Total spending
│   ├── display_breakdown()       # Rich table output
│   ├── analyze_budget()          # AI analysis (LLM)
│   ├── compare_months()          # AI month comparison
│   ├── categorize_expense()      # Rule-based categorization
│   ├── compare_budget_vs_actual()# Budget limit checks
│   ├── SavingsGoal              # Savings tracking class
│   ├── detect_recurring()        # Recurring detection
│   ├── compute_monthly_trends()  # Monthly totals
│   └── get_top_expenses()        # Highest transactions
├── cli.py               # Click CLI with 8 commands
└── web_ui.py            # Streamlit dashboard
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and add tests
4. Run the test suite (`pytest tests/ -v`)
5. Commit (`git commit -m 'Add amazing feature'`)
6. Push (`git push origin feature/amazing-feature`)
7. Open a Pull Request

---

## 📜 License

MIT
