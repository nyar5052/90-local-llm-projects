# 📝 Essay Grader

Grade essays with detailed rubric-based feedback using a local LLM (Gemma 4 via Ollama).

## Features

- **Rubric-based scoring**: Customizable criteria scored on a 1-10 scale
- **Detailed feedback**: Specific comments for each criterion
- **Strength/weakness analysis**: Highlights what works and what needs improvement
- **Actionable suggestions**: Concrete recommendations for improvement
- **JSON export**: Save grading results for records

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) running locally with Gemma 4 model

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Grade an essay with default rubric
```bash
python app.py --essay essay.txt --rubric "clarity,argument,evidence"
```

### Custom rubric criteria
```bash
python app.py --essay paper.txt --rubric "thesis,evidence,analysis,mechanics,originality"
```

### With assignment context
```bash
python app.py --essay essay.txt --rubric "clarity,argument" --context "Compare and contrast essay on WWII"
```

### Save results to file
```bash
python app.py --essay essay.txt --output grade_results.json
```

## Options

| Option | Short | Description |
|--------|-------|-------------|
| `--essay` | `-e` | Path to essay text file (required) |
| `--rubric` | `-r` | Comma-separated criteria (default: clarity,argument,evidence,organization,grammar) |
| `--context` | `-c` | Assignment context or prompt |
| `--output` | `-o` | Save results to JSON file |

## Example Output

```
╭─────── Essay Grade ───────╮
│  Overall Score: 7.5/10 (B+) │
╰───────────────────────────╯

┌────────────┬───────┬─────────────────────────┐
│ Criterion  │ Score │ Feedback                │
├────────────┼───────┼─────────────────────────┤
│ Clarity    │ 8/10  │ Well written throughout  │
│ Argument   │ 7/10  │ Solid thesis statement   │
│ Evidence   │ 7/10  │ Good use of sources      │
└────────────┴───────┴─────────────────────────┘
```

## Running Tests

```bash
pytest test_app.py -v
```
