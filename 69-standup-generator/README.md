# 📋 Standup Generator

Generate professional daily standup updates from task lists and git logs using a local Gemma 4 LLM via Ollama.

## Features

- **Task Import**: Load tasks from JSON files with flexible formats
- **Git Integration**: Automatically include recent git activity
- **Smart Categorization**: Auto-categorizes tasks into yesterday/today/blockers
- **Weekly Summaries**: Generate weekly status reports
- **Task Preview**: Preview categorization before generating
- **Export**: Save standup updates to files

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) running locally with Gemma 4 model

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Generate Daily Standup
```bash
python app.py --tasks tasks.json
```

### Include Git Log
```bash
python app.py --tasks tasks.json --git-log
```

### Weekly Summary
```bash
python app.py --tasks tasks.json --weekly
```

### Preview Tasks
```bash
python app.py --tasks tasks.json --preview
```

### Save to File
```bash
python app.py --tasks tasks.json --output standup.md
```

## Tasks JSON Format

```json
{
  "completed": [
    {"title": "Fix login bug", "status": "done"},
    {"title": "Update documentation", "status": "done"}
  ],
  "today": [
    {"title": "Implement user profile", "status": "in_progress"}
  ],
  "blockers": [
    {"title": "Waiting for API keys", "status": "blocked"}
  ]
}
```

Or as a flat list:
```json
[
  {"title": "Task A", "status": "done"},
  {"title": "Task B", "status": "in_progress"},
  {"title": "Task C", "status": "blocked"}
]
```

## Example Output

```markdown
## 📋 Daily Standup - March 25, 2024

### ✅ Yesterday
- Fixed login bug affecting 200+ users
- Updated API documentation for v2 endpoints

### 🎯 Today
- Implement user profile page (high priority)
- Review PR #42 for auth changes

### 🚧 Blockers
- Waiting for API keys from DevOps team
```

## Testing

```bash
pytest test_app.py -v
```

## License

MIT
