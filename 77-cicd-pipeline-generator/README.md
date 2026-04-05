# 🚀 CI/CD Pipeline Generator

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![LLM](https://img.shields.io/badge/LLM-Ollama-orange?logo=ollama)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-red?logo=streamlit)

> **AI-powered CI/CD pipeline generation** — production-ready configs for GitHub Actions, GitLab CI, Jenkins, Azure Pipelines, and CircleCI.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔧 **Multi-Platform** | GitHub Actions, GitLab CI, Jenkins, Azure Pipelines, CircleCI |
| 💻 **Language Support** | Python, JavaScript, TypeScript, Java, Go, Rust, Ruby, C#, PHP, Kotlin, Swift |
| 📋 **Stage Builder** | 9 pipeline stages: lint, test, security, build, publish, deploy, notify |
| 🔢 **Matrix Builds** | Auto-configured matrix testing across versions and OS |
| 🔐 **Secret Management** | Platform-specific secret templates (Docker, AWS, NPM, PyPI, Slack) |
| 📖 **Pipeline Explainer** | Upload & explain existing pipeline configs |
| ✅ **Config Validation** | Auto-validate generated YAML/Groovy |
| 🖥️ **Web UI** | Interactive Streamlit dashboard with visual pipeline builder |
| ⌨️ **CLI** | Full-featured Click-based command line interface |

---

## 🏗️ Architecture

```
77-cicd-pipeline-generator/
├── src/cicd_gen/            # Source package
│   ├── __init__.py          # Package metadata
│   ├── core.py              # Business logic, platform registry, LLM integration
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
               ┌────────────┼────────────┐
               │            │            │
         ┌─────┴────┐ ┌────┴─────┐ ┌────┴────┐
         │ Platform  │ │  Stage   │ │ Secret  │
         │ Registry  │ │ Catalog  │ │Templates│
         └──────────┘ └──────────┘ └─────────┘
```

---

## 🚀 Installation

```bash
cd 77-cicd-pipeline-generator
pip install -r requirements.txt

# Or install as a package
pip install -e ".[dev]"
cp .env.example .env
```

---

## ⌨️ CLI Usage

```bash
# Generate GitHub Actions pipeline
python -m src.cicd_gen.cli generate --platform github-actions --language python --steps "lint,test,build,deploy"

# Generate GitLab CI with matrix builds
python -m src.cicd_gen.cli generate --platform gitlab-ci --language javascript --steps "lint,test,build" --matrix

# Generate Jenkins pipeline with secrets
python -m src.cicd_gen.cli generate --platform jenkins --language java --secrets "docker,aws" --output Jenkinsfile

# Explain existing pipeline
python -m src.cicd_gen.cli explain --file .github/workflows/ci.yml --platform github-actions

# Browse resources
python -m src.cicd_gen.cli list-platforms
python -m src.cicd_gen.cli list-stages
python -m src.cicd_gen.cli list-matrix
```

---

## 🖥️ Web UI (Streamlit)

```bash
streamlit run src/cicd_gen/web_ui.py
```

The Web UI provides:

- 🔧 **Platform Selector** — Choose target CI/CD platform with config path hints
- 📋 **Stage Builder** — Visual checkbox grid for pipeline stages
- 🔢 **Matrix Config** — Auto-populated version matrices per language
- 🔐 **Secret Management** — Platform-specific secret category selection
- 📄 **Generated Config** — Syntax-highlighted output with download
- 🔀 **Pipeline Visualization** — Visual pipeline flow diagram
- 📖 **Pipeline Explainer** — Upload and analyze existing configs

---

## 🧪 Testing

```bash
make test          # Run all tests
make test-cov      # Run with coverage
```

---

## 🔧 Supported Platforms

| Platform | Config Path | Language |
|----------|-------------|----------|
| **GitHub Actions** | `.github/workflows/ci.yml` | YAML |
| **GitLab CI** | `.gitlab-ci.yml` | YAML |
| **Jenkins** | `Jenkinsfile` | Groovy |
| **Azure Pipelines** | `azure-pipelines.yml` | YAML |
| **CircleCI** | `.circleci/config.yml` | YAML |

---

## 📄 License

MIT
