<div align="center">

# 🛒 Product Description Writer

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Powered by Ollama](https://img.shields.io/badge/LLM-Ollama-green.svg)](https://ollama.ai/)

**Generate SEO-optimized, platform-specific e-commerce product descriptions with AI.**

[Features](#-features) • [Installation](#-installation) • [CLI Usage](#-cli-usage) • [Web UI](#-web-ui) • [Architecture](#-architecture)

</div>

---

## 🌟 Features

| Feature | Description |
|---------|-------------|
| 🏪 **Multi-Platform Support** | Amazon, Shopify, Etsy, eBay with platform-specific optimization |
| 🔗 **Feature-Benefit Mapping** | Automatically maps product features to customer benefits |
| 🔍 **SEO Keywords** | Keyword integration with density analysis and scoring |
| 🔀 **A/B Variants** | Generate multiple description variants for testing |
| 📏 **Length Control** | Short (50-100), Medium (150-250), Long (300-500) word options |
| 📊 **SEO Score** | Real-time SEO score with keyword coverage metrics |
| 💻 **Dual Interface** | Full CLI + Streamlit Web UI |
| ⚙️ **YAML Configuration** | Flexible config management |

## 🏗️ Architecture

```
38-product-description-writer/
├── src/
│   └── product_writer/
│       ├── __init__.py          # Package metadata
│       ├── core.py              # Business logic, SEO, platform configs
│       ├── cli.py               # Click CLI with subcommands
│       └── web_ui.py            # Streamlit web interface
├── tests/
│   ├── __init__.py
│   ├── test_core.py             # Core logic tests
│   └── test_cli.py              # CLI tests
├── config.yaml                  # Configuration
├── setup.py                     # Package setup
├── Makefile                     # Build commands
├── .env.example                 # Environment template
├── requirements.txt             # Dependencies
└── README.md                    # Documentation
```

## 📦 Installation

```bash
make install    # or: pip install -e .
make dev        # with dev dependencies
```

## 🖥️ CLI Usage

### Generate Descriptions

```bash
# Basic
product-writer generate --product "Wireless Headphones"

# Full options
product-writer generate \
  --product "Wireless Headphones" \
  --features "noise-cancel,bluetooth,40h battery" \
  --platform amazon \
  --length long \
  --variants 3 \
  --keywords "wireless,headphones,noise canceling" \
  -o output.md
```

### List Platforms

```bash
product-writer platforms
```

### Map Features to Benefits

```bash
product-writer benefits --features "waterproof,bluetooth,portable"
```

## 🌐 Web UI

```bash
make run-web
```

| Tab | Description |
|-----|-------------|
| 📝 **Product Form** | Enter product details, features, keywords |
| 🏪 **Platform Tabs** | Browse platform-specific guidelines |
| 📄 **Generated** | View and download generated descriptions |
| 📊 **SEO Score** | Keyword coverage, density analysis, overall score |

## ⚙️ Configuration

```yaml
llm:
  temperature: 0.7
  max_tokens: 4096
product:
  platforms: [amazon, shopify, etsy, ebay, generic]
  default_variants: 2
seo:
  keyword_count: 10
```

## 🧪 Testing

```bash
make test
```

## 📄 License

Part of the [90 Local LLM Projects](../../README.md) collection.
