# 📐 Math Problem Solver

Solve math problems with step-by-step explanations using a local LLM (Gemma 4 via Ollama).

## Features

- **Step-by-step solutions**: Detailed breakdown of each step
- **Multiple categories**: Algebra, calculus, geometry, statistics, trigonometry
- **Concept identification**: Lists mathematical concepts used
- **Practice problems**: Suggests related problems for practice
- **Tips**: Helpful hints for similar problems

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) running locally with Gemma 4 model

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Solve with step-by-step explanation
```bash
python app.py --problem "solve 2x + 5 = 15" --show-steps
```

### Quick answer only
```bash
python app.py --problem "integrate x^2 dx" --no-steps
```

### Specify category
```bash
python app.py --problem "find the area of a circle with radius 5" --category geometry
```

### Save solution
```bash
python app.py --problem "find the derivative of x^3 + 2x" --output solution.json
```

## Options

| Option | Short | Description |
|--------|-------|-------------|
| `--problem` | `-p` | Math problem to solve (required) |
| `--show-steps/--no-steps` | | Show step-by-step solution (default: on) |
| `--category` | `-c` | algebra, calculus, geometry, statistics, arithmetic, trigonometry |
| `--output` | `-o` | Save solution to JSON file |

## Example Output

```
╭──────── 📐 Problem ────────╮
│ Solve 2x + 5 = 15          │
│ Category: algebra           │
╰─────────────────────────────╯

📝 Solution Steps:

Step 1: Subtract 5 from both sides
  ┌──────────────────────┐
  │ 2x + 5 - 5 = 15 - 5 │
  │ 2x = 10              │
  └──────────────────────┘

Step 2: Divide both sides by 2
  ┌──────────────┐
  │ x = 5        │
  └──────────────┘

╭────── ✅ Answer ──────╮
│ x = 5                 │
╰───────────────────────╯
```

## Running Tests

```bash
pytest test_app.py -v
```
