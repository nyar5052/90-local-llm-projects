# 🎯 100 Local LLM Projects

> A curated collection of 100 production-level AI applications — all running locally with Gemma 4 + Ollama. Zero cloud costs. 100% private.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Local LLM](https://img.shields.io/badge/LLM-Gemma%204%20via%20Ollama-orange.svg)]()
[![Privacy](https://img.shields.io/badge/Privacy-100%25%20Local-brightgreen.svg)]()
[![Projects](https://img.shields.io/badge/Projects-100-purple.svg)]()

## 🎬 Demo

Each project includes a Streamlit or FastAPI web interface. Launch any project and interact with it through a clean, modern UI — all powered by a local LLM with zero API calls.

## 🔥 Why This Exists

Cloud AI APIs are expensive, rate-limited, and your data leaves your machine. This collection proves you can build **production-quality AI applications** that run entirely on your hardware. From healthcare to legal, education to creative writing — 100 real-world tools, all powered by a single local model.

Whether you're a developer exploring LLM capabilities, a privacy-conscious professional, or someone who wants to build AI tools without recurring API costs — this repo is your launchpad.

## ✨ Features

- 🧠 **100 production-level AI applications** spanning 15+ domains
- 🔒 **100% local processing** — no data ever leaves your machine
- 💰 **Zero cloud costs** — no API keys, no subscriptions, no usage limits
- 🏥 **Healthcare AI** — patient intake summarizer, symptom checker, drug interaction analyzer
- ⚖️ **Legal AI** — contract clause analyzer, legal brief summarizer, compliance checker
- 🎓 **Education AI** — study buddy bot, essay grader, language learning assistant
- 💻 **Developer Tools** — code reviewer, API doc generator, git commit message writer
- 🎨 **Creative AI** — story writer, poetry generator, recipe creator
- 📊 **Business AI** — resume analyzer, meeting summarizer, email draft assistant
- 🐾 **Specialty Bots** — veterinary advisor, fitness coach, travel planner, and more
- 🖥️ **Multiple interfaces** — CLI, Streamlit Web UI, and FastAPI REST API for each project
- 🐳 **Docker support** — containerized deployment for every project
- ✅ **Test suites** — pytest coverage included

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface Layer                   │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │   CLI    │  │ Streamlit UI │  │  FastAPI REST API  │  │
│  └────┬─────┘  └──────┬───────┘  └─────────┬─────────┘  │
│       └───────────────┬┼────────────────────┘            │
│                       ▼▼                                 │
│              ┌─────────────────┐                         │
│              │   Core Engine   │  (domain-specific logic) │
│              │  + LLM Client   │                         │
│              └────────┬────────┘                         │
│                       ▼                                  │
│              ┌─────────────────┐                         │
│              │  Common Module  │  (shared LLM interface)  │
│              └────────┬────────┘                         │
│                       ▼                                  │
│              ┌─────────────────┐                         │
│              │  Ollama Server  │  (Gemma 4 model)        │
│              │  localhost:11434│                          │
│              └─────────────────┘                         │
└─────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **[Ollama](https://ollama.com)** installed and running
- **Gemma 4** model pulled: `ollama pull gemma4`

### Installation

```bash
git clone https://github.com/kennedyraju55/90-local-llm-projects.git
cd 90-local-llm-projects

# Pick any project (e.g., patient-intake-summarizer)
cd patient-intake-summarizer
pip install -r requirements.txt
```

### Usage

Each project supports three interfaces:

```bash
# CLI
python -m src.<project_name>.cli analyze --input example.txt

# Streamlit Web UI
streamlit run src/<project_name>/web_ui.py

# FastAPI REST API
uvicorn src.<project_name>.api:app --reload
```

## 📁 Project Structure

```
90-local-llm-projects/
├── patient-intake-summarizer/     # 🏥 Healthcare AI
├── contract-clause-analyzer/      # ⚖️ Legal AI
├── pdf-chat-assistant/            # 📄 RAG-based PDF Q&A
├── code-review-assistant/         # 💻 Developer Tools
├── resume-analyzer/               # 📊 Business AI
├── study-buddy-bot/               # 🎓 Education AI
├── fitness-coach-bot/             # 🏋️ Health & Wellness
├── meal-planner-bot/              # 🍽️ Nutrition AI
├── travel-itinerary-bot/          # ✈️ Travel Planning
├── it-helpdesk-bot/               # 🖥️ IT Support
├── veterinary-advisor-bot/        # 🐾 Pet Care AI
├── ... (90+ more projects)        #
├── common/                        # 🔧 Shared LLM client module
│   └── llm_client.py              #    Ollama API wrapper
└── README.md
```

## 🗂️ Project Categories

| Category | Count | Examples |
|----------|-------|---------|
| 🏥 Healthcare | 10+ | Patient intake summarizer, symptom checker, drug interaction analyzer |
| ⚖️ Legal | 8+ | Contract analyzer, legal brief summarizer, compliance checker |
| 🎓 Education | 10+ | Study buddy, essay grader, language tutor, quiz generator |
| 💻 Developer Tools | 8+ | Code reviewer, API doc generator, commit message writer |
| 🎨 Creative | 8+ | Story writer, poetry generator, recipe creator |
| 📊 Business | 10+ | Resume analyzer, meeting summarizer, email assistant |
| 🐾 Specialty | 15+ | Vet advisor, fitness coach, travel planner, gift recommender |
| 🔐 Security | 5+ | Password policy analyzer, phishing detector |

## 🤝 Contributing

Contributions welcome! Whether it's a new project idea, bug fix, or improvement to an existing tool — please open an issue or submit a PR.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-project`)
3. Commit your changes (`git commit -m 'Add amazing AI project'`)
4. Push to the branch (`git push origin feature/amazing-project`)
5. Open a Pull Request

## 📄 License

MIT License — see [LICENSE](LICENSE)

## 👨‍💻 Author

**Nrk Raju Guthikonda**
- 🏢 Senior Software Engineer at Microsoft (Copilot Search Infrastructure)
- 🔗 [GitHub](https://github.com/kennedyraju55) | [LinkedIn](https://www.linkedin.com/in/nrk-raju-guthikonda-504066a8/)
- 🚀 Building 116+ open-source AI tools for real-world impact

---

<p align="center">
  <b>⭐ If this collection helps you build local AI apps, give it a star!</b>
</p>
