# 📚 Reading List Manager

AI-powered reading list management with book summaries and personalized recommendations using a local Gemma 4 LLM via Ollama.

## Features

- **Book Management**: Add, list, and track books with status and ratings
- **AI Summaries**: Get comprehensive AI-generated book summaries
- **Smart Recommendations**: Personalized book recommendations based on reading history
- **Reading Analysis**: Insights into your reading habits and patterns
- **Status Tracking**: Track books as to-read, reading, completed, or dropped

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) running locally with Gemma 4 model

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Add a Book
```bash
python app.py add --title "Clean Code" --author "Robert Martin" --genre "technical"
```

### Get Recommendations
```bash
python app.py recommend --genre "technical"
```

### Get Book Summary
```bash
python app.py summary --title "Clean Code" --author "Robert Martin"
```

### List Books
```bash
python app.py list
python app.py list --status reading
```

### Analyze Reading Habits
```bash
python app.py analyze
```

## Example Output

```
╭───────── 📚 Reading List Manager ─────────╮
│                                             │
╰─────────────────────────────────────────────╯

┌──────────────── 📚 Reading List ────────────────┐
│ ID │ Title           │ Author        │ Status    │
├────┼─────────────────┼───────────────┼───────────┤
│ 1  │ Clean Code      │ Robert Martin │ ✅ done   │
│ 2  │ Design Patterns │ GoF           │ 📖 reading│
└────┴─────────────────┴───────────────┴───────────┘
```

## Testing

```bash
pytest test_app.py -v
```

## License

MIT
