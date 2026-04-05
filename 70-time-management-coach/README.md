# ⏱️ Time Management Coach

AI-powered time usage analysis and productivity coaching using a local Gemma 4 LLM via Ollama.

## Features

- **Time Analysis**: Analyze time logs with category breakdowns and visual charts
- **Productivity Scoring**: Get a data-driven productivity score
- **AI Coaching**: Personalized tips for specific productivity goals
- **Pomodoro Planning**: Generate Pomodoro-based daily plans
- **Deep Work Analysis**: Measure focused work time vs. shallow tasks
- **Work-Life Balance**: Assessment and recommendations

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) running locally with Gemma 4 model

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Analyze Time Log
```bash
python app.py review --log timelog.csv --analyze
```

### Get Productivity Tips
```bash
python app.py tips --goal "deep work"
python app.py tips --goal "reduce meeting time"
```

### Generate Pomodoro Plan
```bash
python app.py pomodoro --tasks "write report, review PR, update docs" --hours 6
```

## Time Log CSV Format

```csv
date,category,activity,duration
2024-03-25,Deep Work,Coding feature X,3.0
2024-03-25,Meetings,Sprint planning,1.5
2024-03-25,Email,Inbox processing,1.0
```

## Example Output

```
╭──────── ⏱️ Time Management Coach ────────╮
│ Analyzing your time usage...              │
╰───────────────────────────────────────────╯

┌──────────── ⏱️ Time Breakdown ────────────┐
│ Category  │ Hours │ Pct   │ Visual         │
├───────────┼───────┼───────┼────────────────┤
│ Deep Work │ 9.0h  │ 75.0% │ ███████████████│
│ Meetings  │ 2.0h  │ 16.7% │ ███            │
│ Email     │ 1.0h  │ 8.3%  │ ██             │
│ TOTAL     │ 12.0h │ 100%  │                │
└───────────┴───────┴───────┴────────────────┘
```

## Testing

```bash
pytest test_app.py -v
```

## License

MIT
