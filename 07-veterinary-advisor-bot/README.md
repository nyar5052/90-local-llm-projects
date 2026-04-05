# 🐾 Veterinary Advisor Bot

> AI-powered pet health advice chatbot with medical disclaimers, powered by a local LLM.

## ✨ Features

- **Pet Profile Setup** — Configure pet type, breed, age, and weight
- **Symptom Analysis** — Get possible causes and urgency levels
- **8 Pet Types** — Dog, cat, bird, fish, rabbit, hamster, reptile, and more
- **Emergency Detection** — Flags urgent symptoms that need immediate vet attention
- **Medical Disclaimers** — Always reminds users to consult a real veterinarian
- **Conversation History** — Follow-up questions with full context

## 📦 Installation

```bash
pip install -r requirements.txt
```

## 🚀 Usage

```bash
# Interactive mode with pet profile setup
python app.py

# Quick start with pet info
python app.py --pet-type dog --name "Buddy" --breed "Labrador"
```

### Special Commands

| Command | Description |
|---------|-------------|
| `/symptoms <desc>` | Analyze specific symptoms |
| `quit` | Exit the app |

### Example Session

```
🐾 Veterinary Advisor Bot

╭─ ⚕️ Disclaimer ──────────────────────────────╮
│ This is AI-generated advice, NOT a substitute │
│ for professional veterinary care.             │
╰───────────────────────────────────────────────╯

🐾 About Buddy: He's been scratching a lot

╭─ 🩺 Vet Advisor ─────────────────────────────╮
│ Excessive scratching in dogs can indicate:    │
│ 1. Allergies (most common)                    │
│ 2. Flea infestation                           │
│ 3. Skin infection                             │
│ **Urgency:** Non-urgent                       │
│ **Recommendation:** Schedule a vet visit...   │
╰───────────────────────────────────────────────╯
```

## 🧪 Running Tests

```bash
pytest test_app.py -v
```

## 📁 Project Structure

```
07-veterinary-advisor-bot/
├── app.py              # Main application
├── requirements.txt    # Dependencies
├── test_app.py         # Unit tests
└── README.md           # This file
```
