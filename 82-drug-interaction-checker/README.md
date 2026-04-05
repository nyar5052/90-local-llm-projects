# 82 - Drug Interaction Checker

> **⚠️ IMPORTANT DISCLAIMER:** This project is for **EDUCATIONAL and INFORMATIONAL purposes ONLY**. It is **NOT** a substitute for professional medical or pharmacological advice. Always consult a qualified healthcare provider or pharmacist before making any decisions about your medications. Never start, stop, or change medications based on this tool's output.

## Description

An AI-powered drug interaction checker that uses a local LLM (via Ollama) to analyse potential interactions between medications. The tool provides educational information about interaction severity, mechanisms, and general recommendations while always emphasising the importance of consulting a healthcare professional.

## Features

- **Single-Query Mode** — check interactions for a list of medications via command-line flag
- **Interactive Mode** — repeatedly check different medication combinations in a session
- **Prominent Disclaimers** — medical disclaimer displayed at every startup and in every response
- **Rich Console Output** — tables for medication lists, panels for interaction analysis
- **Severity Classification** — interactions categorised as Major, Moderate, or Minor
- **Error Handling** — graceful handling of Ollama connection issues

## Installation

```bash
cd 82-drug-interaction-checker
pip install -r requirements.txt
```

Make sure [Ollama](https://ollama.ai) is installed and running.

## Usage

### Check Medications

```bash
python app.py check --medications "aspirin,ibuprofen,lisinopril"
```

### Interactive Mode

```bash
python app.py interactive
```

You will see the medical disclaimer, then a prompt where you can enter comma-separated medication names. Type `quit` or `exit` to end.

### Example Output

```
╭─────────── IMPORTANT MEDICAL DISCLAIMER ───────────╮
│                                                     │
│  ⚠️  IMPORTANT MEDICAL DISCLAIMER ⚠️               │
│  This drug interaction checker is for EDUCATIONAL   │
│  and INFORMATIONAL purposes ONLY.                   │
│  ...                                                │
╰─────────────────────────────────────────────────────╯

Checking interactions for 3 medications...

┌───────────────────────────┐
│   Medications Checked     │
├────┬──────────────────────┤
│  # │ Medication           │
├────┼──────────────────────┤
│  1 │ aspirin              │
│  2 │ ibuprofen            │
│  3 │ lisinopril           │
└────┴──────────────────────┘

╭──────────── Interaction Analysis ────────────╮
│                                              │
│  **Disclaimer:** I am not a pharmacist...    │
│                                              │
│  **1. Aspirin + Ibuprofen (Major)**          │
│  Both are NSAIDs; concurrent use increases   │
│  risk of gastrointestinal bleeding...        │
│  ...                                         │
╰──────────────────────────────────────────────╯
```

## Running Tests

```bash
pytest test_app.py -v
```

## Tech Stack

- **Python 3.10+**
- **Ollama** — local LLM inference
- **Click** — CLI framework
- **Rich** — terminal formatting, tables, and panels
- **Pytest** — testing with mocked LLM calls
