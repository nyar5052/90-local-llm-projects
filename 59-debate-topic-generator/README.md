# 🎙️ Debate Topic Generator

Generate debate topics with balanced pro/con arguments using a local LLM (Gemma 4 via Ollama).

## Features

- **Balanced arguments**: Pro and con sides with evidence
- **Research points**: Supporting evidence for each argument
- **Counterarguments**: Common rebuttals and responses
- **Key questions**: Discussion starters and critical thinking prompts
- **Adjustable complexity**: Basic, intermediate, advanced
- **Multiple topics**: Generate several debate topics at once

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) running locally with Gemma 4 model

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Generate debate topics
```bash
python app.py --subject "technology" --complexity advanced --topics 5
```

### Quick basic topics
```bash
python app.py --subject "education" --complexity basic --topics 3
```

### Save to file
```bash
python app.py --subject "environment" --output debate_topics.json
```

## Options

| Option | Short | Description |
|--------|-------|-------------|
| `--subject` | `-s` | Subject area (required) |
| `--complexity` | `-c` | basic, intermediate, advanced (default: intermediate) |
| `--topics` | `-t` | Number of topics (default: 3) |
| `--output` | `-o` | Save to JSON file |

## Example Output

```
╭──── 🎙️ Debate Topics ────╮
│ Technology                 │
│ Complexity: advanced       │
╰────────────────────────────╯

Topic 1: AI should be regulated by governments

┌──── ✓ PRO ────┐  ┌──── ✗ CON ────┐
│ • Prevents     │  │ • Stifles     │
│   misuse       │  │   innovation  │
│ • Protects     │  │ • Hard to     │
│   jobs         │  │   enforce     │
└────────────────┘  └───────────────┘

⚡ Key Counterarguments:
  • Self-regulation could be more effective
```

## Running Tests

```bash
pytest test_app.py -v
```
