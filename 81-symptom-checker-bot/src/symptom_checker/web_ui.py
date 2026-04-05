"""
Symptom Checker Bot - Streamlit Web UI

A browser-based interface for symptom analysis with urgency scoring,
body-region mapping, and session history tracking.

⚠️ MEDICAL DISCLAIMER: For EDUCATIONAL and INFORMATIONAL purposes ONLY.
"""

import sys
import os

# Path setup for common module
_common_path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
sys.path.insert(0, os.path.abspath(_common_path))

try:
    import streamlit as st
except ImportError:
    print("ERROR: Streamlit is not installed. Install it with: pip install streamlit")
    print("Then run: streamlit run src/symptom_checker/web_ui.py")
    sys.exit(1)

from symptom_checker.core import (
    DISCLAIMER,
    SYMPTOM_DATABASE,
    URGENCY_LABELS,
    assess_urgency,
    get_body_regions,
    check_symptoms,
    MedicalHistoryTracker,
    check_ollama_running,
)

# Custom CSS for professional dark theme
st.set_page_config(page_title="Symptom Checker Bot", page_icon="🎯", layout="wide")

st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .stApp { background: linear-gradient(180deg, #0e1117 0%, #1a1a2e 100%); }
    h1 { background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.5rem !important; }
    h2 { color: #667eea !important; }
    h3 { color: #a78bfa !important; }
    .stButton>button { background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 8px; padding: 0.5rem 2rem; font-weight: 600; transition: transform 0.2s; }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4); }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea { background-color: #1a1a2e; border: 1px solid #333; color: #e0e0e0; border-radius: 8px; }
    .stSelectbox>div>div { background-color: #1a1a2e; border: 1px solid #333; }
    .stMetric { background: linear-gradient(135deg, #1a1a2e, #16213e); padding: 1rem; border-radius: 10px; border: 1px solid #333; }
    .css-1d391kg { background-color: #1a1a2e; }
    div[data-testid="stSidebar"] { background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%); }
    .stSuccess { background-color: rgba(102, 126, 234, 0.1); border: 1px solid #667eea; }
    footer { visibility: hidden; }
    .block-container { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

if "history" not in st.session_state:
    st.session_state.history = MedicalHistoryTracker()
if "conversation" not in st.session_state:
    st.session_state.conversation = []

# ---------------------------------------------------------------------------
# Top disclaimer banner
# ---------------------------------------------------------------------------

st.error(
    "⚠️ **MEDICAL DISCLAIMER** — This tool is for **EDUCATIONAL and INFORMATIONAL** "
    "purposes ONLY. It is **NOT** a substitute for professional medical advice, "
    "diagnosis, or treatment. **ALWAYS** consult a qualified healthcare provider. "
    "Call emergency services (911) for medical emergencies."
)

st.title("🏥 Symptom Checker Bot")
st.caption("AI-powered symptom analysis for educational purposes only")

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.header("⚙️ Options")

    # Body region filter
    selected_regions = st.multiselect(
        "Filter by body region",
        options=list(SYMPTOM_DATABASE.keys()),
        default=list(SYMPTOM_DATABASE.keys()),
        format_func=lambda r: f"{r.capitalize()} - {SYMPTOM_DATABASE[r]['description']}",
    )

    # Build symptom options from selected regions
    available_symptoms: list[str] = []
    for region in selected_regions:
        available_symptoms.extend(SYMPTOM_DATABASE[region]["symptoms"])
    available_symptoms = sorted(set(available_symptoms))

    selected_symptoms = st.multiselect(
        "Select known symptoms",
        options=available_symptoms,
    )

    st.divider()

    show_history = st.checkbox("Show session history", value=True)

    st.divider()
    st.subheader("📊 Urgency Legend")
    for level in sorted(URGENCY_LABELS.keys()):
        label, advice = URGENCY_LABELS[level]
        st.write(f"**{label}** — {advice}")

# ---------------------------------------------------------------------------
# Main area
# ---------------------------------------------------------------------------

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("💬 Describe Your Symptoms")

    custom_text = st.text_area(
        "Enter additional symptom details (free text):",
        height=120,
        placeholder="e.g., I've had a persistent headache for 3 days with mild fever...",
    )

    # Combine selected and typed symptoms
    combined_symptoms = ", ".join(selected_symptoms)
    if custom_text.strip():
        combined_symptoms = f"{combined_symptoms}, {custom_text.strip()}" if combined_symptoms else custom_text.strip()

    analyze_clicked = st.button("🔍 Analyze Symptoms", type="primary", disabled=not combined_symptoms)

with col2:
    st.subheader("📊 Urgency Meter")

    if combined_symptoms:
        level, label, advice = assess_urgency(combined_symptoms)
        regions = get_body_regions(combined_symptoms)

        # Color mapping
        color_map = {1: "green", 2: "yellow", 3: "orange", 4: "red", 5: "red"}
        meter_color = color_map.get(level, "gray")

        st.metric("Urgency Level", label.split(" ", 1)[-1], delta=None)
        st.progress(level / 5)

        if level >= 4:
            st.error(f"**{label}**: {advice}")
        elif level >= 3:
            st.warning(f"**{label}**: {advice}")
        else:
            st.info(f"**{label}**: {advice}")

        st.write("**Affected regions:**")
        for r in regions:
            desc = SYMPTOM_DATABASE.get(r, {}).get("description", r)
            st.write(f"- 🗺️ **{r.capitalize()}** — {desc}")
    else:
        st.info("Enter symptoms to see urgency assessment")

# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

if analyze_clicked and combined_symptoms:
    st.divider()
    st.subheader("🩺 AI Analysis")

    if not check_ollama_running():
        st.error(
            "❌ **Ollama is not running.** Please start Ollama first with `ollama serve` "
            "and ensure the model is available (`ollama pull gemma4`)."
        )
    else:
        with st.spinner("Analyzing symptoms with AI..."):
            try:
                response = check_symptoms(combined_symptoms, st.session_state.conversation)
                st.markdown(response)

                # Update conversation and history
                st.session_state.conversation.append({"role": "user", "content": combined_symptoms})
                st.session_state.conversation.append({"role": "assistant", "content": response})

                level, label, advice = assess_urgency(combined_symptoms)
                regions = get_body_regions(combined_symptoms)
                st.session_state.history.add_entry(combined_symptoms, level, regions, response)

            except Exception as exc:
                st.error(f"❌ Analysis failed: {exc}")

# ---------------------------------------------------------------------------
# History
# ---------------------------------------------------------------------------

if show_history:
    entries = st.session_state.history.get_history()
    if entries:
        st.divider()
        st.subheader("📋 Session History")
        for i, entry in enumerate(reversed(entries), 1):
            urgency_label = URGENCY_LABELS.get(entry["urgency"], ("?", ""))[0]
            with st.expander(
                f"Check #{len(entries) - i + 1} — {urgency_label} — "
                f"{entry['symptoms'][:80]}{'...' if len(entry['symptoms']) > 80 else ''}"
            ):
                st.write(f"**Time:** {entry['timestamp'][:19]}")
                st.write(f"**Urgency:** {urgency_label}")
                st.write(f"**Regions:** {', '.join(entry['regions'])}")
                st.markdown(entry["response"])

# ---------------------------------------------------------------------------
# Bottom disclaimer banner
# ---------------------------------------------------------------------------

st.divider()
st.warning(
    "⚠️ **REMINDER** — All information provided by this tool is for **EDUCATIONAL "
    "purposes ONLY**. This is NOT medical advice. Always consult a qualified healthcare "
    "professional for any health concerns. If you are experiencing a medical emergency, "
    "**call emergency services immediately**."
)

st.caption("Part of the 90 Local LLM Projects collection • Powered by Ollama")
