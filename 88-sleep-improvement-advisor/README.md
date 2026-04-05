# 😴 Sleep Improvement Advisor

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)
![Ollama](https://img.shields.io/badge/LLM-Ollama-orange)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-red?logo=streamlit)

AI-powered sleep habit analysis and improvement advisor using a local LLM via Ollama.

---

> ## ⚠️ MEDICAL DISCLAIMER
>
> **This tool provides AI-generated sleep improvement suggestions for INFORMATIONAL PURPOSES ONLY.**
>
> - It is **NOT medical advice** and does **NOT** diagnose or treat sleep disorders.
> - It is **NOT** a substitute for professional medical evaluation.
> - If you have persistent sleep problems, **please consult a qualified healthcare provider** who can rule out conditions like sleep apnea, insomnia, or restless leg syndrome.
>
> **Always seek the advice of a physician or other qualified health provider with any questions you may have regarding a medical condition.**

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 😴 **Sleep Log Analysis** | Parse CSV sleep logs, compute statistics, and get AI-powered pattern analysis |
| 🏆 **Sleep Scoring** | Get a 0-100 sleep score with grade (A-F) and detailed breakdown |
| 🏠 **Environment Optimization** | Interactive checklist for optimizing your sleep environment |
| 🌙 **Routine Builder** | Generate a personalized bedtime routine based on your wake time |
| 📊 **Pattern Analysis** | Analyze day-of-week patterns, weekday vs weekend, and trends |
| 💡 **AI-Powered Tips** | Get evidence-based advice for specific sleep issues |
| 🛏️ **Interactive Assessment** | Take a guided sleep quality questionnaire |

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│                   User Interface                 │
│  ┌──────────────────┐  ┌──────────────────────┐ │
│  │   CLI (Click)     │  │  Web UI (Streamlit)  │ │
│  │  sleep_advisor/   │  │  sleep_advisor/      │ │
│  │  cli.py           │  │  web_ui.py           │ │
│  └────────┬─────────┘  └──────────┬───────────┘ │
│           │                       │              │
│  ┌────────▼───────────────────────▼───────────┐  │
│  │           Core Logic (core.py)             │  │
│  │  parse_sleep_log() │ compute_sleep_stats() │  │
│  │  calculate_sleep_score() │ build_routine() │  │
│  │  analyze_weekly_patterns() │ checklist     │  │
│  └────────────────────┬──────────────────────┘  │
│                       │                          │
│  ┌────────────────────▼──────────────────────┐  │
│  │         LLM Client (common/)              │  │
│  │     Ollama API via llm_client.py          │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

## 📋 Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) running locally with a model pulled (e.g., `ollama pull llama3`)

## 🚀 Installation

```bash
# Install with pip (editable mode with dev dependencies)
pip install -e ".[dev]"

# Or install requirements only
pip install -r requirements.txt
```

## 💻 CLI Usage

### Analyze a Sleep Log

Prepare a CSV file with columns: `date`, `bedtime`, `waketime`, `quality_rating`, `notes`

```csv
date,bedtime,waketime,quality_rating,notes
2024-01-01,23:00,07:00,4,Felt rested
2024-01-02,23:30,06:30,3,Woke up once
2024-01-03,00:00,07:30,2,Trouble falling asleep
```

```bash
sleep-advisor analyze --log sleep_log.csv
```

### Get Tips for a Specific Issue

```bash
sleep-advisor tips --issue "difficulty falling asleep"
sleep-advisor tips --issue "waking up too early"
sleep-advisor tips --issue "daytime sleepiness"
```

### Interactive Sleep Assessment

```bash
sleep-advisor assess
```

### 🏆 Calculate Sleep Score

```bash
sleep-advisor score --log sleep_log.csv
```

### 🏠 Environment Checklist

```bash
sleep-advisor checklist
```

### 🌙 Build Bedtime Routine

```bash
sleep-advisor routine --wake-time 07:00
sleep-advisor routine --wake-time 06:30 --duration 7.0
```

### 📊 Analyze Weekly Patterns

```bash
sleep-advisor patterns --log sleep_log.csv
```

## 🌐 Web UI

Launch the Streamlit web interface:

```bash
streamlit run src/sleep_advisor/web_ui.py
```

The web UI provides:
- **Sleep Log**: Upload and visualize CSV data with statistics
- **Sleep Score**: Visual score with grade and breakdown meters
- **Environment Checklist**: Interactive checklist with priority indicators
- **Routine Builder**: Time picker and slider to generate a routine
- **Pattern Analysis**: Bar charts, line charts, and trend detection

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v --tb=short

# With coverage
python -m pytest tests/ -v --cov=sleep_advisor --cov-report=term-missing
```

## 📁 Project Structure

```
88-sleep-improvement-advisor/
├── app.py                          # Legacy CLI entry point
├── src/
│   ├── __init__.py
│   └── sleep_advisor/
│       ├── __init__.py             # Package metadata
│       ├── core.py                 # Core logic, data models, scoring
│       ├── cli.py                  # Click CLI interface
│       └── web_ui.py              # Streamlit web interface
├── tests/
│   ├── __init__.py
│   ├── test_core.py               # Core logic tests
│   └── test_cli.py                # CLI command tests
├── config.yaml                     # Application configuration
├── setup.py                       # Package setup
├── requirements.txt               # Python dependencies
├── Makefile                       # Common tasks
├── .env.example                   # Environment variables template
├── test_app.py                    # Legacy tests
└── README.md                      # This file
```

## ⚙️ Configuration

See `config.yaml` for configurable settings:
- LLM model selection and parameters
- Optimal sleep duration range
- Logging configuration

Copy `.env.example` to `.env` and customize:
```bash
cp .env.example .env
```

## 🔬 How It Works

1. **Analyze**: Parses your CSV sleep log, computes statistics (average duration, quality trends), and sends a summary to the LLM for pattern analysis
2. **Score**: Evaluates your sleep data across 4 dimensions — duration, quality, consistency, and wake frequency — producing a 0-100 score
3. **Tips**: Sends your specific sleep issue to the LLM for targeted, evidence-based advice
4. **Assess**: Walks you through a questionnaire, then uses the LLM chat interface for personalized recommendations
5. **Checklist**: Provides a curated environment optimization checklist covering light, sound, temperature, bedding, air, and electronics
6. **Routine**: Calculates an ideal bedtime and generates a step-by-step wind-down routine
7. **Patterns**: Analyzes day-of-week averages, weekday vs weekend differences, and quality trends

---

> ## ⚠️ Reminder: Medical Disclaimer
>
> This tool is for **educational and informational purposes only**. It does **NOT** provide medical advice, diagnosis, or treatment. Always consult with a qualified healthcare professional before making changes to your sleep habits, especially if you suspect a sleep disorder.

---

## License

Part of the 90 Local LLM Projects collection.
