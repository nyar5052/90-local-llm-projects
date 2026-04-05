"""
Drug Interaction Checker - Streamlit Web UI

⚠️ DISCLAIMER: This tool is for EDUCATIONAL and INFORMATIONAL purposes only.
It is NOT a substitute for professional medical or pharmacological advice.
Always consult a qualified healthcare provider or pharmacist before making
any decisions about your medications.
"""

import streamlit as st
import sys
import os

# Path setup for shared common module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.drug_checker.core import (  # noqa: E402
    DISCLAIMER,
    SEVERITY_LEVELS,
    check_interactions,
    check_ollama_running,
    classify_severity,
    get_alternatives,
    get_dosage_notes,
    get_food_interactions,
    parse_medications,
    FOOD_INTERACTIONS,
    DOSAGE_NOTES,
    COMMON_ALTERNATIVES,
)

# ---------------------------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="💊 Drug Interaction Checker",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# ⚠️  PROMINENT DISCLAIMER BANNER  ⚠️
# ---------------------------------------------------------------------------
st.error(
    "⚠️ **IMPORTANT MEDICAL DISCLAIMER** ⚠️\n\n"
    "This tool is for **EDUCATIONAL and INFORMATIONAL purposes ONLY**. "
    "It is **NOT** a substitute for professional medical or pharmacological advice. "
    "**ALWAYS** consult a qualified healthcare provider or pharmacist. "
    "**NEVER** start, stop, or change medications based on this tool's output."
)

st.title("💊 Drug Interaction Checker")
st.caption("AI-powered medication interaction analysis using local LLMs")

# ---------------------------------------------------------------------------
# Session State
# ---------------------------------------------------------------------------
if "medications" not in st.session_state:
    st.session_state.medications = []
if "interaction_result" not in st.session_state:
    st.session_state.interaction_result = ""

