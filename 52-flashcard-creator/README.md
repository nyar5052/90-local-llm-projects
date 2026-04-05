# 🗂️ Flashcard Creator

Create and review study flashcards using a local LLM (Gemma 4 via Ollama).

## Features

- **AI-generated flashcards**: Create cards from any topic automatically
- **Multiple difficulty levels**: Easy, medium, hard
- **JSON export**: Save and load flashcard decks
- **Interactive review mode**: Flip cards, rate yourself, track score
- **Shuffle support**: Randomize card order for better learning

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) running locally with Gemma 4 model

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Create flashcards
```bash
python app.py create --topic "Python Data Structures" --count 20
```

### Create with specific difficulty
```bash
python app.py create --topic "Organic Chemistry" --count 15 --difficulty hard
```

### Review flashcards
```bash
python app.py review --file flashcards_python_data_structures.json
```

### Review without shuffling
```bash
python app.py review --file flashcards.json --no-shuffle
```

## Options

### `create` command
| Option | Short | Description |
|--------|-------|-------------|
| `--topic` | `-t` | Topic for flashcards (required) |
| `--count` | `-c` | Number of flashcards (default: 10) |
| `--difficulty` | `-d` | easy, medium, or hard |
| `--output` | `-o` | Output JSON file path |

### `review` command
| Option | Short | Description |
|--------|-------|-------------|
| `--file` | `-f` | Path to flashcards JSON file (required) |
| `--shuffle/--no-shuffle` | | Randomize card order (default: on) |

## Example Output

```
┌───┬──────────────────────────────┬───────────────────────────────────┬────────────┐
│ # │ Front                        │ Back                              │ Difficulty │
├───┼──────────────────────────────┼───────────────────────────────────┼────────────┤
│ 1 │ What is a list in Python?    │ An ordered, mutable collection    │ easy       │
│ 2 │ Tuple vs List?               │ Tuples are immutable              │ medium     │
└───┴──────────────────────────────┴───────────────────────────────────┴────────────┘
```

## Running Tests

```bash
pytest test_app.py -v
```
