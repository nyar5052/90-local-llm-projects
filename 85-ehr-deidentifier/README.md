# 🛡️ EHR De-Identifier

> ⚠️ **CRITICAL DISCLAIMER**: This tool is for **EDUCATIONAL and RESEARCH purposes ONLY**. It is **NOT** certified for **HIPAA compliance**. Do **NOT** rely on this tool for actual medical record de-identification in clinical or production settings. **ALWAYS** use certified, validated de-identification tools for real patient data. This is **NOT** medical or legal advice.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../LICENSE)
[![Ollama](https://img.shields.io/badge/LLM-Ollama-green.svg)](https://ollama.ai)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-red.svg)](https://streamlit.io)
[![NOT HIPAA](https://img.shields.io/badge/HIPAA-NOT%20Certified-red.svg)](#-hipaa-compliance-notice)

An AI-powered EHR de-identification tool that removes Protected Health Information (PHI) from medical records using regex pattern matching and LLM analysis. Features configurable PII rules, audit logging, batch processing, and validation reports.

---

## 🚨 HIPAA Compliance Notice

> **⛔ THIS TOOL IS NOT HIPAA CERTIFIED ⛔**
>
> This tool is a **demonstration/educational project** and has NOT been validated or certified for HIPAA compliance.
>
> - ❌ Do NOT use this on real patient data
> - ❌ Do NOT use this in clinical or production environments
> - ❌ This tool may MISS PHI or produce INCOMPLETE de-identification
> - ❌ No warranty of any kind is provided
> - ✅ Use certified de-identification tools (e.g., Scrubadub, Philter, clinical NLP tools) for real data
> - ✅ Always have a qualified professional review de-identified records
>
> **Using this tool on real patient data could violate HIPAA regulations and result in serious legal consequences.**

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔍 **Regex Detection** | Pattern-based PII detection for SSN, phone, email, dates, MRN |
| 🤖 **LLM Analysis** | AI-powered detection for names, addresses, and contextual PHI |
| ⚙️ **Configurable Rules** | Enable/disable individual PII detection rules |
| 📋 **Audit Log** | Complete audit trail of all de-identification operations |
| 📦 **Batch Processing** | Process multiple files in one operation |
| ✅ **Validation Reports** | Automated quality checks on de-identification results |
| 🌐 **Web UI** | Interactive Streamlit interface with file upload |
| ⚡ **CLI Tool** | Fast command-line processing |
| 📊 **PII Statistics** | Visual breakdown of detected PII types |

---

## 🏗️ Architecture

```
85-ehr-deidentifier/
├── src/
│   └── ehr_deidentifier/
│       ├── __init__.py
│       ├── core.py              # Core logic, PII rules, audit, validation
│       ├── cli.py               # Click CLI interface
│       └── web_ui.py            # Streamlit web interface
├── tests/
│   ├── __init__.py
│   ├── test_core.py
│   └── test_cli.py
├── config.yaml
├── setup.py
├── requirements.txt
├── Makefile
├── .env.example
└── README.md
```

---

## 🔐 HIPAA Safe Harbor - 18 Identifiers

This tool attempts to detect the following HIPAA Safe Harbor identifiers:

| # | Identifier | Detection Method |
|---|-----------|-----------------|
| 1 | Names | LLM |
| 2 | Geographic data | LLM |
| 3 | Dates | Regex + LLM |
| 4 | Phone numbers | Regex |
| 5 | Fax numbers | Regex |
| 6 | Email addresses | Regex |
| 7 | SSN | Regex |
| 8 | Medical record numbers | Regex |
| 9 | Health plan numbers | LLM |
| 10 | Account numbers | LLM |
| 11 | Certificate/license numbers | LLM |
| 12 | Vehicle identifiers | LLM |
| 13 | Device identifiers | LLM |
| 14 | Web URLs | Regex |
| 15 | IP addresses | Regex |
| 16 | Biometric identifiers | LLM |
| 17 | Full-face photographs | N/A (text only) |
| 18 | Other unique identifiers | LLM |

---

## 🚀 Installation

```bash
cd 85-ehr-deidentifier
make install
cp .env.example .env
```

---

## 💻 CLI Usage

### De-identify a File
```bash
python -m ehr_deidentifier.cli deidentify --file patient_record.txt --output clean_record.txt
```

### De-identify Inline Text
```bash
python -m ehr_deidentifier.cli text --input "Patient John Smith, SSN 123-45-6789"
```

### Batch Processing
```bash
python -m ehr_deidentifier.cli batch --directory ./records/ --output-dir ./clean/
```

### View Audit Log
```bash
python -m ehr_deidentifier.cli audit
```

### Validation Report
```bash
python -m ehr_deidentifier.cli validate --file patient_record.txt
```

### List PII Rules
```bash
python -m ehr_deidentifier.cli rules
```

---

## 🌐 Web UI

```bash
make run-web
```

---

## 🧪 Testing

```bash
make test
```

---

## ⚠️ Disclaimer

**This tool is for EDUCATIONAL and RESEARCH purposes ONLY. It is NOT certified for HIPAA compliance. Do NOT use this tool for actual patient data de-identification. Always use certified, validated tools and have qualified professionals review results.**

---

*Part of the [90 Local LLM Projects](../../README.md) collection.*
