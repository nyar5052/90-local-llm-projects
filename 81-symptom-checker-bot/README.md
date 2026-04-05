# 81 - Symptom Checker Bot

> **⚠️ IMPORTANT DISCLAIMER:** This project is for **EDUCATIONAL and INFORMATIONAL purposes ONLY**. It is **NOT** a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of a qualified healthcare provider with any questions you may have regarding a medical condition. If you think you may have a medical emergency, call your doctor or emergency services immediately.

## Description

An AI-powered symptom checker bot that uses a local LLM (via Ollama) to provide general educational information about symptoms and commonly associated conditions. The bot operates through a rich command-line interface and always prominently displays medical disclaimers.

## Features

- **Interactive Chat Mode** — multi-turn conversation to describe and refine symptoms
- **Single-Query Mode** — quick symptom lookup via command-line flag
- **Prominent Disclaimers** — medical disclaimer displayed at every startup and in every response
- **Rich Console Output** — panels, markdown rendering, and colour-coded output
- **Conversation History** — context-aware follow-up questions in chat mode
- **Error Handling** — graceful handling of Ollama connection issues

## Installation

```bash
cd 81-symptom-checker-bot
pip install -r requirements.txt
```

Make sure [Ollama](https://ollama.ai) is installed and running.

## Usage

### Interactive Chat

```bash
python app.py chat
```

You will see the medical disclaimer, then an interactive prompt where you can describe your symptoms. Type `quit` or `exit` to end the session.

### Single Symptom Check

```bash
python app.py check --symptoms "headache, fever, sore throat"
```

### Example Output

```
╭─────────── IMPORTANT MEDICAL DISCLAIMER ───────────╮
│                                                     │
│  ⚠️  MEDICAL DISCLAIMER ⚠️                         │
│                                                     │
│  This symptom checker is for EDUCATIONAL and        │
│  INFORMATIONAL purposes ONLY.                       │
│  ...                                                │
╰─────────────────────────────────────────────────────╯

Analyzing symptoms: headache, fever, sore throat

╭──────────── Symptom Information ────────────╮
│                                             │
│  **Disclaimer:** I am not a doctor...       │
│  Based on common medical literature, these  │
│  symptoms may be associated with:           │
│  - Common cold / flu                        │
│  - Strep throat                             │
│  ...                                        │
│  Please consult a healthcare professional.  │
╰─────────────────────────────────────────────╯
```

## Running Tests

```bash
pytest test_app.py -v
```

## Tech Stack

- **Python 3.10+**
- **Ollama** — local LLM inference
- **Click** — CLI framework
- **Rich** — terminal formatting and panels
- **Pytest** — testing with mocked LLM calls
