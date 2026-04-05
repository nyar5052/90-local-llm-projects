# 📚 Textbook Chapter Summarizer

AI-powered tool that generates structured, chapter-by-chapter summaries of textbook content using a local LLM via Ollama. Extracts key concepts, definitions, formulas, and generates review questions to help students study more effectively.

## Features

- **Three summary styles** — concise bullets, detailed explanations, or flashcard-style study guides
- **Structured extraction** — automatically identifies key concepts, definitions, formulas, and equations
- **Chapter detection** — recognizes common heading formats (Chapter, Unit, Lesson)
- **Review questions** — generates practice questions from the chapter content
- **Rich terminal output** — beautifully formatted output with panels and Markdown rendering
- **Local & private** — runs entirely on your machine using Ollama

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Ensure Ollama is running with a model available
ollama serve
ollama pull gemma4
```

## Usage

```bash
# Concise summary (default)
python app.py --file chapter.txt

# Detailed summary with full explanations
python app.py --file chapter.txt --style detailed

# Study guide with flashcard-style Q&A
python app.py --file chapter.txt --style study-guide
```

### Options

| Option    | Description                                      | Default    |
|-----------|--------------------------------------------------|------------|
| `--file`  | Path to the textbook chapter text file (required) | —          |
| `--style` | Summary style: `concise`, `detailed`, `study-guide` | `concise` |

## Example Output

```
📚 Textbook Chapter Summarizer

✓ Ollama is running.
✓ Loaded chapter3.txt (256 words)
✓ Detected: Chapter 3: Thermodynamics

╭─ 📚 Chapter 3: Thermodynamics  (Concise Summary) ─╮
╰────────────────────────────────────────────────────╯

## Key Concepts
- First law of thermodynamics (conservation of energy)
- Second law of thermodynamics (entropy always increases)

## Definitions
- **Entropy**: A measure of disorder or randomness in a system.
- **Enthalpy**: The total heat content of a system.

## Formulas & Equations
- ΔU = Q - W (First law of thermodynamics)

## Summary
This chapter introduces the fundamental laws of thermodynamics...

## Review Questions
- What is the first law of thermodynamics?
- Define entropy and explain its significance.
- How does the equation ΔU = Q - W relate to energy conservation?
```

## Summary Styles

### Concise
Short bullet points for each section. Best for quick review before exams.

### Detailed
Full paragraph explanations with examples. Best for deep understanding of material.

### Study Guide
Flashcard-style Q&A format. Best for active recall practice and self-testing.

## Running Tests

```bash
pytest test_app.py -v
```

## Project Structure

```
17-textbook-summarizer/
├── app.py              # Main application
├── requirements.txt    # Python dependencies
├── test_app.py         # Test suite
└── README.md           # This file
```

## How It Works

1. Reads the textbook chapter from a text file
2. Detects the chapter number and title from heading patterns
3. Sends the chapter text to a local LLM with a style-specific prompt
4. The LLM extracts key concepts, definitions, formulas, and generates a summary
5. Results are displayed in a formatted terminal layout using Rich
