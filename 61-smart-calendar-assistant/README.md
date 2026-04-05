# 📅 Smart Calendar Assistant

AI-powered schedule optimization and meeting suggestions using a local Gemma 4 LLM via Ollama.

## Features

- **Schedule Optimization**: Analyzes your calendar and suggests rearrangements for better productivity
- **Meeting Time Suggestions**: Finds the best available slots for new meetings
- **Workload Analysis**: Evaluates daily load, work-life balance, and free time availability
- **Conflict Detection**: Identifies overlapping or too-close events
- **Rich Display**: Beautiful terminal output with tables and formatted panels

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

### View Schedule
```bash
python app.py --schedule calendar.json --view
```

### Optimize Schedule
```bash
python app.py --schedule calendar.json --optimize
```

### Suggest Meeting Time
```bash
python app.py --schedule calendar.json --suggest --duration "30 minutes" --attendees "engineering team"
```

### Analyze Workload
```bash
python app.py --schedule calendar.json --workload
```

## Calendar JSON Format

```json
{
  "events": [
    {
      "date": "2024-03-25",
      "time": "09:00",
      "title": "Team Standup",
      "duration": "30 min",
      "priority": "high"
    }
  ]
}
```

## Example Output

```
╭─────────── 📅 Smart Calendar Assistant ───────────╮
│ AI-powered schedule optimization and suggestions   │
╰────────────────────────────────────────────────────╯

┌──────────────── 📅 Current Schedule ────────────────┐
│ Date       │ Time  │ Event          │ Duration │ Pri │
├────────────┼───────┼────────────────┼──────────┼─────┤
│ 2024-03-25 │ 09:00 │ Team Standup   │ 30 min   │ high│
│ 2024-03-25 │ 10:00 │ Code Review    │ 60 min   │ med │
│ 2024-03-25 │ 14:00 │ Sprint Planning│ 90 min   │ high│
└────────────┴───────┴────────────────┴──────────┴─────┘
```

## Testing

```bash
pytest test_app.py -v
```

## License

MIT
