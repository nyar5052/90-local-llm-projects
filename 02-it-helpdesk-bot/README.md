# 🖥️ IT Helpdesk Bot

> AI-powered IT support chatbot for diagnosing and resolving common tech issues using a local LLM.

## ✨ Features

- **Category-Based Support** — Choose from 7 support categories (hardware, software, network, etc.)
- **Conversational Troubleshooting** — Multi-turn dialogue with context awareness
- **Step-by-Step Solutions** — Clear, numbered troubleshooting instructions
- **Smart Escalation** — Recommends professional help for complex issues
- **Conversation History** — Maintains full context throughout the session
- **Rich CLI Interface** — Beautiful formatted output with panels and colors

## 📦 Installation

```bash
pip install -r requirements.txt
```

## 🚀 Usage

```bash
# Interactive mode with category selection
python app.py

# Pre-select a category
python app.py --category 3   # Network Issues
```

### Support Categories

| # | Category | Description |
|---|----------|-------------|
| 1 | 🖥️ Hardware | Computer hardware, peripherals, monitors |
| 2 | 💾 Software | Application errors, installations, updates |
| 3 | 🌐 Network | WiFi, ethernet, VPN, connectivity |
| 4 | 🔒 Security | Passwords, malware, phishing |
| 5 | 📧 Email | Email setup, sending/receiving |
| 6 | 🖨️ Printer | Printer setup, drivers, print jobs |
| 7 | 💬 General | Any other IT question |

### Example Session

```
🖥️ IT Helpdesk Bot
Select a category: 3

You: My WiFi keeps disconnecting every few minutes

╭─ 🤖 IT Support ─────────────────────────────╮
│ Let's troubleshoot your WiFi issue:          │
│ 1. Restart your router and modem...          │
│ 2. Check for driver updates...               │
╰──────────────────────────────────────────────╯
```

## 🧪 Running Tests

```bash
pytest test_app.py -v
```

## 📁 Project Structure

```
02-it-helpdesk-bot/
├── app.py              # Main application
├── requirements.txt    # Dependencies
├── test_app.py         # Unit tests
└── README.md           # This file
```
