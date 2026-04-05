# 🏥 First Aid Guide Bot

![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)
![Version](https://img.shields.io/badge/version-1.0.0-orange)
![LLM: Ollama](https://img.shields.io/badge/LLM-Ollama-purple)

A production-grade, local LLM-powered first aid information assistant. Provides step-by-step guidance for common emergency situations, interactive triage, supply checklists, CPR instructions, and emergency contact management — all running privately on your machine.

---

> ## 🚨🚨🚨 EMERGENCY DISCLAIMER 🚨🚨🚨
>
> # ☎️ FOR LIFE-THREATENING EMERGENCIES, CALL 911 IMMEDIATELY
>
> ### ☠️ Poison Control: 1-800-222-1222
> ### 💬 Crisis Lifeline: 988
>
> **This tool is NOT a substitute for emergency medical services.**
> **This is NOT medical advice.**
>
> - Always seek professional medical evaluation for injuries and illness.
> - This tool provides **general first aid information only**.
> - **Do NOT delay calling 911** to use this tool.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🏥 **Situation Guides** | Step-by-step first aid instructions for 15+ common scenarios |
| 🔀 **Emergency Triage** | Quick decision-tree assessment for emergency situations |
| 📦 **Supply Checklist** | Complete first aid kit inventory with priority levels |
| ❤️ **CPR Guide** | Detailed CPR steps with timing information |
| 📞 **Emergency Contacts** | Manage personal emergency contacts |
| 🤖 **AI Chat** | Interactive first aid assistant with follow-up questions |

## 🏗️ Architecture

```
src/first_aid/
├── __init__.py        # Package metadata
├── core.py            # Core logic, data, decision trees, contact management
├── cli.py             # Click CLI with all commands
└── web_ui.py          # Streamlit web interface
tests/
├── test_core.py       # Unit tests for core logic
└── test_cli.py        # CLI integration tests
app.py                 # Original standalone script
config.yaml            # Configuration
setup.py               # Package setup
```

## 📋 Prerequisites

- **Python 3.10+**
- [Ollama](https://ollama.ai/) running locally with a model pulled (e.g., `ollama pull llama3`)

## 🚀 Installation

```bash
# Install in development mode
pip install -e ".[dev]"

# Or install dependencies directly
pip install -r requirements.txt
```

## 💻 CLI Usage

```bash
# Get first aid for a specific situation
first-aid guide --situation "minor burn"
first-aid guide -s "choking adult"

# Interactive chat mode
first-aid chat

# List common scenarios with severity levels
first-aid list

# Emergency triage assessment
first-aid triage --conscious --breathing --bleeding
first-aid triage --unconscious --not-breathing

# View first aid supply checklist
first-aid supplies
first-aid supplies --priority essential

# Display CPR steps
first-aid cpr

# Manage emergency contacts
first-aid contacts --list
first-aid contacts --add
first-aid contacts --remove
```

## 🌐 Web UI (Streamlit)

```bash
streamlit run src/first_aid/web_ui.py
```

The web interface provides:
- **🏥 Situation Guide** — Select from common scenarios or describe your own
- **🔀 Emergency Triage** — Interactive radio buttons for quick assessment
- **📦 Supply Checklist** — Filterable checklist with progress tracking
- **❤️ CPR Guide** — Step-by-step cards with a practice timer
- **📞 Emergency Contacts** — Add, view, and manage contacts

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v --tb=short

# With coverage
python -m pytest tests/ -v --cov=first_aid --cov-report=term-missing
```

## 🔧 Configuration

Edit `config.yaml` to customize:

```yaml
app:
  name: "First Aid Guide Bot"
  version: "1.0.0"
llm:
  model: "llama3"
  temperature: 0.3
  max_tokens: 1500
emergency:
  primary: "911"
  poison_control: "1-800-222-1222"
  crisis_line: "988"
```

## 🔒 Privacy

All processing happens **locally on your machine**. No data is sent to external servers. The LLM runs through Ollama on your own hardware.

## 📚 Emergency Resources

- **Emergency Services**: Call **911**
- **Poison Control**: **1-800-222-1222**
- **Crisis Lifeline**: **988**
- **American Red Cross First Aid App**: [Download](https://www.redcross.org/get-help/how-to-prepare-for-emergencies/mobile-apps.html)
- **Mayo Clinic First Aid**: https://www.mayoclinic.org/first-aid

---

> ## 🚨 REMINDER 🚨
>
> **This tool is for general informational purposes ONLY and is NOT medical advice.**
>
> **Always call 911 for life-threatening emergencies.**
> **Poison Control: 1-800-222-1222**
>
> Always seek professional medical care for injuries and illness. Do NOT rely on this tool in place of professional medical services.
