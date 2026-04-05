# 🌍 Language Learning Bot

> Practice conversations in 15+ languages with an AI tutor that corrects grammar and teaches vocabulary.

## ✨ Features

- **15 Languages** — Spanish, French, German, Japanese, Korean, and more
- **3 Proficiency Levels** — Beginner, intermediate, and advanced
- **Conversational Practice** — Natural dialogue with corrections
- **Grammar Explanations** — Learn rules as you practice
- **Mini Lessons** — On-demand lessons on specific topics
- **Vocabulary Builder** — Useful words with translations and examples
- **Translation Help** — Quick translations on demand

## 📦 Installation

```bash
pip install -r requirements.txt
```

## 🚀 Usage

```bash
# Start learning Spanish as a beginner
python app.py --language spanish --level beginner

# Practice advanced French
python app.py --language french --level advanced

# Learn Japanese at intermediate level
python app.py --language japanese --level intermediate
```

### Special Commands

| Command | Description |
|---------|-------------|
| `/lesson <topic>` | Get a mini lesson on a topic |
| `/translate <text>` | Translate text |
| `/vocab` | Get useful vocabulary |
| `quit` | Exit the app |

### Example Session

```
🌍 Language Learning Bot - Practice Spanish at beginner level

╭─ 🎓 Spanish Tutor ──────────────────────────╮
│ ¡Hola! ¿Cómo te llamas?                     │
│ (Hello! What's your name?)                   │
╰──────────────────────────────────────────────╯

You: Me llamo John

╭─ 🎓 Tutor ──────────────────────────────────╮
│ ¡Muy bien, John! ¿De dónde eres?            │
│ (Very good, John! Where are you from?)       │
│                                              │
│ ✅ Your sentence was correct!                │
╰──────────────────────────────────────────────╯
```

## 🧪 Running Tests

```bash
pytest test_app.py -v
```

## 📁 Project Structure

```
06-language-learning-bot/
├── app.py              # Main application
├── requirements.txt    # Dependencies
├── test_app.py         # Unit tests
└── README.md           # This file
```
