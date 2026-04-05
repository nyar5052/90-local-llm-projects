# 📚 Curriculum Planner

Design comprehensive course curricula using a local LLM (Gemma 4 via Ollama).

## Features

- **Complete course design**: Learning objectives, weekly plans, assessments
- **Customizable duration**: Set any number of weeks
- **Multiple levels**: Beginner, intermediate, advanced
- **Resource recommendations**: Textbooks, videos, articles, tools
- **Assessment strategy**: Quizzes, assignments, projects
- **JSON export**: Save and share curricula

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) running locally with Gemma 4 model

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Design a course curriculum
```bash
python app.py --course "Intro to Machine Learning" --weeks 12 --level beginner
```

### With focus areas
```bash
python app.py --course "Web Development" --weeks 8 --level intermediate --focus "React,Node.js"
```

### Save to file
```bash
python app.py --course "Data Science" --weeks 16 --output curriculum.json
```

## Options

| Option | Short | Description |
|--------|-------|-------------|
| `--course` | `-c` | Course name (required) |
| `--weeks` | `-w` | Duration in weeks (default: 12) |
| `--level` | `-l` | beginner, intermediate, advanced |
| `--focus` | `-f` | Special focus areas (comma-separated) |
| `--output` | `-o` | Save to JSON file |

## Example Output

```
╭─────────── 📚 Course Overview ───────────╮
│ Intro to Machine Learning                 │
│ Level: beginner | Duration: 12 weeks      │
╰───────────────────────────────────────────╯

🎯 Learning Objectives:
  1. Understand basic ML concepts
  2. Implement simple models in Python

┌──────┬────────────────────┬──────────────────┐
│ Week │ Title              │ Topics           │
├──────┼────────────────────┼──────────────────┤
│ 1    │ Intro to ML        │ • What is ML?    │
│ 2    │ Supervised Learning│ • Regression     │
└──────┴────────────────────┴──────────────────┘
```

## Running Tests

```bash
pytest test_app.py -v
```
