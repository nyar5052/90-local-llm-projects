<div align="center">

# 🚀 90 Production-Level Projects with Local LLM

### Built with Gemma 4 + Ollama | 100% Private & Offline

[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-black?style=for-the-badge&logo=ollama&logoColor=white)](https://ollama.ai)
[![Gemma](https://img.shields.io/badge/Gemma_4-Google-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/gemma)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Projects](https://img.shields.io/badge/Projects-90-red?style=for-the-badge)]()

<br/>

> **🔒 Your data never leaves your machine.** All 90 projects run entirely on your local hardware using Gemma 4 via Ollama. No API keys, no cloud costs, no data sharing.

<br/>

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   🤖 90 Projects  ·  9 Categories  ·  100% Local AI    │
│                                                         │
│   Built for developers, students, and professionals     │
│   who value privacy, speed, and zero cloud costs.       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

</div>

---

## 📋 Table of Contents

- [🌟 Why Local LLMs?](#-why-local-llms)
- [⚡ Quick Start](#-quick-start)
- [📂 All 90 Projects](#-all-90-projects)
- [🏗️ Architecture](#️-architecture)
- [🛠️ Tech Stack](#️-tech-stack)
- [📊 Project Categories](#-project-categories)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

---

## 🌟 Why Local LLMs?

| Feature | Cloud LLMs | Local LLMs (This Repo) |
|---------|-----------|----------------------|
| 🔒 Privacy | Data sent to servers | **Data stays on your machine** |
| 💰 Cost | Pay per token | **Completely free** |
| 🌐 Internet | Required | **Works offline** |
| ⚡ Speed | Network latency | **Local inference** |
| 🎛️ Control | Limited customization | **Full control** |
| 📊 Data | Subject to policies | **Your rules** |

---

## ⚡ Quick Start

### Prerequisites

1. **Install Ollama** → [ollama.ai](https://ollama.ai)
2. **Pull Gemma 4** model:
   ```bash
   ollama pull gemma4
   ```
3. **Clone this repo:**
   ```bash
   git clone https://github.com/kennedyraju55/90-local-llm-projects.git
   cd 90-local-llm-projects
   ```
4. **Install base dependencies:**
   ```bash
   pip install -r requirements-base.txt
   ```

### Run Any Project

```bash
# Navigate to any project folder
cd 01-pdf-chat-assistant

# Install project-specific dependencies
pip install -r requirements.txt

# Run the project
python app.py --help
```

---

## 📂 All 90 Projects

### 🤖 Category 1: Chatbots & Conversational AI

| # | Project | Description | Key Features |
|---|---------|-------------|--------------|
| 01 | [PDF Chat Assistant](01-pdf-chat-assistant/) | Ask questions about PDFs | PDF parsing, context-aware Q&A |
| 02 | [IT Helpdesk Bot](02-it-helpdesk-bot/) | Local IT support chatbot | Troubleshooting, knowledge base |
| 03 | [Meal Planner Bot](03-meal-planner-bot/) | Recipe & meal suggestions | Dietary preferences, weekly plans |
| 04 | [Fitness Coach Bot](04-fitness-coach-bot/) | Personalized workout plans | Equipment-aware, progressive |
| 05 | [Travel Itinerary Bot](05-travel-itinerary-bot/) | Vacation planning assistant | Budget-aware, day-by-day plans |
| 06 | [Language Learning Bot](06-language-learning-bot/) | Practice conversations | Grammar correction, levels |
| 07 | [Veterinary Advisor Bot](07-veterinary-advisor-bot/) | Pet health chatbot | Species-specific advice |
| 08 | [Gift Recommendation Bot](08-gift-recommendation-bot/) | Personalized gift ideas | Occasion & budget aware |
| 09 | [Study Buddy Bot](09-study-buddy-bot/) | Exam preparation helper | Quizzing, concept explanations |
| 10 | [Mood Journal Bot](10-mood-journal-bot/) | Private mood tracking | Sentiment analysis, patterns |

### 📄 Category 2: Document Processing & Analysis

| # | Project | Description | Key Features |
|---|---------|-------------|--------------|
| 11 | [Legal Doc Summarizer](11-legal-doc-summarizer/) | Contract & legal analysis | Key clauses, obligations |
| 12 | [Resume Analyzer](12-resume-analyzer/) | Resume optimization tool | Job matching, scoring |
| 13 | [Meeting Summarizer](13-meeting-summarizer/) | Transcript to action items | Decisions, follow-ups |
| 14 | [Medical Lit Summarizer](14-medical-lit-summarizer/) | Research paper summaries | Methodology, findings |
| 15 | [Invoice Extractor](15-invoice-extractor/) | Receipt data extraction | Structured JSON output |
| 16 | [PDF Report Generator](16-pdf-report-generator/) | Auto report generation | Data-driven narratives |
| 17 | [Textbook Summarizer](17-textbook-summarizer/) | Chapter summaries | Key concepts, definitions |
| 18 | [Policy Compliance Checker](18-policy-compliance-checker/) | Regulation review | Compliance scoring |
| 19 | [News Digest Generator](19-news-digest-generator/) | RSS feed summarization | Topic grouping |
| 20 | [Research Paper Q&A](20-research-paper-qa/) | Academic Q&A assistant | Citation-aware answers |

### 💻 Category 3: Code & Developer Tools

| # | Project | Description | Key Features |
|---|---------|-------------|--------------|
| 21 | [Code Review Bot](21-code-review-bot/) | Code review & bug detection | Security, performance focus |
| 22 | [Commit Message Generator](22-commit-message-generator/) | Smart git commits | Conventional commits |
| 23 | [Stack Trace Explainer](23-stack-trace-explainer/) | Debug helper | Plain English errors |
| 24 | [Regex Generator](24-regex-generator/) | Pattern builder & explainer | Generate & explain regex |
| 25 | [API Doc Generator](25-api-doc-generator/) | Auto API documentation | Function extraction |
| 26 | [Code Snippet Search](26-code-snippet-search/) | Local code finder | NL-powered search |
| 27 | [SQL Query Generator](27-sql-query-generator/) | Natural language to SQL | Schema-aware |
| 28 | [Code Translator](28-code-translator/) | Language converter | 5+ languages |
| 29 | [Unit Test Generator](29-unit-test-generator/) | Auto test writing | pytest output |
| 30 | [Code Complexity Analyzer](30-code-complexity-analyzer/) | Quality metrics | Readability scores |

### ✍️ Category 4: Content Creation & Writing

| # | Project | Description | Key Features |
|---|---------|-------------|--------------|
| 31 | [Blog Post Generator](31-blog-post-generator/) | SEO-friendly articles | Tone control, keywords |
| 32 | [Social Media Writer](32-social-media-writer/) | Multi-platform posts | Platform-specific |
| 33 | [Email Campaign Writer](33-email-campaign-writer/) | Marketing copy | A/B variants |
| 34 | [Poem & Lyrics Generator](34-poem-lyrics-generator/) | Creative writing | Multiple styles |
| 35 | [Video Script Writer](35-video-script-writer/) | YouTube scripts | Timestamps, B-roll |
| 36 | [Newsletter Editor](36-newsletter-editor/) | Content curation | Section formatting |
| 37 | [Story Outline Generator](37-story-outline-generator/) | Fiction planning | Characters, plots |
| 38 | [Product Description Writer](38-product-description-writer/) | E-commerce copy | SEO-optimized |
| 39 | [Presentation Generator](39-presentation-generator/) | Slide scripts | Speaker notes |
| 40 | [Cover Letter Generator](40-cover-letter-generator/) | Job applications | Resume matching |

### 📊 Category 5: Data & Business Intelligence

| # | Project | Description | Key Features |
|---|---------|-------------|--------------|
| 41 | [CSV Data Analyzer](41-csv-data-analyzer/) | Upload & analyze CSVs | NL queries, pandas |
| 42 | [Sentiment Analysis Dashboard](42-sentiment-analysis-dashboard/) | Customer feedback | Confidence scores |
| 43 | [Survey Response Analyzer](43-survey-response-analyzer/) | Insights extraction | Theme grouping |
| 44 | [Stock Report Generator](44-stock-report-generator/) | Financial analysis | Trend narrative |
| 45 | [Competitor Analysis Tool](45-competitor-analysis-tool/) | Market research | SWOT analysis |
| 46 | [Support Ticket Classifier](46-support-ticket-classifier/) | Auto routing | Priority scoring |
| 47 | [Financial Report Generator](47-financial-report-generator/) | Accounting summaries | Period comparison |
| 48 | [Sales Email Generator](48-sales-email-generator/) | Outreach copy | Personalization |
| 49 | [KPI Dashboard Reporter](49-kpi-dashboard-reporter/) | Business metrics | Trend highlights |
| 50 | [Trend Analysis Tool](50-trend-analysis-tool/) | Market trends | Topic detection |

### 🎓 Category 6: Education & Learning

| # | Project | Description | Key Features |
|---|---------|-------------|--------------|
| 51 | [Quiz Generator](51-quiz-generator/) | Auto assessments | Multiple formats |
| 52 | [Flashcard Creator](52-flashcard-creator/) | Study cards | Review mode |
| 53 | [Essay Grader](53-essay-grader/) | Writing evaluation | Rubric scoring |
| 54 | [Curriculum Planner](54-curriculum-planner/) | Course design | Weekly breakdown |
| 55 | [Science Experiment Explainer](55-science-experiment-explainer/) | Lab guides | Safety, materials |
| 56 | [Math Problem Solver](56-math-problem-solver/) | Step-by-step solutions | Multi-topic |
| 57 | [History Timeline Generator](57-history-timeline-generator/) | Event summaries | Key dates |
| 58 | [Vocabulary Builder](58-vocabulary-builder/) | Word learning | Quiz mode |
| 59 | [Debate Topic Generator](59-debate-topic-generator/) | Critical thinking | Pro/con arguments |
| 60 | [Reading Comprehension Builder](60-reading-comprehension-builder/) | Passage analysis | Q&A generation |

### 🏠 Category 7: Personal Productivity

| # | Project | Description | Key Features |
|---|---------|-------------|--------------|
| 61 | [Smart Calendar Assistant](61-smart-calendar-assistant/) | Schedule optimization | Meeting suggestions |
| 62 | [Personal Knowledge Base](62-personal-knowledge-base/) | Semantic search notes | AI-powered search |
| 63 | [Diary Journal Organizer](63-diary-journal-organizer/) | Private notes | AI insights |
| 64 | [Household Budget Analyzer](64-household-budget-analyzer/) | Expense tracking | Category breakdown |
| 65 | [Reading List Manager](65-reading-list-manager/) | Book summaries | Recommendations |
| 66 | [Home Automation Scripter](66-home-automation-scripter/) | IoT scripts | YAML configs |
| 67 | [Family Story Creator](67-family-story-creator/) | Memory preservation | Narrative generation |
| 68 | [Habit Tracker Analyzer](68-habit-tracker-analyzer/) | Behavior analysis | Streak tracking |
| 69 | [Standup Generator](69-standup-generator/) | Meeting prep | Git-aware |
| 70 | [Time Management Coach](70-time-management-coach/) | Productivity tips | Time analysis |

### 🔒 Category 8: Security, Privacy & DevOps

| # | Project | Description | Key Features |
|---|---------|-------------|--------------|
| 71 | [Cybersecurity Alert Summarizer](71-cybersecurity-alert-summarizer/) | Threat reports | Priority ranking |
| 72 | [Incident Report Generator](72-incident-report-generator/) | Security logs | Timeline, remediation |
| 73 | [GDPR Compliance Checker](73-gdpr-compliance-checker/) | Privacy review | Data handling checks |
| 74 | [Password Strength Advisor](74-password-strength-advisor/) | Security tips | Policy analysis |
| 75 | [Log File Analyzer](75-log-file-analyzer/) | System diagnostics | Pattern detection |
| 76 | [Docker Compose Generator](76-docker-compose-generator/) | Container configs | Stack templates |
| 77 | [CI/CD Pipeline Generator](77-cicd-pipeline-generator/) | Workflow automation | Multi-platform |
| 78 | [Infra Doc Generator](78-infra-doc-generator/) | Cloud documentation | Config to docs |
| 79 | [Vulnerability Report Writer](79-vulnerability-report-writer/) | Security assessment | Executive summaries |
| 80 | [Env Config Manager](80-env-config-manager/) | Settings helper | Validation, security |

### 🏥 Category 9: Healthcare & Wellness

| # | Project | Description | Key Features |
|---|---------|-------------|--------------|
| 81 | [Symptom Checker Bot](81-symptom-checker-bot/) | Health triage | Medical disclaimers |
| 82 | [Drug Interaction Checker](82-drug-interaction-checker/) | Medication safety | Education-only |
| 83 | [Medical Terms Explainer](83-medical-terms-explainer/) | Health literacy | Etymology, usage |
| 84 | [Health Plan Generator](84-health-plan-generator/) | Wellness advice | Holistic plans |
| 85 | [EHR De-identifier](85-ehr-deidentifier/) | Privacy tool | PII removal |
| 86 | [Nutrition Label Analyzer](86-nutrition-label-analyzer/) | Food analysis | Health insights |
| 87 | [Exercise Form Guide](87-exercise-form-guide/) | Workout instructions | Safety tips |
| 88 | [Sleep Improvement Advisor](88-sleep-improvement-advisor/) | Rest optimization | Pattern analysis |
| 89 | [Stress Management Bot](89-stress-management-bot/) | Coping strategies | CBT techniques |
| 90 | [First Aid Guide Bot](90-first-aid-guide-bot/) | Emergency help | Step-by-step |

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     User Interface                       │
│              (CLI / Streamlit / Gradio)                   │
├──────────────────────────────────────────────────────────┤
│                   Application Layer                      │
│         (90 Python apps with business logic)             │
├──────────────────────────────────────────────────────────┤
│                  Common LLM Client                       │
│           (common/llm_client.py - shared)                │
├──────────────────────────────────────────────────────────┤
│                   Ollama Server                          │
│              (http://localhost:11434)                     │
├──────────────────────────────────────────────────────────┤
│                    Gemma 4 Model                         │
│              (9.6 GB - runs locally)                     │
└──────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Technology | Purpose |
|-----------|---------|
| **Python 3.10+** | Core language |
| **Ollama** | Local LLM server |
| **Gemma 4** | Google's local LLM model |
| **Rich** | Beautiful terminal output |
| **Click** | CLI framework |
| **Pytest** | Testing |
| **Pydantic** | Data validation |
| **Requests** | HTTP client for Ollama |

---

## 📁 Repository Structure

```
90-local-llm-projects/
├── common/                    # Shared utilities
│   ├── __init__.py
│   └── llm_client.py         # Ollama client library
├── 01-pdf-chat-assistant/     # Project 1
│   ├── app.py                 # Main application
│   ├── requirements.txt       # Dependencies
│   ├── test_app.py           # Tests
│   └── README.md             # Documentation
├── 02-it-helpdesk-bot/        # Project 2
│   └── ...
├── ...                        # Projects 3-90
├── web-book/                  # LinkedIn web book
├── assets/images/             # Project images
├── requirements-base.txt      # Base dependencies
├── .gitignore
└── README.md                  # This file
```

---

## 📊 Project Statistics

- **Total Projects:** 90
- **Categories:** 9
- **Language:** Python
- **LLM:** Gemma 4 (100% local)
- **Tests:** 400+ unit tests
- **Lines of Code:** 15,000+

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-project`)
3. Commit your changes (`git commit -m 'Add amazing project'`)
4. Push to the branch (`git push origin feature/amazing-project`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ⭐ Star This Repo!

If you find these projects useful, please give this repo a ⭐! It helps others discover it.

---

<div align="center">

**Built with ❤️ using Local AI**

*No data was sent to the cloud in the making of these projects.*

[⬆ Back to Top](#-90-production-level-projects-with-local-llm)

</div>
