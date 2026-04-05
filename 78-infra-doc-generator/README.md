# 📐 Infrastructure Doc Generator

AI-powered tool that generates comprehensive infrastructure documentation from Terraform, Docker Compose, Kubernetes, and other configuration files.

## Features

- **Auto-Detection**: Automatically identifies config type (Docker, Terraform, K8s, Ansible)
- **Comprehensive Docs**: Architecture overview, component details, networking, security
- **Architecture Diagrams**: Text-based architecture diagram generation
- **Multiple Formats**: Markdown or plain text output
- **Export Support**: Save documentation to files

## Usage

```bash
# Generate docs from Docker Compose
python app.py --file docker-compose.yml --format markdown

# Generate docs from Terraform
python app.py --file main.tf --format markdown

# Generate architecture diagram
python app.py --file docker-compose.yml --diagram

# Save to file
python app.py --file k8s-deployment.yaml --output infra-docs.md
```

## Example Output

```
╭──────────────────────────────────────╮
│   📐 Infrastructure Doc Generator    │
╰──────────────────────────────────────╯
File: docker-compose.yml
Detected type: Docker Compose

╭─ Infrastructure Documentation ──────╮
│ # Architecture Overview             │
│ Multi-tier web application with      │
│ Nginx reverse proxy and PostgreSQL.  │
│                                     │
│ ## Components                       │
│ | Service | Image | Port | Purpose  │
│ |---------|-------|------|----------|
│ | web     | nginx | 80   | Proxy   │
│ | db      | pg:16 | 5432 | Data    │
│                                     │
│ ## Network Topology                 │
│ web → db (internal network)         │
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
