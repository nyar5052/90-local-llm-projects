# 📚 Reading Comprehension Builder

Create reading comprehension exercises from any topic using a local LLM (Gemma 4 via Ollama).

## Features

- **AI-generated passages**: Custom reading passages on any topic
- **Multiple question types**: Factual, inferential, analytical, vocabulary, main-idea
- **Adjustable difficulty**: Elementary through college level
- **Interactive mode**: Answer questions and get scored
- **Vocabulary support**: Key terms with definitions
- **JSON export**: Save exercises for classroom use

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) running locally with Gemma 4 model

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Create an exercise
```bash
python app.py --topic "Climate Change" --level "high school" --questions 5
```

### Interactive mode
```bash
python app.py --topic "Space Exploration" --questions 8 --interactive
```

### Show answers
```bash
python app.py --topic "Ancient Egypt" --level "middle school" --show-answers
```

### Adjust passage length
```bash
python app.py --topic "Robotics" --length long --questions 10
```

### Save to file
```bash
python app.py --topic "Marine Biology" --output exercise.json
```

## Options

| Option | Short | Description |
|--------|-------|-------------|
| `--topic` | `-t` | Topic for the passage (required) |
| `--level` | `-l` | Reading level (default: high school) |
| `--questions` | `-q` | Number of questions (default: 5) |
| `--length` | | Passage length: short, medium, long |
| `--interactive` | `-i` | Answer questions interactively |
| `--show-answers` | `-a` | Show answers immediately |
| `--output` | `-o` | Save to JSON file |

## Example Output

```
╭──── 📚 Reading Comprehension ────╮
│ Understanding Climate Change      │
│ Level: high school | Words: ~350  │
╰──────────────────────────────────╯

╭──────────── 📖 Passage ──────────╮
│ Climate change refers to long-   │
│ term shifts in temperatures...   │
╰──────────────────────────────────╯

Q1 [factual] (easy)
  What has been the main driver of climate change?
    A) Solar variations
    B) Human activities
    C) Volcanic eruptions
    D) Ocean currents
```

## Running Tests

```bash
pytest test_app.py -v
```
