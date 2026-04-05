# 🧪 Unit Test Generator

AI-powered tool that automatically generates comprehensive unit tests for Python functions and classes using a local Gemma 4 LLM.

## ✨ Features

- **AST Analysis** — Extracts functions, classes, methods, and their signatures
- **Framework Support** — Generates tests for pytest or unittest
- **Comprehensive Coverage** — Creates happy path, edge case, and error tests
- **Parametrized Tests** — Uses pytest.parametrize for similar test cases
- **Mock Support** — Automatically mocks external dependencies
- **File Output** — Save generated tests directly to a test file

## 📦 Installation

```bash
pip install -r requirements.txt
```

## 🚀 Usage

```bash
# Generate pytest tests (default)
python app.py --file module.py

# Generate unittest tests
python app.py --file module.py --framework unittest

# Save to a file
python app.py --file module.py --output test_module.py

# Show source code before generating
python app.py --file module.py --show-source
```

## 📋 Example Output

```
╭──────────────────────────────────────────╮
│  🧪 Unit Test Generator                 │
│  Generate comprehensive unit tests       │
╰──────────────────────────────────────────╯

╭── 📊 Code Structure ──────────────────╮
│ Type     │ Name         │ Details      │
│ Function │ add          │ (a, b)       │
│ Function │ divide       │ (a, b)       │
│ Class    │ StringUtils  │ 2 methods    │
╰────────────────────────────────────────╯

╭── 🧪 Generated Tests ─────────────────╮
│ ```python                              │
│ import pytest                          │
│ from module import add, divide         │
│                                        │
│ class TestAdd:                         │
│     def test_positive_numbers(self):   │
│         assert add(2, 3) == 5          │
│                                        │
│     def test_negative_numbers(self):   │
│         assert add(-1, -1) == -2       │
│ ```                                    │
╰────────────────────────────────────────╯
```

## 🧪 Testing

```bash
pytest test_app.py -v
```

## ⚙️ Requirements

- Python 3.10+
- Ollama running locally with Gemma 4 model
