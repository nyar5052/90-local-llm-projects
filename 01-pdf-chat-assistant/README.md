# 📄 PDF Chat Assistant

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![LLM](https://img.shields.io/badge/LLM-Gemma%204-orange)
![License](https://img.shields.io/badge/License-MIT-green)
![UI](https://img.shields.io/badge/UI-Streamlit-red?logo=streamlit)

> Ask questions about your PDF documents using a local LLM powered by Gemma 4 via Ollama.

## ✨ Features

- **Multi-PDF Support** — Load and query multiple PDFs simultaneously
- **Smart Chunking** — Splits documents into overlapping chunks for optimal context
- **Keyword-Based Retrieval** — Finds the most relevant chunks for each question
- **Conversation History** — Maintains context across follow-up questions
- **Chat Export** — Export your conversation to Markdown
- **Streamlit Web UI** — Beautiful browser-based interface with file uploader and chat
- **Rich CLI Output** — Formatted terminal responses with Markdown rendering
- **Configurable** — YAML-based settings for model, chunking, and more
- **Fully Local** — All processing happens on your machine, no data leaves your system

## 📦 Installation

```bash
pip install -r requirements.txt
pip install -e .
```

## 🚀 Usage

### CLI

```bash
# Single PDF
python -m pdf_chat.cli --pdf path/to/document.pdf

# Multiple PDFs
python -m pdf_chat.cli --pdf doc1.pdf --pdf doc2.pdf

# With auto-export on exit
python -m pdf_chat.cli --pdf doc.pdf --export
```

### Web UI (Streamlit)

```bash
streamlit run src/pdf_chat/web_ui.py
```

### Interactive Commands

| Command  | Action                        |
|----------|-------------------------------|
| `quit`   | Exit the session              |
| `export` | Save chat history to Markdown |
| `clear`  | Reset conversation history    |

## 🖼️ Screenshots

*Coming soon — screenshots of both CLI and Web UI.*

## 🧪 Running Tests

```bash
pytest tests/ -v
```

## 🔧 Requirements

- Python 3.10+
- Ollama running locally with Gemma 4 model
- PDF documents to analyze

## ⚙️ Configuration

Edit `config.yaml` to customize model, chunking, and export settings.

## 📁 Project Structure

```
01-pdf-chat-assistant/
├── src/
│   └── pdf_chat/
│       ├── __init__.py      # Package metadata
│       ├── core.py          # Core business logic
│       ├── cli.py           # Click CLI interface
│       ├── web_ui.py        # Streamlit web interface
│       ├── config.py        # Configuration management
│       └── utils.py         # Helper utilities
├── tests/
│   ├── __init__.py
│   ├── test_core.py         # Core logic tests
│   └── test_cli.py          # CLI tests
├── config.yaml              # Default configuration
├── setup.py                 # Package setup
├── requirements.txt         # Dependencies
├── Makefile                 # Common commands
├── .env.example             # Example environment variables
└── README.md                # This file
```
