# 🐳 Docker Compose Generator

AI-powered tool that generates production-ready Docker Compose files from natural language descriptions of your desired stack.

## Features

- **Natural Language Input**: Describe your stack in plain English
- **Common Stack Templates**: MEAN, MERN, LAMP, LEMP, Django, Flask, Rails, and more
- **Environment-Aware**: Development, staging, and production configurations
- **Best Practices**: Health checks, resource limits, named volumes, proper networking
- **Compose Explainer**: Analyze and explain existing docker-compose files

## Usage

```bash
# Generate a compose file from description
python app.py --stack "python flask with postgres and redis" --env production

# Generate development environment
python app.py --stack "react frontend with node api and mongodb" --env development

# List common stacks
python app.py --list-stacks

# Explain existing compose file
python app.py --explain docker-compose.yml

# Save to file
python app.py --stack "wordpress with mysql" --output docker-compose.yml
```

## Example Output

```
╭──────────────────────────────────────╮
│   🐳 Docker Compose Generator       │
╰──────────────────────────────────────╯

╭─ Generated docker-compose.yml ──────╮
│ version: '3.8'                      │
│ services:                           │
│   web:                              │
│     image: python:3.11-slim         │
│     build: .                        │
│     ports:                          │
│       - "5000:5000"                 │
│   db:                               │
│     image: postgres:16              │
│     volumes:                        │
│       - pgdata:/var/lib/postgresql  │
│   redis:                            │
│     image: redis:7-alpine           │
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
