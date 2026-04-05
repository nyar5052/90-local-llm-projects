# 🎯 Habit Tracker Analyzer

Track daily habits and get AI-powered analysis of patterns and streaks using a local Gemma 4 LLM via Ollama.

## Features

- **Habit Logging**: Quick daily habit check-ins with notes
- **Streak Tracking**: Current and best streaks for each habit
- **Completion Rates**: 30-day completion rates with visual progress bars
- **AI Analysis**: Intelligent pattern analysis and improvement suggestions
- **Habit Stacking**: AI suggests how to link habits for consistency
- **Visual Dashboard**: Rich terminal display of habit status

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) running locally with Gemma 4 model

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Log a Habit
```bash
python app.py log --habit "exercise" --done
python app.py log --habit "reading" --done --notes "Read 30 pages"
python app.py log --habit "meditation" --skip
```

### View Status
```bash
python app.py status
```

### Analyze Patterns
```bash
python app.py analyze --period month
python app.py analyze --period week
```

## Example Output

```
╭─────────── 🎯 Habit Tracker ───────────╮
│                                          │
╰──────────────────────────────────────────╯

┌────────────── 🎯 Habit Tracker ──────────────┐
│ Habit      │ Streak  │ Best │ 30-Day   │ Total│
├────────────┼─────────┼──────┼──────────┼──────┤
│ exercise   │ 🔥 5 d  │ ⭐ 12│ 73% 🟩🟩 │ 22   │
│ reading    │ 🔥 3 d  │ ⭐ 7 │ 60% 🟩🟩 │ 18   │
│ meditation │ 🔥 1 d  │ ⭐ 4 │ 40% 🟩🟩 │ 12   │
└────────────┴─────────┴──────┴──────────┴──────┘
```

## Testing

```bash
pytest test_app.py -v
```

## License

MIT
