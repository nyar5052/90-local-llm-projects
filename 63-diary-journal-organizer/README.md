# 📔 Diary Journal Organizer

Private diary with AI-powered insights, mood analysis, and theme discovery using a local Gemma 4 LLM via Ollama.

## Features

- **Daily Journal Entries**: Write and store private diary entries with mood and tags
- **Mood Analysis**: AI analyzes mood patterns over time
- **Theme Discovery**: Finds recurring themes and topics in your entries
- **Comprehensive Insights**: Generates summaries, patterns, and growth observations
- **Privacy First**: All data stored locally, AI runs on your machine

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) running locally with Gemma 4 model
- Start Ollama: `ollama serve`
- Pull model: `ollama pull gemma4`

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Write a New Entry
```bash
python app.py write --content "Had a wonderful day hiking with friends" --mood happy --tags "outdoors,friends"
```

### Interactive Writing
```bash
python app.py write
```

### Get Weekly Insights
```bash
python app.py insights --period week
```

### Mood Analysis Only
```bash
python app.py insights --period month --mood-only
```

### View Recent Entries
```bash
python app.py view --period week
```

## Example Output

```
╭──────── 📔 Diary Journal ────────╮
│ Generating weekly insights...     │
╰───────────────────────────────────╯

╭────────── ✨ Journal Insights ──────────╮
│ ## Summary                               │
│ A productive week with positive mood.    │
│                                          │
│ ## Mood Analysis                         │
│ - Overall trend: Improving               │
│ - Happiest day: Wednesday                │
│                                          │
│ ## Key Themes                            │
│ - Work productivity                      │
│ - Social connections                     │
╰──────────────────────────────────────────╯
```

## Testing

```bash
pytest test_app.py -v
```

## License

MIT
