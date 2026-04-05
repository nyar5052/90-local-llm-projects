# 📚 Personal Knowledge Base

AI-powered note storage and semantic search using a local Gemma 4 LLM via Ollama.

## Features

- **Smart Note Storage**: Store notes with titles, content, and tags in JSON format
- **Semantic Search**: AI-powered search that understands meaning, not just keywords
- **Knowledge Summary**: Generate an overview of your entire knowledge base
- **Connection Discovery**: Find relationships between different notes
- **Tag Organization**: Organize notes with flexible tagging

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) running locally with Gemma 4 model
- Start Ollama: `ollama serve`
- Pull model: `ollama pull gemma4`

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Add a Note
```bash
python app.py add --title "ML Notes" --content "Neural networks use backpropagation for training" --tags "ml,ai"
```

### Search Notes
```bash
python app.py search --query "neural network training"
```

### List All Notes
```bash
python app.py list
```

### Generate Summary
```bash
python app.py summary
```

### Delete a Note
```bash
python app.py delete --note-id 1
```

## Example Output

```
╭────────── 📚 Personal Knowledge Base ──────────╮
│ Searching for: neural network training          │
╰─────────────────────────────────────────────────╯

╭─────────── 🔍 Search Results ───────────╮
│ ## Relevant Notes                        │
│ - Note #1: ML Notes covers neural        │
│   networks and backpropagation           │
│ - Related topics: deep learning, SGD     │
╰──────────────────────────────────────────╯
```

## Testing

```bash
pytest test_app.py -v
```

## License

MIT
