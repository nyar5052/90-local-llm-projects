# 📊 Log File Analyzer

AI-powered log file analyzer that detects error patterns, clusters related issues, and suggests root causes using a local LLM.

## Features

- **Error Pattern Detection**: Identify recurring error patterns automatically
- **Error Clustering**: Group similar errors for batch resolution
- **Root Cause Analysis**: AI-suggested root causes for detected issues
- **Focus Areas**: Errors, warnings, security, performance, or all
- **Tail Support**: Analyze only the last N lines of large log files

## Usage

```bash
# Analyze errors in a log file
python app.py --file server.log --focus errors

# Analyze last 1000 lines only
python app.py --file server.log --focus errors --last 1000

# Cluster similar errors
python app.py --file server.log --cluster

# Focus on security events
python app.py --file auth.log --focus security

# Add system context
python app.py --file server.log --focus performance --context "Django app on AWS"

# Save results
python app.py --file server.log --focus all --output report.md
```

## Example Output

```
╭──────────────────────────────────────╮
│   📊 Log File Analyzer              │
╰──────────────────────────────────────╯
Analyzing: server.log
Lines: 1523
Focus: errors

╭─ Log Analysis ──────────────────────╮
│ ## Summary                          │
│ 3 error patterns detected           │
│                                     │
│ ## Error Patterns                   │
│ 1. Database timeouts (45 instances) │
│ 2. HTTP 500 errors (12 instances)   │
│ 3. Memory warnings (8 instances)    │
│                                     │
│ ## Root Cause                       │
│ Connection pool exhaustion likely   │
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
