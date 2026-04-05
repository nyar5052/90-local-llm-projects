# 🐳 Docker Compose Generator

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![LLM](https://img.shields.io/badge/LLM-Ollama-orange?logo=ollama)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-red?logo=streamlit)
![Docker](https://img.shields.io/badge/Docker-Compose-blue?logo=docker)

> **AI-powered Docker Compose file generation** — from natural language descriptions to production-ready YAML in seconds.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🗣️ **Natural Language Input** | Describe your stack in plain English |
| 📦 **Service Catalog** | 20+ pre-configured services (databases, web servers, messaging, monitoring) |
| 🌍 **Multi-Environment** | Development, staging, and production profiles with tailored configs |
| 🔗 **Network Config** | Simple, isolated, and overlay network templates |
| 💾 **Volume Management** | Named volumes with proper mount points |
| 📋 **Common Stacks** | MEAN, MERN, LAMP, LEMP, Django, Flask, Rails, WordPress, ELK |
| ✅ **YAML Validation** | Auto-validate generated compose files |
| 📖 **Compose Explainer** | Upload & explain existing docker-compose files |
| 🖥️ **Web UI** | Interactive Streamlit dashboard with stack builder |
| ⌨️ **CLI** | Full-featured Click-based command line interface |

---

## 🏗️ Architecture

```
76-docker-compose-generator/
├── src/docker_gen/          # Source package
│   ├── __init__.py          # Package metadata
│   ├── core.py              # Business logic, service catalog, LLM integration
│   ├── cli.py               # Click CLI interface
│   └── web_ui.py            # Streamlit web interface
├── tests/                   # Test suite
│   ├── test_core.py         # Core logic tests
│   └── test_cli.py          # CLI integration tests
├── config.yaml              # Application configuration
├── setup.py                 # Package setup
├── Makefile                 # Development commands
├── .env.example             # Environment template
├── requirements.txt         # Dependencies
└── README.md
```

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   CLI / Web  │────▶│     Core     │────▶│   Ollama     │
│   Interface  │     │   Engine     │     │   LLM API    │
└──────────────┘     └──────┬───────┘     └──────────────┘
                            │
                    ┌───────┴───────┐
                    │               │
              ┌─────┴─────┐  ┌─────┴─────┐
              │  Service   │  │   Env     │
              │  Catalog   │  │  Profiles │
              └───────────┘  └───────────┘
```

---

## 🚀 Installation

```bash
# Clone and navigate
cd 76-docker-compose-generator

# Install dependencies
pip install -r requirements.txt

# Or install as a package
pip install -e ".[dev]"

# Copy environment config
cp .env.example .env
```

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai) running locally with a model pulled
- Dependencies listed in `requirements.txt`

---

## ⌨️ CLI Usage

```bash
# Generate compose file from natural language
python -m src.docker_gen.cli generate --stack "flask with postgres and redis" --env production

# Use specific catalog services
python -m src.docker_gen.cli generate --stack "web app" --services "nginx,postgres,redis" --env staging

# Generate with network mode
python -m src.docker_gen.cli generate --stack "microservices" --network isolated --output docker-compose.yml

# Explain an existing compose file
python -m src.docker_gen.cli explain --file docker-compose.yml

# Browse available resources
python -m src.docker_gen.cli list-stacks
python -m src.docker_gen.cli list-services
python -m src.docker_gen.cli list-envs
```

---

## 🖥️ Web UI (Streamlit)

```bash
streamlit run src/docker_gen/web_ui.py
```

The Web UI provides:

- 🏗️ **Stack Builder** — Natural language, quick stack, or service picker modes
- 🃏 **Service Cards** — Browse and select from the service catalog
- 📄 **Generated YAML** — Syntax-highlighted output with download button
- 🌍 **Environment Tabs** — Switch between dev/staging/prod profiles
- 📖 **Compose Explainer** — Upload and analyze existing compose files
- 📦 **Service Catalog** — Visual catalog with metrics cards

---

## 🧪 Testing

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test
python -m pytest tests/test_core.py -v
```

---

## ⚙️ Configuration

Edit `config.yaml` to customize:

```yaml
llm:
  model: "gemma3"
  temperature: 0.3
  max_tokens: 3000

defaults:
  environment: "development"
  network_mode: "simple"
```

---

## 📦 Service Catalog

| Category | Services |
|----------|----------|
| **Databases** | PostgreSQL, MySQL, MongoDB, Redis, MariaDB |
| **Web Servers** | Nginx, Traefik, Caddy, Apache |
| **Messaging** | RabbitMQ, Kafka, NATS |
| **Monitoring** | Prometheus, Grafana, Elasticsearch, Kibana |
| **Runtimes** | Python, Node.js, Go, Java |

---

## 📄 License

MIT
