# 📄 PDF Chat Assistant

> Ask questions about your PDF documents using a local LLM powered by Gemma 4 via Ollama.

## ✨ Features

- **PDF Text Extraction** — Extracts text from any PDF using PyPDF2
- **Smart Chunking** — Splits documents into overlapping chunks for optimal context
- **Keyword-Based Retrieval** — Finds the most relevant chunks for each question
- **Conversation History** — Maintains context across follow-up questions
- **Rich CLI Output** — Beautiful formatted responses with Markdown rendering
- **Fully Local** — All processing happens on your machine, no data leaves your system

## 📦 Installation

```bash
pip install -r requirements.txt
```

## 🚀 Usage

```bash
python app.py --pdf path/to/document.pdf
```

Then ask questions interactively:

```
❓ Your question: What is the main topic of this document?
╭─ Answer ──────────────────────────────────────╮
│ The document primarily discusses...           │
╰───────────────────────────────────────────────╯

❓ Your question: Summarize section 3
╭─ Answer ──────────────────────────────────────╮
│ Section 3 covers the following key points...  │
╰───────────────────────────────────────────────╯
```

Type `quit` or `exit` to end the session.

## 🧪 Running Tests

```bash
pytest test_app.py -v
```

## 🔧 Requirements

- Python 3.10+
- Ollama running locally with Gemma 4 model
- PDF documents to analyze

## 📁 Project Structure

```
01-pdf-chat-assistant/
├── app.py              # Main application
├── requirements.txt    # Dependencies
├── test_app.py         # Unit tests
└── README.md           # This file
```
