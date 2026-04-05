# ✅ Policy Compliance Checker

An AI-powered tool that checks documents against policy rules and produces detailed compliance reports with severity-graded violations, compliant areas, and actionable remediation steps.

## Features

- **Automated Compliance Analysis** — leverages a local LLM (Gemma 4 via Ollama) to audit documents against policy rules.
- **Severity Levels** — violations are graded as **High**, **Medium**, or **Low** with color-coded output.
- **Severity Filtering** — focus on the issues that matter most with `--severity high|medium|low`.
- **Compliance Score** — a 0–100 score with a visual progress bar.
- **Remediation Steps** — each violation includes a concrete fix suggestion.
- **Rich Terminal Output** — tables, colored text, and progress bars via Rich.

## Installation

```bash
# Navigate to the project directory
cd 18-policy-compliance-checker

# Install dependencies
pip install -r requirements.txt

# Ensure Ollama is running with Gemma 4
ollama serve          # in a separate terminal
ollama pull gemma4
```

## Usage

```bash
# Basic compliance check
python app.py --document doc.txt --policy policy.txt

# Show only high-severity violations
python app.py --document doc.txt --policy policy.txt --severity high

# Show only medium-severity violations
python app.py --document doc.txt --policy policy.txt --severity medium
```

### CLI Options

| Option        | Required | Description                                |
|---------------|----------|--------------------------------------------|
| `--document`  | Yes      | Path to the document to check              |
| `--policy`    | Yes      | Path to the policy rules file              |
| `--severity`  | No       | Filter: `all` (default), `high`, `medium`, `low` |

## Example Output

```
📄 Policy Compliance Checker

  Document: doc.txt (1234 chars)
  Policy:   policy.txt (567 chars)

╔══════════════════════════════════╗
║   Policy Compliance Report       ║
╚══════════════════════════════════╝

Compliance Score: 72%
Score ████████████████████████████████████░░░░░░░░░░░░░░  72%

Summary: Document partially complies with the policy.

╭──────────────────────────────────────────────────────────╮
│ ⚠ Violations (2)                                        │
├──────────┬─────────────────┬──────────────┬──────────────┤
│ Severity │ Rule            │ Description  │ Remediation  │
├──────────┼─────────────────┼──────────────┼──────────────┤
│ HIGH     │ Data Retention  │ No retention │ Add clause   │
│ MEDIUM   │ Access Control  │ Missing RBAC │ Define roles │
╰──────────┴─────────────────┴──────────────┴──────────────╯

╭──────────────────────────────────────────────────────────╮
│ ✅ Compliant Areas                                       │
├──────────────────┬───────────────────────────────────────┤
│ Encryption       │ AES-256 encryption is used            │
╰──────────────────┴───────────────────────────────────────╯

📋 Recommendations:
  1. Add data retention policy.
  2. Define RBAC roles.
```

## Running Tests

```bash
pytest test_app.py -v
```

## Project Structure

```
18-policy-compliance-checker/
├── app.py              # Main application
├── requirements.txt    # Python dependencies
├── test_app.py         # Pytest test suite
└── README.md           # This file
```

## How It Works

1. Reads the target document and policy rules from disk.
2. Sends both to a local Gemma 4 LLM via Ollama for analysis.
3. Parses the structured JSON compliance report from the LLM.
4. Renders a rich, color-coded report in the terminal.
