# 📝 Quiz Generator

Auto-generate quizzes from any topic using a local LLM (Gemma 4 via Ollama).

## Features

- **Multiple question formats**: Multiple choice, true/false, short answer, or mixed
- **Adjustable difficulty**: Easy, medium, or hard
- **Interactive mode**: Take the quiz directly in the terminal with scoring
- **Export to JSON**: Save quizzes for later use or integration
- **Rich CLI output**: Beautiful terminal formatting with color-coded results

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) running locally with the Gemma 4 model

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Generate a quiz (display only)
```bash
python app.py --topic "World War II" --questions 10 --type multiple-choice
```

### Generate with answers shown
```bash
python app.py --topic "Python Programming" --questions 5 --show-answers
```

### Interactive quiz mode
```bash
python app.py --topic "Biology" --questions 10 --type mixed --interactive
```

### Save quiz to file
```bash
python app.py --topic "Chemistry" --questions 15 --output quiz.json
```

### Adjust difficulty
```bash
python app.py --topic "Calculus" --questions 8 --difficulty hard --type short-answer
```

## Options

| Option | Short | Description |
|--------|-------|-------------|
| `--topic` | `-t` | Quiz topic (required) |
| `--questions` | `-q` | Number of questions (default: 5) |
| `--type` | | Question type: multiple-choice, true-false, short-answer, mixed |
| `--difficulty` | `-d` | Difficulty: easy, medium, hard |
| `--interactive` | `-i` | Take the quiz interactively |
| `--show-answers` | `-a` | Show answers alongside questions |
| `--output` | `-o` | Save quiz to JSON file |

## Example Output

```
╭──────────────────────────────────────╮
│         📝 Quiz Generator            │
╰──────────────────────────────────────╯

Q1 [multiple-choice]
  What year did World War II begin?
    A) 1935
    B) 1939
    C) 1941
    D) 1945
  Answer: B
  Explanation: WWII started in September 1939.
```

## Running Tests

```bash
pytest test_app.py -v
```
