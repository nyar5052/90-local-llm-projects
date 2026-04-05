# 📊 CSV Data Analyzer

Ask natural language questions about your CSV data using a local Gemma 4 LLM.

## Features

- **Natural Language Queries**: Ask questions in plain English about your data
- **Automatic Data Profiling**: Generates statistics, data types, and null analysis
- **Rich Table Preview**: Displays data preview with formatted tables
- **Intelligent Analysis**: LLM-powered insights with specific numbers and trends
- **Flexible Output**: Markdown-formatted analysis results

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) running locally with Gemma 4 model

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Basic usage
python app.py --file sales.csv --query "What month had highest revenue?"

# Without data preview
python app.py --file data.csv --query "Show average values" --no-preview

# Short flags
python app.py -f sales.csv -q "Summarize the trends"
```

## Example Output

```
📊 CSV Data Analyzer
✓ Loaded sales.csv: 12 rows × 4 columns

┌───────┬─────────┬──────────┬────────┐
│ month │ revenue │ expenses │ profit │
├───────┼─────────┼──────────┼────────┤
│ Jan   │ 10000   │ 8000     │ 2000   │
│ Feb   │ 15000   │ 9000     │ 6000   │
│ Mar   │ 12000   │ 7500     │ 4500   │
│ Apr   │ 18000   │ 10000    │ 8000   │
│ May   │ 20000   │ 11000    │ 9000   │
└───────┴─────────┴──────────┴────────┘

Question: What month had highest revenue?

╭── 📈 Analysis Result ──╮
│ Based on the data,      │
│ **May** had the highest │
│ revenue at **$20,000**. │
╰─────────────────────────╯
```

## Testing

```bash
pytest test_app.py -v
```
