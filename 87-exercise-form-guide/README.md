# 87 - Exercise Form Guide 🏋️

AI-powered exercise form instructions using a local LLM via Ollama.

> ⚠️ **DISCLAIMER**: This tool provides AI-generated exercise guidance for **educational purposes only**. It is **NOT medical advice**. Always consult a qualified fitness professional or physician before starting any exercise program.

## Features

- **Exercise Guides**: Step-by-step form instructions with target muscles, common mistakes, breathing cues, progressions/regressions, and safety tips
- **Exercise Discovery**: List exercises by muscle group with difficulty levels and equipment needs
- **Routine Generation**: Weekly workout routines tailored to your goal and experience level
- **Rich Console Output**: Clean, formatted output with panels and Markdown rendering

## Prerequisites

- Python 3.8+
- [Ollama](https://ollama.ai/) running locally with a model pulled (e.g., `ollama pull llama3`)

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Get Exercise Form Guide

```bash
python app.py guide --exercise "deadlift" --level intermediate
python app.py guide --exercise "bench press" --level beginner
python app.py guide --exercise "pull-up" --level advanced
```

### List Exercises by Muscle Group

```bash
python app.py list --muscle-group legs
python app.py list --muscle-group chest
python app.py list --muscle-group core
```

Available muscle groups: `legs`, `chest`, `back`, `shoulders`, `arms`, `core`, `full body`

### Generate Workout Routine

```bash
python app.py routine --goal strength --level beginner
python app.py routine --goal hypertrophy --level intermediate
python app.py routine --goal flexibility --level advanced
```

Available goals: `strength`, `hypertrophy`, `endurance`, `flexibility`

## Testing

```bash
pytest test_app.py -v
```

## Project Structure

```
87-exercise-form-guide/
├── app.py              # Main CLI application
├── requirements.txt    # Python dependencies
├── test_app.py         # Test suite
└── README.md           # This file
```

## How It Works

1. User selects a command (`guide`, `list`, or `routine`) with relevant options
2. The app constructs a detailed prompt tailored to the request
3. The prompt is sent to a local LLM via Ollama for generation
4. The response is formatted with Rich and displayed in the terminal

## License

Part of the 90 Local LLM Projects collection.
