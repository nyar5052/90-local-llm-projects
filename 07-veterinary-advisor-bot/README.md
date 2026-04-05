# 🐾 Veterinary Advisor Bot

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![LLM](https://img.shields.io/badge/LLM-Ollama%2FGemma4-orange.svg)
![UI](https://img.shields.io/badge/UI-Streamlit-red.svg)

> AI-powered pet health advice chatbot with medical disclaimers, symptom tracking, and breed-specific guidance.

## ✨ Features

- **Pet Profile Storage** — Save and manage multiple pet profiles
- **Symptom Analysis** — Get possible causes and urgency levels
- **Symptom History** — Track symptoms over time per pet
- **Breed-Specific Advice** — Tailored care tips for specific breeds
- **Nutrition Guidance** — Diet and feeding recommendations
- **8 Pet Types** — Dog, cat, bird, fish, rabbit, hamster, reptile, and more
- **Emergency Detection** — Flags urgent symptoms needing immediate vet attention
- **Medical Disclaimers** — Always reminds users to consult a real veterinarian
- **Streamlit Web UI** — Full-featured browser interface

## 📦 Installation

```bash
pip install -r requirements.txt
```

## 🚀 CLI Usage

```bash
# Interactive mode with pet profile setup
python -m vet_advisor.cli chat-cmd

# Quick start with pet info
python -m vet_advisor.cli chat-cmd --pet-type dog --name "Buddy" --breed "Labrador"

# List saved pets
python -m vet_advisor.cli list-pets
```

### Chat Commands

| Command | Description |
|---------|-------------|
| `/symptoms <desc>` | Analyze specific symptoms |
| `/breed` | Get breed-specific advice |
| `/nutrition` | Get nutrition advice |
| `/history` | View symptom history |
| `quit` | Exit the app |

## 🌐 Web UI

```bash
streamlit run src/vet_advisor/web_ui.py
```

The web UI provides:
- 💬 Interactive health consultation chat
- 🐾 Pet profile management with sidebar
- 🩺 Symptom analysis and history tracking
- 🐕 Breed-specific and nutrition advice

## 🧪 Running Tests

```bash
python -m pytest tests/ -v
```

## 📁 Project Structure

```
07-veterinary-advisor-bot/
├── src/
│   └── vet_advisor/
│       ├── __init__.py       # Package metadata
│       ├── core.py           # Core business logic
│       ├── cli.py            # Click CLI interface
│       ├── web_ui.py         # Streamlit web interface
│       ├── config.py         # Configuration management
│       └── utils.py          # Helper utilities
├── tests/
│   ├── __init__.py
│   ├── test_core.py          # Core logic tests
│   └── test_cli.py           # CLI tests
├── config.yaml               # Default configuration
├── setup.py                  # Package setup
├── requirements.txt          # Dependencies
├── Makefile                  # Common commands
├── .env.example              # Example environment variables
└── README.md                 # This file
```
