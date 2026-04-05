# 🏥 First Aid Guide Bot

A local LLM-powered first aid information assistant that provides step-by-step guidance for common emergency situations. Always recommends calling emergency services for serious situations.

---

> **🚨 EMERGENCY DISCLAIMER**
>
> **This tool is NOT a substitute for emergency medical services.**
> **This is NOT medical advice.**
>
> - **For life-threatening emergencies, CALL 911 IMMEDIATELY.**
> - **For poison control, call 1-800-222-1222.**
> - Always seek professional medical evaluation for injuries and illness.
> - This tool provides general first aid information only.

---

## Features

| Command | Description |
|---------|-------------|
| `python app.py guide --situation "minor burn"` | Get step-by-step first aid for a specific situation |
| `python app.py chat` | Interactive first aid assistant |
| `python app.py list` | List common first aid scenarios with severity levels |

### 📋 Guide Mode
Get detailed, structured first aid instructions for any situation, including:
- ⚠️ Emergency warning signs (when to call 911)
- 📝 Numbered step-by-step instructions
- 🚫 What NOT to do (common mistakes to avoid)
- 🏥 When to seek professional medical help

### 🗣️ Chat Mode
Ask follow-up questions interactively. The assistant maintains conversation context for multi-step guidance.

### 📊 List Mode
Browse 15 common first aid scenarios with severity ratings:
- Burns, cuts, choking, sprains, allergic reactions
- Nosebleed, bee stings, heat exhaustion, hypothermia
- Fractures, seizures, fainting, eye injuries, poisoning

## Prerequisites

- Python 3.8+
- [Ollama](https://ollama.ai/) running locally with a model pulled (e.g., `ollama pull llama3.2`)

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Get first aid for a specific situation
python app.py guide --situation "minor burn"
python app.py guide -s "choking adult"
python app.py guide -s "allergic reaction"

# Interactive chat mode
python app.py chat

# List common scenarios
python app.py list
```

## Testing

```bash
pytest test_app.py -v
```

## How It Works

The bot connects to a locally running LLM via Ollama. All processing happens on your machine — **no data is sent to external servers**. The LLM is instructed to always prioritize safety, recommend emergency services for serious situations, and provide clear step-by-step instructions.

## Emergency Resources

- **Emergency Services**: Call **911**
- **Poison Control**: **1-800-222-1222**
- **American Red Cross First Aid App**: [Download](https://www.redcross.org/get-help/how-to-prepare-for-emergencies/mobile-apps.html)
- **Mayo Clinic First Aid**: https://www.mayoclinic.org/first-aid

---

*This tool is for general informational purposes only and is NOT medical advice. Always call 911 for life-threatening emergencies and seek professional medical care for injuries and illness.*
