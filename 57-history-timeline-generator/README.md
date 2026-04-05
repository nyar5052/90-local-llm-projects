# 📜 History Timeline Generator

Generate historical timelines with key events, figures, and significance using a local LLM (Gemma 4 via Ollama).

## Features

- **Chronological timelines**: Events ordered by date
- **Key figures**: Important people for each event
- **Category tagging**: Political, military, social, economic, cultural, scientific
- **Multiple detail levels**: Brief, medium, detailed
- **Date range filtering**: Focus on specific periods
- **Themes and legacy**: Overarching themes and long-term impact

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) running locally with Gemma 4 model

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Generate a timeline
```bash
python app.py --topic "American Civil War" --detail medium
```

### Brief overview
```bash
python app.py --topic "French Revolution" --detail brief
```

### With date range
```bash
python app.py --topic "Space Race" --start 1957 --end 1972
```

### Save to file
```bash
python app.py --topic "Industrial Revolution" --output timeline.json
```

## Options

| Option | Short | Description |
|--------|-------|-------------|
| `--topic` | `-t` | Historical topic (required) |
| `--detail` | `-d` | brief, medium, detailed (default: medium) |
| `--start` | `-s` | Start year filter |
| `--end` | `-e` | End year filter |
| `--output` | `-o` | Save to JSON file |

## Example Output

```
╭──── 📜 Historical Timeline ────╮
│ American Civil War Timeline     │
│ Period: 1861 - 1865             │
╰─────────────────────────────────╯

┌─────────────────┬──────────────────────┬─────────────┐
│ Date            │ Event                │ Key Figures │
├─────────────────┼──────────────────────┼─────────────┤
│ April 12, 1861  │ Battle of Fort Sumter│ Beauregard  │
│ Jan 1, 1863     │ Emancipation Proc.   │ Lincoln     │
│ April 9, 1865   │ Surrender at Appo.   │ Lee, Grant  │
└─────────────────┴──────────────────────┴─────────────┘
```

## Running Tests

```bash
pytest test_app.py -v
```
