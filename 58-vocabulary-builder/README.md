# 📖 Vocabulary Builder

Generate vocabulary lists and quiz yourself using a local LLM (Gemma 4 via Ollama).

## Features

- **Rich word entries**: Definitions, examples, etymology, synonyms, antonyms
- **Mnemonic devices**: Memory aids for each word
- **Difficulty levels**: Easy, medium, hard
- **Interactive quiz mode**: Test your knowledge
- **JSON export/import**: Save and reload word lists
- **Multiple topics**: SAT, GRE, academic, professional

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) running locally with Gemma 4 model

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Generate vocabulary list
```bash
python app.py learn --topic "SAT words" --count 15
```

### With specific level
```bash
python app.py learn --topic "Medical terminology" --count 20 --level advanced
```

### Quiz mode
```bash
python app.py quiz --file vocab_sat_words.json
```

## Options

### `learn` command
| Option | Short | Description |
|--------|-------|-------------|
| `--topic` | `-t` | Vocabulary topic (required) |
| `--count` | `-c` | Number of words (default: 10) |
| `--level` | `-l` | Target level |
| `--output` | `-o` | Output JSON file |

### `quiz` command
| Option | Short | Description |
|--------|-------|-------------|
| `--file` | `-f` | Path to vocabulary JSON file (required) |

## Example Output

```
╭──── 📖 Vocabulary Builder ────╮
│ SAT Words                      │
│ Level: Advanced | Words: 15    │
╰────────────────────────────────╯

ubiquitous (adjective)
  Present, appearing, or found everywhere.
  Example: "Smartphones have become ubiquitous."
  Etymology: From Latin ubique meaning 'everywhere'
  Synonyms: omnipresent, pervasive
  💡 Mnemonic: U-BIG-uitous: so BIG it's everywhere
```

## Running Tests

```bash
pytest test_app.py -v
```
