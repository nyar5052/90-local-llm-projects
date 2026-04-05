# 🔑 Password Strength Advisor

AI-powered password policy analyzer and secure password generator using a local LLM for NIST/OWASP compliance checking.

## Features

- **Policy Analysis**: Check password policies against NIST SP 800-63B
- **Password Strength Check**: Analyze individual passwords for weaknesses
- **Secure Generation**: Cryptographically secure password generation
- **Compliance Rating**: STRONG ✅ / ADEQUATE ⚠️ / WEAK ❌ ratings
- **Best Practices**: OWASP-aligned recommendations

## Usage

```bash
# Analyze a password policy
python app.py --policy policy.txt --analyze

# Check password strength
python app.py --password "MyPassword123"

# Generate secure passwords
python app.py generate --length 16 --requirements "upper,lower,digits,special"

# Generate multiple passwords
python app.py generate --length 20 --count 10
```

## Example Output

```
╭──────────────────────────────────────╮
│   🔑 Password Strength Advisor      │
╰──────────────────────────────────────╯

┌─ Generated Passwords (length=16) ──┐
│ #  │ Password         │ Length     │
│ 1  │ kX9!mQ2@pL7#nR4  │ 16        │
│ 2  │ Wz5$jH8&vT3*bY6  │ 16        │
│ 3  │ fA1^cN6%dG9!eU2  │ 16        │
└────────────────────────────────────-┘
```

## Requirements

- Python 3.10+
- Ollama running locally with Gemma 4 model
- Dependencies: `pip install -r requirements.txt`

## Testing

```bash
pytest test_app.py -v
```
