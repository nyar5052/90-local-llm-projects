# 🔒 GDPR Compliance Checker

AI-powered tool that analyzes documents, privacy policies, and code for GDPR compliance issues with detailed findings and recommendations.

## Features

- **Full Compliance Analysis**: Check against all GDPR articles
- **Targeted Checks**: Focus on consent, retention, transfers, security, or rights
- **Checklist Generation**: Create actionable compliance checklists
- **Severity Ratings**: Clear COMPLIANT ✅ / NON-COMPLIANT ❌ ratings
- **Recommendations**: Specific remediation guidance per finding

## Usage

```bash
# Full GDPR compliance check
python app.py --file privacy_policy.txt --check all

# Check consent mechanisms only
python app.py --file privacy_policy.txt --check consent

# Check data retention policies
python app.py --file policy.txt --check retention

# Generate compliance checklist
python app.py --file privacy_policy.txt --checklist

# Save results to file
python app.py --file policy.txt --check all --output report.md
```

## Example Output

```
╭──────────────────────────────────────╮
│   🔒 GDPR Compliance Checker        │
╰──────────────────────────────────────╯

╭─ Compliance Report ─────────────────╮
│ ## Findings                         │
│ - Consent: NON-COMPLIANT ❌        │
│   No explicit opt-in mechanism      │
│ - Data Retention: PARTIAL ⚠️        │
│   No defined retention period       │
│ - Subject Rights: COMPLIANT ✅     │
│   Deletion process documented       │
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
