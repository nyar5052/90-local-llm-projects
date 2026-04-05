# 📔 Mood Journal Bot

> Private mood tracking with AI-powered insights and pattern analysis, all stored locally.

## ✨ Features

- **10 Mood Options** — Happy, calm, neutral, sad, angry, anxious, stressed, grateful, tired, excited
- **Energy Tracking** — Rate your energy level alongside mood
- **Local Storage** — All entries stored privately in JSON on your machine
- **AI Analysis** — Get insights on mood patterns and trends
- **History View** — Browse past entries in a formatted table
- **Statistics** — See mood distributions and averages
- **Privacy First** — No data leaves your computer

## 📦 Installation

```bash
pip install -r requirements.txt
```

## 🚀 Usage

```bash
# Write a new journal entry
python app.py journal

# Analyze mood patterns (last 7 days)
python app.py analyze

# Analyze last 30 days
python app.py analyze --days 30

# View recent entries
python app.py history

# View all-time statistics
python app.py stats
```

### Commands

| Command | Description |
|---------|-------------|
| `journal` | Write a new mood entry |
| `analyze` | Get AI insights on mood patterns |
| `history` | View recent journal entries |
| `stats` | Show mood statistics |

### Example Session

```
$ python app.py journal

╭─ 📔 Mood Journal ────────────────────────────╮
│ Record how you're feeling today               │
╰───────────────────────────────────────────────╯

Select your mood: 1 (😊 Happy)
Energy level (1-10): 8
📝 What's on your mind?: Had a productive day at work!

╭─ ✅ Entry Saved — 2024-01-15 14:30 ─────────╮
│ 😊 Happy | Energy: 8/10                      │
│ Had a productive day at work!                 │
╰───────────────────────────────────────────────╯

$ python app.py analyze

╭─ 🧠 AI Insights ─────────────────────────────╮
│ **Overall Trend:** Your mood has been mostly  │
│ positive this week with improving energy...   │
│                                               │
│ **Patterns:** You tend to feel happiest on    │
│ days with productive work sessions...         │
╰───────────────────────────────────────────────╯
```

## 🧪 Running Tests

```bash
pytest test_app.py -v
```

## 📁 Project Structure

```
10-mood-journal-bot/
├── app.py                  # Main application
├── requirements.txt        # Dependencies
├── test_app.py             # Unit tests
├── journal_entries.json    # Local data store (auto-created)
└── README.md               # This file
```

## 🔒 Privacy

All journal entries are stored locally in `journal_entries.json`. No data is ever sent to external servers. The AI analysis runs entirely on your local machine via Ollama.
