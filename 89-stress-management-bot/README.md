# 🧘 Stress Management Bot

An interactive stress management chatbot powered by a local LLM. Features guided breathing exercises, CBT-based techniques, journaling prompts, and personalized stress assessments.

---

> **⚠️ IMPORTANT DISCLAIMER**
>
> This tool is **NOT** a substitute for professional mental health care. It is **NOT medical advice**. It provides general wellness suggestions only.
>
> **If you are in crisis, please contact:**
> - **988 Suicide & Crisis Lifeline**: Call or text **988**
> - **Crisis Text Line**: Text **HOME** to **741741**
> - **Emergency Services**: Call **911**
> - **International Association for Suicide Prevention**: https://www.iasp.info/resources/Crisis_Centres/

---

## Features

| Command | Description |
|---------|-------------|
| `python app.py chat` | Interactive stress management conversation |
| `python app.py breathe` | Guided breathing exercise (Box Breathing or 4-7-8) |
| `python app.py journal` | AI-generated journaling prompt with space to write |
| `python app.py assess` | Stress level assessment with personalized recommendations |

### 🗣️ Chat Mode
Have a supportive conversation with an AI trained in evidence-based stress management techniques including Cognitive Behavioral Therapy (CBT), mindfulness, and positive psychology.

### 🌬️ Breathing Exercises
Choose from guided breathing techniques with real-time visual progress:
- **Box Breathing** (4-4-4-4): Used by Navy SEALs for stress reduction
- **4-7-8 Breathing**: A relaxation technique that promotes calm and sleep

### 📝 Journaling
Receive a thoughtful, AI-generated journaling prompt designed to encourage self-reflection, emotional processing, and gratitude.

### 📊 Stress Assessment
Answer a brief questionnaire and receive personalized, evidence-based recommendations for managing your stress level.

## Prerequisites

- Python 3.8+
- [Ollama](https://ollama.ai/) running locally with a model pulled (e.g., `ollama pull llama3.2`)

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Interactive chat session
python app.py chat

# Guided breathing exercise
python app.py breathe
python app.py breathe --technique box
python app.py breathe --technique 478

# Journaling prompt
python app.py journal

# Stress assessment
python app.py assess
```

## Testing

```bash
pytest test_app.py -v
```

## How It Works

The bot connects to a locally running LLM via Ollama. All processing happens on your machine — **no data is sent to external servers**. The LLM is instructed to use evidence-based therapeutic techniques and to always recommend professional help when appropriate.

## Mental Health Resources

- **988 Suicide & Crisis Lifeline**: Call or text 988
- **Crisis Text Line**: Text HOME to 741741
- **NAMI Helpline**: 1-800-950-NAMI (6264)
- **SAMHSA Helpline**: 1-800-662-4357
- **Psychology Today Therapist Finder**: https://www.psychologytoday.com/us/therapists

---

*This tool is for educational and wellness purposes only. Always consult a licensed mental health professional for clinical care.*
