# 🔤 Regex Generator

AI-powered tool that generates regular expressions from natural language descriptions and explains existing patterns using a local Gemma 4 LLM.

## ✨ Features

- **Generate from Description** — Describe what you want to match in plain English
- **Explain Patterns** — Get detailed breakdowns of existing regex patterns
- **Test Patterns** — Validate regex against test strings with match highlighting
- **Multi-flavor Support** — Get regex in Python, JavaScript, and PCRE flavors
- **Edge Case Awareness** — Warns about common regex pitfalls

## 📦 Installation

```bash
pip install -r requirements.txt
```

## 🚀 Usage

```bash
# Generate regex from description
python app.py generate "email addresses"
python app.py generate "US phone numbers with area code"

# Generate and test
python app.py generate "IPv4 addresses" --test "192.168.1.1" --test "999.999.999.999"

# Explain an existing regex
python app.py explain "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
python app.py explain "^(?=.*[A-Z])(?=.*\d).{8,}$"

# Test a regex against strings
python app.py test "\d{3}-\d{4}" "555-1234" "hello" "123-4567"
```

## 📋 Example Output

```
╭──────────────────────────────────────────╮
│  🔤 Regex Generator                     │
│  Generate regex from natural language    │
╰──────────────────────────────────────────╯

╭── 🎯 Generated Regex ─────────────────╮
│ Pattern: \d{3}-\d{3}-\d{4}            │
│                                        │
│ Components:                            │
│ • \d{3} - Three digits (area code)     │
│ • -     - Literal hyphen               │
│ • \d{3} - Three digits (exchange)      │
│ • -     - Literal hyphen               │
│ • \d{4} - Four digits (number)         │
╰────────────────────────────────────────╯
```

## 🧪 Testing

```bash
pytest test_app.py -v
```

## ⚙️ Requirements

- Python 3.10+
- Ollama running locally with Gemma 4 model
