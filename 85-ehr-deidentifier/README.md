# 85 - EHR De-Identifier

> **⚠️ DISCLAIMER: This tool is for EDUCATIONAL and RESEARCH purposes ONLY. It is NOT certified for HIPAA compliance and must NOT be used for actual patient data de-identification in clinical or production environments. Always use certified, validated de-identification tools for real Protected Health Information (PHI). This is NOT medical or legal advice.**

De-identifies medical records by removing Personally Identifiable Information (PII) and Protected Health Information (PHI). Uses a combination of regex pattern matching and local LLM analysis to replace sensitive data with bracketed placeholders.

## Features

- **Dual-layer de-identification**: Regex pre-processing for structured patterns (SSNs, phones, emails, dates) followed by LLM analysis for contextual PII (names, addresses, etc.)
- **File processing**: De-identify entire medical record files
- **Inline text**: Quickly de-identify text snippets from the command line
- **Rich output**: Color-coded display showing original vs. de-identified text with a replacement log
- **Graceful fallback**: If the LLM is unavailable, regex-only results are still returned

## Placeholder Types

| PII Type | Placeholder |
|---|---|
| Names | `[NAME_1]`, `[NAME_2]`, ... |
| Dates | `[DATE_1]`, `[DATE_2]`, ... |
| SSNs | `[SSN_1]`, `[SSN_2]`, ... |
| Phone numbers | `[PHONE_1]`, `[PHONE_2]`, ... |
| Addresses | `[ADDRESS_1]`, `[ADDRESS_2]`, ... |
| Medical Record Numbers | `[MRN_1]`, `[MRN_2]`, ... |
| Email addresses | `[EMAIL_1]`, `[EMAIL_2]`, ... |

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) running locally with a model pulled (e.g., `ollama pull llama3.2`)

## Setup

```bash
cd 85-ehr-deidentifier
pip install -r requirements.txt
```

## Usage

### De-identify a file

```bash
python app.py deidentify --file medical_record.txt --output deidentified.txt
```

### De-identify inline text

```bash
python app.py text --input "Patient John Smith, DOB 01/15/1980, visited on 03/22/2024"
```

## Running Tests

```bash
pytest test_app.py -v
```

## How It Works

1. **Regex pre-processing** scans for structured PII patterns (SSN, phone, email, dates) and replaces them with placeholders.
2. **LLM analysis** sends the partially de-identified text to a local LLM which identifies remaining contextual PII (names, addresses, medical record numbers, etc.).
3. **Results display** shows original text, a table of regex-detected items, and the final de-identified output.

## ⚠️ Important Limitations

- This tool uses a local LLM which may miss PII or incorrectly flag non-PII text.
- Regex patterns cover common US formats only and may miss international formats.
- **Never use this on real patient data** — use HIPAA-certified tools for production use.
- The LLM may hallucinate or alter medical terminology despite instructions not to.
- This tool has not been validated against any de-identification benchmarks.
