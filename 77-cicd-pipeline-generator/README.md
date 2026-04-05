# 🚀 CI/CD Pipeline Generator

AI-powered tool that generates production-ready CI/CD pipeline configurations for GitHub Actions, GitLab CI, Azure Pipelines, Jenkins, and CircleCI.

## Features

- **Multi-Platform**: GitHub Actions, GitLab CI, Azure Pipelines, Jenkins, CircleCI
- **Language Support**: Python, JavaScript, TypeScript, Java, Go, Rust, Ruby, and more
- **Best Practices**: Caching, parallel jobs, matrix builds, artifact handling
- **Pipeline Explainer**: Analyze and explain existing pipeline configs
- **Customizable Steps**: lint, test, build, deploy, and custom steps

## Usage

```bash
# Generate GitHub Actions pipeline
python app.py --platform github-actions --language python --steps "lint,test,build,deploy"

# Generate GitLab CI pipeline
python app.py --platform gitlab-ci --language javascript --steps "lint,test,build"

# Explain existing pipeline
python app.py --explain .github/workflows/ci.yml --platform github-actions

# List supported platforms
python app.py --list-platforms

# Save to file
python app.py --platform github-actions --language go --output ci.yml
```

## Example Output

```
╭──────────────────────────────────────╮
│   🚀 CI/CD Pipeline Generator       │
╰──────────────────────────────────────╯

╭─ Generated GitHub Actions Pipeline ─╮
│ name: CI                            │
│ on:                                 │
│   push:                             │
│     branches: [main]                │
│ jobs:                               │
│   lint:                             │
│     runs-on: ubuntu-latest          │
│     steps:                          │
│       - uses: actions/checkout@v4   │
│       - run: pip install flake8     │
│       - run: flake8 .               │
│   test:                             │
│     runs-on: ubuntu-latest          │
│     needs: lint                     │
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
