# 💰 Household Budget Analyzer

AI-powered household expense analysis with category breakdowns and savings suggestions using a local Gemma 4 LLM via Ollama.

## Features

- **CSV Import**: Load expenses from standard CSV files
- **Category Breakdown**: Visual breakdown of spending by category
- **AI Analysis**: Intelligent budget analysis with savings suggestions
- **Month Filtering**: Filter and analyze specific months
- **Monthly Comparison**: Compare spending trends across months
- **Budget Recommendations**: Get suggested budget percentages per category

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) running locally with Gemma 4 model
- Start Ollama: `ollama serve`
- Pull model: `ollama pull gemma4`

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Analyze Monthly Expenses
```bash
python app.py --file expenses.csv --month "March 2024"
```

### Full AI Analysis
```bash
python app.py --file expenses.csv --month "March 2024" --analyze
```

### Compare Months
```bash
python app.py --file expenses.csv --compare
```

### Category Breakdown Only
```bash
python app.py --file expenses.csv --breakdown
```

## CSV Format

```csv
date,category,description,amount
2024-03-01,Groceries,Weekly shopping,150.00
2024-03-05,Utilities,Electric bill,95.50
2024-03-10,Entertainment,Movie tickets,35.00
```

## Example Output

```
╭──────── 💰 Household Budget Analyzer ────────╮
│ AI-powered expense analysis                   │
╰───────────────────────────────────────────────╯

┌─────────── 💰 Expense Breakdown ───────────┐
│ Category      │ Amount    │ Percentage      │
├───────────────┼───────────┼─────────────────┤
│ Groceries     │ $225.25   │ 63.3% ████████  │
│ Utilities     │ $95.50    │ 26.8% █████     │
│ Entertainment │ $35.00    │ 9.8%  ██        │
│ TOTAL         │ $355.75   │ 100%            │
└───────────────┴───────────┴─────────────────┘
```

## Testing

```bash
pytest test_app.py -v
```

## License

MIT
