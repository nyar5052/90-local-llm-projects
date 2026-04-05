# 📄 Resume Analyzer

Analyze resumes, get improvement suggestions, and score them against job descriptions — all powered by a local LLM via Ollama.

## Features

- **General Resume Analysis** — Extract skills, experience, education, and achievements; identify strengths and weaknesses; get formatting and content suggestions with an overall quality score.
- **Job Description Scoring** — Score your resume against a specific JD with match percentage, missing skills, keyword gaps, and prioritized improvement recommendations.
- **Rich Terminal Output** — Beautiful panels, tables, and progress bars rendered with Rich.
- **Local & Private** — All processing happens on your machine via Ollama. Your resume never leaves your computer.

## Prerequisites

- [Python 3.10+](https://www.python.org/)
- [Ollama](https://ollama.com/) running locally with the `gemma4` model pulled

```bash
ollama serve
ollama pull gemma4
```

## Installation

```bash
cd 12-resume-analyzer
pip install -r requirements.txt
```

## Usage

### General Resume Analysis

Analyze a resume and get feedback without a specific job in mind:

```bash
python app.py --resume resume.txt
```

### Score Against a Job Description

Compare your resume to a job posting and see how well you match:

```bash
python app.py --resume resume.txt --job-description jd.txt
```

## Example Output

### General Analysis

```
╭──── 📊 Overall Resume Score ────╮
│          72/100                  │
╰─────────────────────────────────╯

🛠️  Extracted Skills
┌───┬──────────────┐
│ # │ Skill        │
├───┼──────────────┤
│ 1 │ Python       │
│ 2 │ Go           │
│ 3 │ Docker       │
│ 4 │ Kubernetes   │
│ 5 │ AWS          │
└───┴──────────────┘

💪 Strengths & Weaknesses
┌─────────────────────┬──────────────────────────┐
│ Strengths ✅        │ Weaknesses ⚠️            │
├─────────────────────┼──────────────────────────┤
│ Strong tech skills  │ No summary section       │
│ Leadership exp.     │ Limited project details   │
└─────────────────────┴──────────────────────────┘
```

### JD Scoring

```
╭──── 🎯 Resume-JD Match Score ────╮
│              78%                  │
╰──────────────────────────────────╯

🛠️  Skills Comparison
┌─────────────┬─────────────┐
│ Matching ✅ │ Missing ❌   │
├─────────────┼─────────────┤
│ Python      │ Redis       │
│ Go          │ Rust        │
│ Docker      │ GCP         │
└─────────────┴─────────────┘
```

## Running Tests

```bash
pytest test_app.py -v
```

## Project Structure

```
12-resume-analyzer/
├── app.py              # Main application
├── requirements.txt    # Python dependencies
├── test_app.py         # Pytest test suite
└── README.md           # This file
```

## License

Part of the [90 Local LLM Projects](../) collection.
