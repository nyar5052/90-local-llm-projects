# 88 - Sleep Improvement Advisor 😴

AI-powered sleep habit analysis and improvement advisor using a local LLM via Ollama.

> ⚠️ **MEDICAL DISCLAIMER**: This tool provides AI-generated sleep improvement suggestions for **informational purposes only**. It is **NOT medical advice** and does **NOT** diagnose or treat sleep disorders. If you have persistent sleep problems, please consult a qualified healthcare provider.

## Features

- **Sleep Log Analysis**: Parse CSV sleep logs, compute statistics, and get AI-powered pattern analysis
- **Issue-Specific Tips**: Get evidence-based advice for specific sleep problems
- **Interactive Assessment**: Take a guided sleep quality questionnaire with personalized recommendations
- **Rich Console Output**: Tables for sleep data, panels for statistics, and formatted Markdown advice

## Prerequisites

- Python 3.8+
- [Ollama](https://ollama.ai/) running locally with a model pulled (e.g., `ollama pull llama3`)

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Analyze a Sleep Log

Prepare a CSV file with columns: `date`, `bedtime`, `waketime`, `quality_rating`, `notes`

```csv
date,bedtime,waketime,quality_rating,notes
2024-01-01,23:00,07:00,4,Felt rested
2024-01-02,23:30,06:30,3,Woke up once
2024-01-03,00:00,07:30,2,Trouble falling asleep
```

```bash
python app.py analyze --log sleep_log.csv
```

### Get Tips for a Specific Issue

```bash
python app.py tips --issue "difficulty falling asleep"
python app.py tips --issue "waking up too early"
python app.py tips --issue "daytime sleepiness"
```

### Interactive Sleep Assessment

```bash
python app.py assess
```

The assessment asks about your bedtime routine, caffeine intake, screen time, exercise habits, sleep environment, and more.

## Testing

```bash
pytest test_app.py -v
```

## Project Structure

```
88-sleep-improvement-advisor/
├── app.py              # Main CLI application
├── requirements.txt    # Python dependencies
├── test_app.py         # Test suite
└── README.md           # This file
```

## How It Works

1. **Analyze**: Parses your CSV sleep log, computes statistics (average duration, quality trends), and sends a summary to the LLM for pattern analysis
2. **Tips**: Sends your specific sleep issue to the LLM for targeted, evidence-based advice
3. **Assess**: Walks you through a questionnaire, then uses the LLM chat interface for personalized recommendations

## License

Part of the 90 Local LLM Projects collection.
