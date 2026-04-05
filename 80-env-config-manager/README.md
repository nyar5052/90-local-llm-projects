# ⚙️ Environment Config Manager

AI-powered environment configuration manager that validates .env files, suggests missing variables, and generates templates with security reviews.

## Features

- **Validation**: Security audit of .env files (weak secrets, empty values, defaults)
- **Template Generation**: Create .env templates for Flask, Django, Express, and more
- **Missing Variable Detection**: AI suggests missing vars based on project type
- **Secret Detection**: Identifies and masks sensitive values
- **Multi-Environment**: Development, staging, and production configurations

## Usage

```bash
# Validate an .env file
python app.py --file .env --validate

# Suggest missing variables for a Flask project
python app.py --file .env --suggest flask

# Generate .env template for a project
python app.py generate --project "flask" --env production

# Generate and save template
python app.py generate --project django --env development --output .env.example
```

## Example Output

```
╭──────────────────────────────────────╮
│   ⚙️ Environment Config Manager     │
╰──────────────────────────────────────╯

┌─ Parsed Environment Variables ──────┐
│ Variable     │ Value      │ Status  │
│ APP_NAME     │ MyApp      │ ✅      │
│ SECRET_KEY   │ ***        │ 🔑      │
│ API_KEY      │ (empty)    │ ⚠️      │
└─────────────────────────────────────┘

╭─ Validation Results ────────────────╮
│ ## Security Issues                  │
│ - ❌ SECRET_KEY uses default value  │
│ - ⚠️ API_KEY is empty              │
│ - ⚠️ DEBUG=true in production      │
│                                     │
│ ## Recommendations                  │
│ 1. Use a secret manager             │
│ 2. Rotate all default secrets       │
╰─────────────────────────────────────╯
```

## Requirements

- Python 3.10+
- Ollama running locally with Gemma 4 model
- Dependencies: `pip install -r requirements.txt`

## Testing

```bash
pytest test_app.py -v
```
