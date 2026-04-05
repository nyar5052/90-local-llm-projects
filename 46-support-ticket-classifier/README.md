# 🎫 Support Ticket Classifier

Classify support tickets by category and priority, with suggested responses, using a local Gemma 4 LLM.

## Features

- **Auto-Classification**: Categorizes tickets into custom categories
- **Priority Assignment**: Assigns low/medium/high/critical priority levels
- **Response Suggestions**: Generates initial customer-facing responses
- **Confidence Scoring**: Each classification includes a confidence score
- **Summary Dashboard**: Overview of ticket distribution by category and priority

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) running locally with Gemma 4 model

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Classify tickets
python app.py --file tickets.csv --categories "billing,technical,account"

# Specify text column
python app.py -f tickets.csv -c "billing,tech,general" -col "description"
```

## Input Format

CSV file with ticket data (auto-detects description column):

```csv
id,subject,description,customer
1,Login issue,Cannot access my account,john@test.com
2,Billing error,Charged twice this month,jane@test.com
```

## Example Output

```
🎫 Support Ticket Classifier
✓ Loaded 50 tickets from tickets.csv
Categories: billing, technical, account

┌───┬────────────────────┬───────────┬──────────┬────────────┬──────────────────────┐
│ # │ Ticket             │ Category  │ Priority │ Confidence │ Suggested Response   │
├───┼────────────────────┼───────────┼──────────┼────────────┼──────────────────────┤
│ 1 │ Cannot access...   │ technical │ 🟠 High  │ 92%        │ We're investigating  │
│ 2 │ Charged twice...   │ billing   │ 🔴 Crit  │ 95%        │ Reviewing charge...  │
│ 3 │ Add dark mode...   │ technical │ 🟢 Low   │ 88%        │ Feature request...   │
└───┴────────────────────┴───────────┴──────────┴────────────┴──────────────────────┘

📊 Classification Summary
  Total Tickets: 50
  billing: 18  |  technical: 22  |  account: 10
  🟢 Low: 10  |  🟡 Medium: 20  |  🟠 High: 15  |  🔴 Critical: 5
```

## Testing

```bash
pytest test_app.py -v
```
