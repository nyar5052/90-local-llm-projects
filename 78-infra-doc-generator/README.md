# 📐 Infrastructure Doc Generator

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![LLM](https://img.shields.io/badge/LLM-Ollama-orange?logo=ollama)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-red?logo=streamlit)

> **AI-powered infrastructure documentation** — generate comprehensive docs from Terraform, Kubernetes, Docker Compose, Ansible, and CloudFormation configs.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📁 **Multi-Format Input** | Terraform, Kubernetes, Docker Compose, Dockerfile, Ansible, CloudFormation |
| 🔍 **Auto-Detection** | Smart config type detection by filename and content analysis |
| 📐 **Diagram Generation** | Text-based architecture diagrams from any config |
| 🔗 **Dependency Mapping** | Extract and visualize service/resource dependencies |
| 📄 **Multiple Output Formats** | Markdown, HTML, plain text |
| 📤 **Export Support** | Download generated docs and diagrams |
| 🖥️ **Web UI** | Interactive Streamlit dashboard with file upload |
| ⌨️ **CLI** | Full-featured command line interface |

---

## 🏗️ Architecture

```
78-infra-doc-generator/
├── src/infra_doc_gen/       # Source package
│   ├── __init__.py          # Package metadata
│   ├── core.py              # Detection, doc gen, diagram, dependency mapping
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
│   CLI / Web  │────▶│   Core       │────▶│   Ollama     │
│   Interface  │     │   Engine     │     │   LLM API    │
└──────────────┘     └──────┬───────┘     └──────────────┘
                            │
               ┌────────────┼────────────┐
               │            │            │
         ┌─────┴────┐ ┌────┴─────┐ ┌────┴────┐
         │  Config   │ │ Diagram  │ │  Dep    │
         │ Detector  │ │Generator │ │ Mapper  │
         └──────────┘ └──────────┘ └─────────┘
```

---

## 🚀 Installation

```bash
cd 78-infra-doc-generator
pip install -r requirements.txt
pip install -e ".[dev]"
cp .env.example .env
```

---

## ⌨️ CLI Usage

```bash
# Generate docs from Docker Compose
python -m src.infra_doc_gen.cli generate --file docker-compose.yml --format markdown

# Generate docs with architecture diagram
python -m src.infra_doc_gen.cli generate --file main.tf --diagram --output infra-docs.md

# Generate architecture diagram only
python -m src.infra_doc_gen.cli diagram --file k8s-deployment.yaml

# Generate dependency map
python -m src.infra_doc_gen.cli deps --file docker-compose.yml

# List supported formats
python -m src.infra_doc_gen.cli list-formats
```

---

## 🖥️ Web UI (Streamlit)

```bash
streamlit run src/infra_doc_gen/web_ui.py
```

The Web UI provides:

- 📁 **Config Upload** — Drag & drop or paste infrastructure configs
- 📄 **Generated Docs** — Rich markdown documentation with export
- 🔗 **Dependency Tree** — Visual dependency analysis with local + AI detection
- 📐 **Architecture Diagrams** — AI-generated architecture visualizations
- 📋 **Format Reference** — Browse all supported input formats

---

## 🧪 Testing

```bash
make test          # Run all tests
make test-cov      # Run with coverage
```

---

## 📋 Supported Input Formats

| Format | Extensions | Detection |
|--------|-----------|-----------|
| **Terraform** | `.tf`, `.hcl` | `resource`, `provider`, `variable` |
| **Kubernetes** | `.yml`, `.yaml` | `apiVersion`, `kind`, `metadata` |
| **Docker Compose** | `.yml`, `.yaml` | `services`, `image`, `build` |
| **Dockerfile** | `Dockerfile` | `FROM`, `RUN`, `COPY` |
| **Ansible** | `.yml`, `.yaml` | `hosts`, `tasks`, `roles` |
| **CloudFormation** | `.json`, `.yml` | `AWSTemplateFormatVersion`, `Resources` |

---

## 📄 License

MIT
