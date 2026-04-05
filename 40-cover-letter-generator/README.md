# Cover Letter Generator

Generate personalized cover letters that match resume highlights to job descriptions using a local Gemma 4 LLM via Ollama.

## Features

- **Resume Matching**: Automatically identifies relevant experience from your resume
- **Job-Specific**: Tailors content to specific job requirements
- **Multiple Tones**: Professional, enthusiastic, confident, or conversational
- **Strong Hooks**: Opens with compelling statements, not generic "I am writing to..."
- **Metrics-Driven**: Highlights achievements with quantifiable results
- **Proper Formatting**: Business letter format under 400 words

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) running locally with the Gemma 4 model

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Prepare Input Files

**resume.txt:**
```
Software Engineer with 5 years experience
- Led team of 8 engineers at TechCorp
- Built ML pipeline processing 1M+ records/day
- Python, AWS, Kubernetes, TensorFlow
- MS Computer Science from Stanford
```

**jd.txt:**
```
Senior Software Engineer at Google
Requirements: Python, ML, cloud platforms
We're looking for someone to lead our AI team...
```

### Run

```bash
# Basic usage
python app.py --resume resume.txt --job-description jd.txt --company "Google"

# With tone and name
python app.py --resume resume.txt --job-description jd.txt --company "Google" --tone enthusiastic --name "Jane Doe"

# Save to file
python app.py --resume resume.txt --job-description jd.txt --company "Meta" -o cover_letter.md
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--resume` | Path to resume file (required) | - |
| `--job-description` | Path to job description file (required) | - |
| `--company` | Company name (required) | - |
| `--tone` | Writing tone | professional |
| `--name` | Applicant name | None |
| `-o, --output` | Save to file | None |

## Example Output

```
╭─ ✉️ Cover Letter ─────────────────────────────╮
│ Dear Google Hiring Team,                       │
│                                                │
│ When I built an ML pipeline that processes     │
│ over 1 million records daily at TechCorp,      │
│ I realized my passion lies in solving          │
│ problems at massive scale — exactly what       │
│ your Senior Engineer role demands.             │
│                                                │
│ With 5 years of experience leading...          │
│                                                │
│ I would welcome the opportunity to discuss     │
│ how my experience aligns with Google's...      │
│                                                │
│ Best regards,                                  │
│ Jane Doe                                       │
╰────────────────────────────────────────────────╯
```

## Testing

```bash
pytest test_app.py -v
```