# ---------------------------------------------------------------------------
# Sidebar - Medication Input
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("📋 Medication List")

    st.warning(
        "⚠️ For educational purposes only. "
        "Always consult a pharmacist."
    )

    meds_input = st.text_area(
        "Enter medications (one per line or comma-separated):",
        placeholder="aspirin\nibuprofen\nwarfarin",
        height=150,
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Set Medications", use_container_width=True):
            if meds_input.strip():
                # Support both newline and comma separated
                raw = meds_input.replace("\n", ",")
                st.session_state.medications = parse_medications(raw)
                st.session_state.interaction_result = ""
                st.rerun()
    with col2:
        if st.button("🗑️ Clear All", use_container_width=True):
            st.session_state.medications = []
            st.session_state.interaction_result = ""
            st.rerun()

    if st.session_state.medications:
        st.divider()
        st.subheader("Current Medications")
        for i, med in enumerate(st.session_state.medications):
            col_med, col_del = st.columns([4, 1])
            with col_med:
                st.write(f"**{i + 1}.** {med}")
            with col_del:
                if st.button("✖", key=f"del_{i}"):
                    st.session_state.medications.pop(i)
                    st.session_state.interaction_result = ""
                    st.rerun()

    st.divider()
    st.markdown(
        "**Severity Legend:**\n"
        "- 🚫 Contraindicated\n"
        "- 🔴 Major\n"
        "- 🟡 Moderate\n"
        "- 🟢 Minor\n"
        "- ✅ None"
    )

# ---------------------------------------------------------------------------
# Main Content - Tabs
# ---------------------------------------------------------------------------
tab_interactions, tab_food, tab_dosage, tab_alternatives = st.tabs([
    "💊 Drug Interactions",
    "🍎 Food Interactions",
    "📋 Dosage Notes",
    "💡 Alternatives",
])

# ---- Tab 1: Drug Interactions ----
with tab_interactions:
    st.header("Drug-Drug Interaction Analysis")

    if not st.session_state.medications:
        st.info("👈 Add medications in the sidebar to begin.")
    elif len(st.session_state.medications) < 2:
        st.warning("Please add at least **2 medications** to check for interactions.")
    else:
        # Show current medications
        st.write("**Checking interactions for:**")
        cols = st.columns(min(len(st.session_state.medications), 5))
        for i, med in enumerate(st.session_state.medications):
            with cols[i % len(cols)]:
                st.metric(label=f"Med {i + 1}", value=med.title())

        if st.button("🔍 Check Interactions", type="primary", use_container_width=True):
            if not check_ollama_running():
                st.error("❌ Ollama is not running. Please start Ollama first: `ollama serve`")
            else:
                with st.spinner("Analysing interactions... This may take a moment."):
                    try:
                        result = check_interactions(st.session_state.medications)
                        st.session_state.interaction_result = result
                    except Exception as e:
                        st.error(f"Error communicating with LLM: {e}")

        if st.session_state.interaction_result:
            result = st.session_state.interaction_result
            severity = classify_severity(result)
            sev_info = SEVERITY_LEVELS[severity]

            # Severity banner
            severity_colors = {
                "contraindicated": "error",
                "major": "error",
                "moderate": "warning",
                "minor": "success",
                "none": "success",
            }
            severity_method = getattr(st, severity_colors.get(severity, "info"))
            severity_method(
                f"{sev_info['emoji']} **Overall Severity: {severity.upper()}** — {sev_info['description']}"
            )

            st.markdown("---")
            st.markdown(result)

            st.markdown("---")
            st.caption(
                "⚠️ This analysis is for educational purposes only. "
                "ALWAYS consult a qualified healthcare provider or pharmacist."
            )

# ---- Tab 2: Food Interactions ----
with tab_food:
    st.header("🍎 Drug-Food Interactions")

    if not st.session_state.medications:
        st.info("👈 Add medications in the sidebar to see food interactions.")
    else:
        found_any = False
        for med in st.session_state.medications:
            foods = get_food_interactions(med)
            if foods:
                found_any = True
                st.subheader(f"🍽️ {med.title()}")
                for food_item in foods:
                    st.markdown(f"- ⚠️ {food_item}")
                st.markdown("")

        if not found_any:
            st.info(
                "No food interactions found in our database for the listed medications. "
                "This does **not** mean there are no food interactions — "
                "always consult a pharmacist."
            )

    st.divider()
    with st.expander("📖 View Full Food Interaction Database"):
        for drug, foods in FOOD_INTERACTIONS.items():
            st.markdown(f"**{drug.title()}**: {', '.join(foods)}")

# ---- Tab 3: Dosage Notes ----
with tab_dosage:
    st.header("📋 Dosage Information")

    st.warning(
        "⚠️ Dosage information is for **general reference only**. "
        "Your prescribed dosage may differ. NEVER change your dosage "
        "without consulting your healthcare provider."
    )

    if not st.session_state.medications:
        st.info("👈 Add medications in the sidebar to see dosage notes.")
    else:
        for med in st.session_state.medications:
            dosage = get_dosage_notes(med)
            if dosage:
                st.markdown(f"**💊 {med.title()}**: {dosage}")
            else:
                st.markdown(f"**💊 {med.title()}**: _No dosage info in database_")

    st.divider()
    with st.expander("📖 View Full Dosage Database"):
        for drug, note in DOSAGE_NOTES.items():
            st.markdown(f"**{drug.title()}**: {note}")

# ---- Tab 4: Alternatives ----
with tab_alternatives:
    st.header("💡 Alternative Medications")

    st.error(
        "🚨 **NEVER** switch medications without consulting your healthcare provider. "
        "These alternatives are listed for **informational purposes only**."
    )

    if not st.session_state.medications:
        st.info("👈 Add medications in the sidebar to see alternatives.")
    else:
        for med in st.session_state.medications:
            alts = get_alternatives(med)
            if alts:
                st.subheader(f"🔄 {med.title()}")
                for alt in alts:
                    alt_dosage = get_dosage_notes(alt)
                    label = f"**{alt.title()}**"
                    if alt_dosage:
                        label += f" — _{alt_dosage}_"
                    st.markdown(f"- {label}")
            else:
                st.markdown(f"**{med.title()}**: _No alternatives in database_")

    st.divider()
    with st.expander("📖 View Full Alternatives Database"):
        for drug, alts in COMMON_ALTERNATIVES.items():
            st.markdown(f"**{drug.title()}**: {', '.join(a.title() for a in alts)}")

# ---------------------------------------------------------------------------
# ⚠️  DISCLAIMER FOOTER  ⚠️
# ---------------------------------------------------------------------------
st.divider()
st.error(
    "⚠️ **REMINDER**: This tool is for **EDUCATIONAL and INFORMATIONAL purposes ONLY**. "
    "It is **NOT** a substitute for professional medical or pharmacological advice. "
    "**ALWAYS** consult a qualified healthcare provider or pharmacist before making "
    "any decisions about your medications. **NEVER** start, stop, or change medications "
    "based on this tool's output."
)
st.caption("Part of the 90 Local LLM Projects collection • Powered by Ollama + Gemma 4")
