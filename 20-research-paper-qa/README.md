# 🔍 Research Paper Q&A

Interactive question answering over research papers using a local LLM. Upload any research paper and engage in a contextual conversation about its content.

## Features

- **Contextual Q&A** — Ask questions about any research paper with full conversation memory
- **Follow-up Support** — The system maintains conversation history for coherent multi-turn dialogue
- **Rich Output** — Markdown-rendered answers displayed in styled terminal panels
- **Interactive CLI** — Clean command-line interface with intuitive controls
- **Local & Private** — All processing runs locally via Ollama; your papers never leave your machine

## Installation

```bash
cd 20-research-paper-qa
pip install -r requirements.txt
```

Ensure [Ollama](https://ollama.com) is installed and running with the `gemma4` model:

```bash
ollama serve
ollama pull gemma4
```

## Usage

```bash
python app.py --paper path/to/paper.txt
```

### Interactive Commands

| Command   | Description                        |
|-----------|------------------------------------|
| *(text)*  | Ask a question about the paper     |
| `history` | View past questions and answers    |
| `clear`   | Reset conversation context         |
| `quit`    | Exit the application               |

## Example Session

```
$ python app.py --paper transformer_paper.txt

 Loading paper: transformer_paper.txt
 ✓ Paper loaded (8,432 words)

╭─ 🔍 Research Paper Q&A ─╮
│ Commands:                │
│   • Type your question   │
│   • history              │
│   • clear                │
│   • quit                 │
╰──────────────────────────╯

Ask a question: What is the main contribution of this paper?

╭─ 📄 Answer ──────────────────────────────────────────╮
│ The main contribution of this paper is the           │
│ Transformer architecture, which relies entirely on   │
│ attention mechanisms, dispensing with recurrence and  │
│ convolutions. The authors demonstrate that this      │
│ model achieves state-of-the-art results on machine   │
│ translation benchmarks.                              │
╰──────────────────────────────────────────────────────╯

Ask a question: How many layers does it use?

╭─ 📄 Answer ──────────────────────────────────────────╮
│ According to the paper, the Transformer uses a       │
│ stack of 6 identical layers for both the encoder     │
│ and decoder components.                              │
╰──────────────────────────────────────────────────────╯

Ask a question: quit
 Goodbye!
```

## Testing

```bash
pytest test_app.py -v
```

## Project Structure

```
20-research-paper-qa/
├── app.py              # Main application
├── requirements.txt    # Dependencies
├── test_app.py         # Test suite
└── README.md           # Documentation
```
