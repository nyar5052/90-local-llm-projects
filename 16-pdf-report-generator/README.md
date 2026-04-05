# 📊 PDF Report Generator

Generate professional, structured markdown reports from raw CSV data using a local LLM.

## Description

This tool takes a topic and a CSV data file, analyzes the data statistically, and uses a local LLM (via Ollama) to produce a comprehensive report with an executive summary, key findings, detailed analysis, actionable recommendations, and a conclusion.

## Features

- **Automatic Data Analysis** – Detects numeric vs. categorical columns and computes relevant statistics (min, max, mean, median, stdev, unique counts).
- **LLM-Powered Reports** – Generates natural-language reports grounded in your actual data.
- **Markdown Output** – Clean markdown with YAML front-matter, ready for conversion to PDF, HTML, or any other format.
- **Rich CLI** – Colorful terminal output with data preview tables, progress spinners, and a report preview.
- **Flexible Input** – Works with any well-formed CSV file.

## Installation

```bash
cd 16-pdf-report-generator
pip install -r requirements.txt
```

Ensure [Ollama](https://ollama.com/) is installed and running:

```bash
ollama serve
ollama pull gemma4
```

## Usage

```bash
# Basic usage
python app.py --topic "Q4 Sales" --data data.csv

# Specify output file
python app.py --topic "Q4 Sales" --data data.csv --output reports/q4_sales.md

# Help
python app.py --help
```

### CLI Options

| Option     | Required | Default       | Description                  |
|------------|----------|---------------|------------------------------|
| `--topic`  | Yes      | —             | Report topic or title        |
| `--data`   | Yes      | —             | Path to input CSV file       |
| `--output` | No       | `report.md`   | Output markdown file path    |

## Example Output

```
---
title: "Q4 Sales"
generated: "2025-01-15 14:30:00"
generator: "16-pdf-report-generator"
---

# Q4 Sales Report

## Executive Summary
Revenue across all regions totaled $91,500 with an average of $18,300 per region...

## Key Findings
- North region led in units sold (350 total)
- Widget B was the top-performing product ($49,000 combined revenue)
- ...

## Data Analysis
...

## Recommendations
...

## Conclusion
...
```

## Testing

```bash
pytest test_app.py -v
```

## Project Structure

```
16-pdf-report-generator/
├── app.py              # Main application
├── requirements.txt    # Python dependencies
├── test_app.py         # Pytest test suite
└── README.md           # This file
```
