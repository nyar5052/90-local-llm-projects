# 🔬 Science Experiment Explainer

Explain science experiments step-by-step using a local LLM (Gemma 4 via Ollama).

## Features

- **Complete experiment guides**: Materials, procedure, safety, results
- **Grade-level appropriate**: Elementary through college
- **Safety first**: Highlighted safety precautions
- **Scientific explanations**: Why the experiment works
- **Discussion questions**: For classroom use
- **Variations**: Alternative approaches to try

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) running locally with Gemma 4 model

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Explain an experiment
```bash
python app.py --experiment "baking soda volcano" --level "middle school"
```

### With detailed explanation
```bash
python app.py --experiment "electrolysis of water" --level "high school" --detail detailed
```

### Save to file
```bash
python app.py --experiment "plant growth" --output experiment.json
```

## Options

| Option | Short | Description |
|--------|-------|-------------|
| `--experiment` | `-e` | Experiment name (required) |
| `--level` | `-l` | Grade level (default: middle school) |
| `--detail` | `-d` | brief, medium, detailed |
| `--output` | `-o` | Save to JSON file |

## Example Output

```
╭───── 🔬 Science Experiment ─────╮
│ Baking Soda Volcano              │
│ Subject: Chemistry               │
│ Level: middle school             │
╰──────────────────────────────────╯

🛡️ Safety Precautions:
  ⚠️  Wear safety goggles
  ⚠️  Adult supervision recommended

📋 Procedure:
  Step 1: Build the volcano shape
  Step 2: Add baking soda
  Step 3: Pour vinegar slowly
```

## Running Tests

```bash
pytest test_app.py -v
```
