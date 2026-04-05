# 🔬 Medical Literature Summarizer

Automatically summarize medical and scientific research papers using a local LLM. Extracts structured sections including methodology, key findings, statistical results, conclusions, and more.

## Features

- **Structured Extraction** — Pulls out title/authors, abstract, methodology, key findings, statistical results, conclusions, limitations, and future work
- **Adjustable Detail** — Choose between brief, standard, or comprehensive summaries
- **Rich Output** — Color-coded, formatted terminal output with section panels
- **Local LLM** — Powered by Ollama with Gemma 4, keeping your data private
- **CLI Interface** — Simple command-line usage via Click

## Installation

```bash
cd 14-medical-lit-summarizer
pip install -r requirements.txt
```

Ensure [Ollama](https://ollama.ai) is installed and running with the `gemma4` model:

```bash
ollama pull gemma4
ollama serve
```

## Usage

```bash
# Standard summary
python app.py --paper research.txt

# Brief summary
python app.py --paper research.txt --detail brief

# Comprehensive summary
python app.py --paper research.txt --detail comprehensive
```

### Options

| Option     | Description                              | Default    |
|------------|------------------------------------------|------------|
| `--paper`  | Path to the paper text file (required)   | —          |
| `--detail` | Detail level: brief/standard/comprehensive | standard |

## Example Output

```
╭─────────────────────────────────────╮
│ 🔬 Medical Literature Summarizer    │
╰─────────────────────────────────────╯
✓ Ollama is running.

Analyzing paper...

╭──── 📄 Title & Authors ─────────────╮
│ Title: Effects of Aspirin on ...     │
│ Authors: Jane Smith, John Doe, ...   │
╰──────────────────────────────────────╯

╭──── 🔬 Methodology ─────────────────╮
│ Double-blind, placebo-controlled     │
│ randomized trial with 5,000 ...      │
╰──────────────────────────────────────╯

╭──── 🔑 Key Findings ────────────────╮
│ 15% relative risk reduction in       │
│ cardiovascular events (p=0.003) ...  │
╰──────────────────────────────────────╯
```

## Running Tests

```bash
pytest test_app.py -v
```

## Project Structure

```
14-medical-lit-summarizer/
├── app.py              # Main application
├── requirements.txt    # Python dependencies
├── test_app.py         # Test suite
└── README.md           # This file
```

## How It Works

1. Reads the full text of a medical/scientific paper from a file
2. Sends the paper to a local Gemma 4 model via Ollama for each section
3. Extracts structured information using tailored prompts per section
4. Displays a formatted summary with Rich panels in the terminal

## License

Part of the [90 Local LLM Projects](../README.md) collection.
