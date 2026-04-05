# 📋 Incident Report Generator

AI-powered tool that generates professional incident reports from raw security logs, with timeline extraction, impact assessment, and remediation steps.

## Features

- **Full Report Generation**: Executive summary, timeline, impact, root cause, remediation
- **Timeline Extraction**: Chronological event reconstruction from logs
- **Multiple Incident Types**: Security, outage, data-breach, malware, phishing
- **Export Support**: Save reports to file for distribution
- **Professional Format**: Management-ready markdown output

## Usage

```bash
# Generate a security incident report
python app.py --logs incident_logs.txt --type security

# Generate with custom title
python app.py --logs incident_logs.txt --type data-breach --title "Q1 Data Breach"

# Extract timeline only
python app.py --logs incident_logs.txt --timeline-only

# Save report to file
python app.py --logs incident_logs.txt --type malware --output report.md
```

## Example Output

```
╭──────────────────────────────────────╮
│   📋 Incident Report Generator       │
╰──────────────────────────────────────╯

╭─ Incident Report ───────────────────╮
│ # Security Incident Report          │
│ ## Executive Summary                │
│ Unauthorized SSH access detected... │
│                                     │
│ ## Timeline                         │
│ - 10:23 - Initial breach attempt    │
│ - 10:25 - Root access gained        │
│                                     │
│ ## Remediation Steps                │
│ 1. Revoke compromised credentials   │
│ 2. Patch SSH configuration          │
╰─────────────────────────────────────╯
```

## Requirements

- Python 3.10+
- Ollama running locally with Gemma 4 model
- Dependencies: `pip install -r requirements.txt`

## Testing

```bash
pytest test_app.py -v
```
