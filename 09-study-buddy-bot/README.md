# 📚 Study Buddy Bot

> AI-powered exam preparation assistant that quizzes, explains, and creates study plans using a local LLM.

## ✨ Features

- **5 Study Modes** — Quiz, explain, study plan, summarize, flashcards
- **Any Subject** — Works with any academic subject and topic
- **Interactive Q&A** — Ask follow-up questions for deeper understanding
- **Adaptive Teaching** — Uses Feynman technique and analogies
- **Practice Tests** — Mix of multiple choice, true/false, and short answer
- **Study Plans** — Day-by-day revision schedules with goals

## 📦 Installation

```bash
pip install -r requirements.txt
```

## 🚀 Usage

```bash
# Explain a topic
python app.py --subject "Biology" --topic "Cell Division" --mode explain

# Generate a quiz
python app.py --subject "History" --topic "World War 2" --mode quiz

# Create a study plan
python app.py --subject "Chemistry" --topic "Organic Chemistry" --mode plan

# Generate flashcards
python app.py --subject "Physics" --topic "Newton's Laws" --mode flashcards

# Interactive mode (choose mode at runtime)
python app.py --subject "Math" --topic "Calculus"
```

### Example Output

```
╭─ 📚 Quiz — Cell Division ───────────────────╮
│ **Q1:** What are the main phases of mitosis? │
│ A) Prophase, Metaphase, Anaphase, Telophase  │
│ B) G1, S, G2, M                              │
│ C) ...                                        │
│                                               │
│ **Answer Key:**                               │
│ 1. A — The four phases of mitosis are...     │
╰───────────────────────────────────────────────╯

📝 Your question: What's the difference between mitosis and meiosis?
╭─ 📚 Study Buddy ─────────────────────────────╮
│ Great question! The key differences are...    │
╰───────────────────────────────────────────────╯
```

## 🧪 Running Tests

```bash
pytest test_app.py -v
```

## 📁 Project Structure

```
09-study-buddy-bot/
├── app.py              # Main application
├── requirements.txt    # Dependencies
├── test_app.py         # Unit tests
└── README.md           # This file
```
