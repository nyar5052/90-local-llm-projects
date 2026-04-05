# 📋 Standup Generator

![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)
![Version 2.0](https://img.shields.io/badge/version-2.0.0-green.svg)
![License MIT](https://img.shields.io/badge/license-MIT-brightgreen.svg)

AI-powered daily standup update generator with Git integration, JIRA ticket detection, team views, history archive, and multiple templates — all powered by a local LLM via Ollama.

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 **AI Standup Generation** | Generate professional standups from task lists using local LLM |
| 🔀 **Git Integration** | Automatically include recent commits and branch info |
| 🎫 **JIRA Ticket Detection** | Auto-detect and format `PROJ-123` style references |
| 👥 **Team View** | Generate combined standups for multiple team members |
| 📜 **History Archive** | Save and browse past standups by date and member |
| 📝 **Templates** | Daily, weekly, sprint review, and async update templates |
| 🌐 **Web UI** | Streamlit-based web interface for easy interaction |
| ⚙️ **Configurable** | YAML configuration for all settings |

## 🏗️ Architecture

```
standup-generator/
├── src/standup_gen/
│   ├── __init__.py          # Package init
│   ├── core.py              # Business logic, LLM integration
│   ├── cli.py               # Click CLI with subcommands
│   └── web_ui.py            # Streamlit web interface
├── tests/
│   └── test_core.py         # Unit tests
├── config.yaml              # Configuration
├── setup.py                 # Package setup
├── Makefile                 # Development commands
├── requirements.txt         # Dependencies
└── README.md
```

## 📦 Installation

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) running locally

### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Or install as package (editable)
pip install -e ".[dev]"

# Copy environment config
cp .env.example .env
```

## 🚀 CLI Usage

The CLI uses subcommands for different operations:

### Generate Daily Standup

```bash
# Basic usage
standup-gen generate -t tasks.json

# With git log and save to history
standup-gen generate -t tasks.json --git-log --save

# Custom template and output
standup-gen generate -t tasks.json --template async --output standup.md

# With team and project names
standup-gen generate -t tasks.json --team "Backend" --project "API v2"
```

### Weekly Summary

```bash
standup-gen weekly -t tasks.json
standup-gen weekly -t tasks.json --git-log --output weekly.md
```

### Sprint Review

```bash
standup-gen sprint -t tasks.json --sprint-name "Sprint 14"
standup-gen sprint -t tasks.json -s "Sprint 14" --output sprint_review.md
```

### Browse History

```bash
# Last 7 days
standup-gen history

# Last 30 days, filtered by member
standup-gen history --days 30 --member alice
```

### Team Standup

```bash
standup-gen team -m alice -m bob -m charlie --tasks-dir ./team_tasks/
```

### Global Options

```bash
# Verbose output
standup-gen -v generate -t tasks.json

# Custom config file
standup-gen -c my_config.yaml generate -t tasks.json
```

## 🌐 Web UI

Launch the Streamlit web interface:

```bash
streamlit run src/standup_gen/web_ui.py
```

The web UI provides:

- **Generate Standup** — Quick task entry or JSON input, template selection, git integration toggle
- **History** — Browse past standups with date filters and stats
- **Team View** — Combined and individual team member standups
- **Settings** — Configure git, LLM, templates, and team members

## 🔀 Git Integration

Automatically includes recent commit history in standup reports:

```bash
# Include last day of commits
standup-gen generate -t tasks.json --git-log

# Custom repo path and days
standup-gen generate -t tasks.json --git-log --git-path /path/to/repo --git-days 3
```

Enable by default in `config.yaml`:

```yaml
git:
  enabled: true
  repo_path: "."
  days: 1
  include_branches: true
```

## 🎫 Ticket References

JIRA-style ticket references (e.g., `PROJ-123`) are automatically detected and formatted:

- Without link template: `PROJ-123` → **PROJ-123**
- With link template: `PROJ-123` → [PROJ-123](https://jira.example.com/browse/PROJ-123)

Configure in `config.yaml`:

```yaml
ticket:
  pattern: "[A-Z]+-\\d+"
  link_template: "https://jira.example.com/browse/{ticket}"
```

## 📋 Task JSON Format

### Dict format

```json
{
  "completed": [
    {"title": "Fix login bug PROJ-101", "status": "done"},
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

### List format

```json
[
  {"title": "Task A", "status": "done"},
  {"title": "Task B", "status": "in_progress"},
  {"title": "Task C", "status": "blocked"}
]
```

## ⚙️ Configuration

All settings are managed in `config.yaml`:

```yaml
llm:
  model: "llama3.2"
  temperature: 0.4
  max_tokens: 2000

standup:
  default_template: "daily"    # daily, weekly, sprint_review, async
  history_file: "standup_history.json"
  auto_save: true

git:
  enabled: true
  repo_path: "."
  days: 1
  include_branches: true

team:
  name: "My Team"
  members: ["alice", "bob"]

ticket:
  pattern: "[A-Z]+-\\d+"
  link_template: ""

logging:
  level: "INFO"
  file: "standup_gen.log"
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --tb=short
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and add tests
4. Run tests (`pytest tests/ -v`)
5. Commit (`git commit -m 'Add amazing feature'`)
6. Push (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

MIT
