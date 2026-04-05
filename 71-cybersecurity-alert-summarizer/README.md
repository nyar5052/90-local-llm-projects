# 🛡️ Cybersecurity Alert Summarizer

AI-powered tool that summarizes security alerts and CVE reports, prioritizes threats, and suggests mitigations using a local LLM.

## Features

- **Alert Summarization**: Condense verbose security alerts into actionable summaries
- **CVE Analysis**: Parse and explain CVE reports with severity assessment
- **Threat Prioritization**: Rank multiple alerts by risk level
- **Mitigation Suggestions**: Get AI-recommended remediation steps
- **Severity Filtering**: Focus on specific severity levels (critical/high/medium/low)

## Usage

```bash
# Summarize an alert file
python app.py --alert alert.txt --severity high

# Inline alert text
python app.py --text "CVE-2024-1234: Remote code execution in OpenSSL 3.0.x"

# Prioritize multiple alerts
python app.py --alert alerts.txt --prioritize

# Filter by severity
python app.py --alert alert.txt --severity critical
```

## Example Output

```
╭──────────────────────────────────────╮
│   🛡️ Cybersecurity Alert Summarizer  │
╰──────────────────────────────────────╯

╭─ Analysis Results ───────────────────╮
│ ## Threat Summary                    │
│ Critical RCE vulnerability affecting │
│ OpenSSL 3.0.x servers.               │
│                                      │
│ ## Severity: CRITICAL (CVSS 9.8)     │
│                                      │
│ ## Recommended Mitigations           │
│ 1. Patch OpenSSL to 3.0.10+         │
│ 2. Enable WAF rules                 │
│ 3. Monitor for exploit attempts     │
╰──────────────────────────────────────╯
```

## Requirements

- Python 3.10+
- Ollama running locally with Gemma 4 model
- Dependencies: `pip install -r requirements.txt`

## Testing

```bash
pytest test_app.py -v
```
