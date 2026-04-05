# ⚙️ Environment Config Manager

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![LLM](https://img.shields.io/badge/LLM-Ollama-orange?logo=ollama)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-red?logo=streamlit)
![Security](https://img.shields.io/badge/Security-Secrets-yellow?logo=keybase)

> **AI-powered .env file management** — validate, compare, migrate, and document environment configurations with security analysis and secret detection.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔍 **Validation** | Security audit of .env files (weak secrets, empty values, defaults) |
| 🔐 **Secret Detection** | Pattern-based detection of API keys, passwords, tokens, SSH keys |
| 🔄 **Multi-Env Comparison** | Side-by-side comparison of environment files |
| 📜 **Migration Scripts** | Auto-generate bash scripts to migrate between environments |
| 📄 **Doc Generation** | AI-generated documentation for all variables |
| 💡 **Variable Suggestions** | AI suggests missing vars based on project type |
| 📝 **Template Generation** | Create .env templates for Flask, Django, Express, etc. |
| 🖥️ **Web UI** | Interactive Streamlit dashboard with upload and comparison views |
| ⌨️ **CLI** | Full-featured command line interface with 7 commands |

---

## 🏗️ Architecture

```
80-env-config-manager/
├── src/env_manager/         # Source package
│   ├── __init__.py          # Package metadata
│   ├── core.py              # Parsing, detection, comparison, migration, LLM
│   ├── cli.py               # Click CLI interface (7 commands)
│   └── web_ui.py            # Streamlit web interface (4 tabs)
├── tests/                   # Test suite
│   ├── test_core.py         # Core logic tests (parsing, secrets, comparison)
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
          ┌─────────────────┼─────────────────┐
          │                 │                 │
    ┌─────┴────┐    ┌──────┴──────┐   ┌──────┴──────┐
    │  Secret   │   │    Env      │   │ Migration   │
    │ Detector  │   │  Comparator │   │  Generator  │
    └──────────┘   └─────────────┘   └─────────────┘
```

---

## 🚀 Installation

```bash
cd 80-env-config-manager
pip install -r requirements.txt
pip install -e ".[dev]"
cp .env.example .env
```

---

## ⌨️ CLI Usage

```bash
# Validate an .env file
python -m src.env_manager.cli validate --file .env

# Suggest missing variables for a Flask project
python -m src.env_manager.cli suggest --file .env --project flask

# Generate .env template
python -m src.env_manager.cli generate --project django --env production

# Compare two environments
python -m src.env_manager.cli compare --file1 .env.dev --file2 .env.prod

# Generate migration script
python -m src.env_manager.cli migrate --from-file .env.dev --to-file .env.prod --output migrate.sh

# Generate environment documentation
python -m src.env_manager.cli docs --file .env --output env-docs.md
```

---

## 🖥️ Web UI (Streamlit)

```bash
streamlit run src/env_manager/web_ui.py
```

The Web UI provides:

- 📁 **Env File Upload** — Upload or paste .env files with parsed variable display
- 🔄 **Comparison View** — Side-by-side environment comparison with migration scripts
- 🔐 **Security Alerts** — Pattern-based secret detection with severity levels
- 📄 **Doc Generator** — AI-generated documentation for environment variables

---

## 🔐 Secret Detection Patterns

| Pattern | Detects |
|---------|---------|
| `api_key` | API_KEY, APIKEY variables |
| `password` | PASSWORD, PASSWD, PASS |
| `secret` | SECRET, PRIVATE |
| `token` | TOKEN, JWT, BEARER |
| `database_url` | DATABASE_URL, DB_URI, CONNECTION_STRING |
| `aws` | AWS_ACCESS, AWS_SECRET |
| `ssh_key` | SSH_KEY, RSA_KEY |
| `encryption` | ENCRYPT, CIPHER, HMAC |

---

## 🧪 Testing

```bash
make test          # Run all tests
make test-cov      # Run with coverage
```

---

## 📄 License

MIT
