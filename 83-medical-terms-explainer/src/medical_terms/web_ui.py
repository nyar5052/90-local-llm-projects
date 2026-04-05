"""
Medical Terms Explainer — Streamlit Web UI.

⚠️  DISCLAIMER: This tool is for EDUCATIONAL PURPOSES ONLY and does NOT provide
medical advice. Always consult a qualified healthcare professional for medical
questions or concerns.
"""

import sys
import os

# Ensure the project root and src are on the path so imports work when run via
# ``streamlit run src/medical_terms/web_ui.py``
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
_src_root = os.path.join(_project_root, 'src')
if _src_root not in sys.path:
    sys.path.insert(0, _src_root)

import streamlit as st

from medical_terms.core import (
    DISCLAIMER,
    MEDICAL_ABBREVIATIONS,
    PRONUNCIATION_GUIDE,
    check_ollama_running,
    decode_abbreviation,
    explain_term,
    get_pronunciation,
    get_related_conditions,
    get_visual_aid,
    search_abbreviations,
)

# ---------------------------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Medical Terms Explainer",
    page_icon="📚",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Session State Initialisation
# ---------------------------------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = []
if "bookmarks" not in st.session_state:
    st.session_state.bookmarks = []

# ---------------------------------------------------------------------------
# Disclaimer Banner (always visible)
# ---------------------------------------------------------------------------
st.error(
    "⚠️  **MEDICAL DISCLAIMER** — This tool is for **EDUCATIONAL PURPOSES ONLY**. "
    "It does **NOT** provide medical advice, diagnosis, or treatment recommendations. "
    "**ALWAYS** consult a qualified healthcare professional for any medical questions or concerns.",
    icon="🚨",
)

st.title("📚 Medical Terms Explainer")

# ---------------------------------------------------------------------------
# Sidebar — History & Bookmarks
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("📋 Recently Searched")
    if st.session_state.history:
        for h in reversed(st.session_state.history[-10:]):
            st.markdown(f"- {h}")
    else:
        st.caption("No searches yet.")

    st.divider()

    st.header("🔖 Bookmarks")
    if st.session_state.bookmarks:
        for b in st.session_state.bookmarks:
            st.markdown(f"- {b}")
        if st.button("Clear Bookmarks"):
            st.session_state.bookmarks = []
            st.rerun()
    else:
        st.caption("No bookmarks yet.")

    st.divider()
    st.caption(DISCLAIMER)

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tab_explain, tab_abbrev, tab_pronounce = st.tabs([
    "📖 Term Explainer",
    "🔤 Abbreviation Decoder",
    "🗣️ Pronunciation Guide",
])

# ========================== Tab 1: Term Explainer ==========================
with tab_explain:
    st.subheader("Explain a Medical Term")

    col1, col2 = st.columns([3, 1])
    with col1:
        term_input = st.text_input(
            "Enter a medical term",
            placeholder="e.g. hypertension, tachycardia, edema",
            key="term_input",
        )
    with col2:
        detail_level = st.radio(
            "Detail level",
            options=["brief", "standard", "comprehensive"],
            index=1,
            key="detail_level",
        )

    if st.button("Explain", type="primary", key="btn_explain"):
        if not term_input.strip():
            st.warning("Please enter a medical term.")
        elif not check_ollama_running():
            st.error("Ollama is not running. Please start Ollama first (`ollama serve`).")
        else:
            term = term_input.strip()
            # Add to history
            if term not in st.session_state.history:
                st.session_state.history.append(term)

            with st.spinner(f"Looking up '{term}'..."):
                try:
                    explanation = explain_term(term, detail_level)
                except Exception as exc:
                    st.error(f"Error: {exc}")
                    explanation = None

            if explanation:
                st.markdown("---")
                st.markdown(f"### 📖 {term}")

                # Term card
                st.markdown(explanation)

                # Extras
                cols = st.columns(3)
                pron = get_pronunciation(term)
                if pron:
                    with cols[0]:
                        st.info(f"🗣️ **Pronunciation:** {pron}")

                visual = get_visual_aid(term)
                if visual:
                    with cols[1]:
                        st.info(f"🖼️ **Visual Aid:** {visual}")

                related = get_related_conditions(term)
                if related:
                    with cols[2]:
                        st.info(f"🔗 **Related:** {', '.join(related)}")

                # Bookmark button
                if term not in st.session_state.bookmarks:
                    if st.button(f"🔖 Bookmark '{term}'", key=f"bm_{term}"):
                        st.session_state.bookmarks.append(term)
                        st.rerun()

                st.markdown("---")
                st.warning(DISCLAIMER)

# ===================== Tab 2: Abbreviation Decoder ========================
with tab_abbrev:
    st.subheader("🔤 Medical Abbreviation Decoder")

    abbrev_input = st.text_input(
        "Enter an abbreviation",
        placeholder="e.g. CBC, MRI, STAT",
        key="abbrev_input",
    )

    col_a, col_b = st.columns(2)

    with col_a:
        if st.button("Decode", type="primary", key="btn_decode"):
            if abbrev_input.strip():
                meaning = decode_abbreviation(abbrev_input.strip())
                if meaning:
                    st.success(f"**{abbrev_input.strip()}** → {meaning}")
                else:
                    st.warning(f"'{abbrev_input.strip()}' not found. Try searching below.")
            else:
                st.warning("Please enter an abbreviation.")

    with col_b:
        search_query = st.text_input(
            "Search abbreviations",
            placeholder="e.g. blood, heart, therapy",
            key="abbrev_search",
        )
        if search_query.strip():
            results = search_abbreviations(search_query.strip())
            if results:
                for k, v in sorted(results.items()):
                    st.markdown(f"- **{k}** → {v}")
            else:
                st.info("No matches found.")

    st.divider()
    st.subheader("📋 All Abbreviations")

    # Display full table
    table_data = [
        {"Abbreviation": k, "Meaning": v}
        for k, v in sorted(MEDICAL_ABBREVIATIONS.items())
    ]
    st.dataframe(table_data, use_container_width=True, hide_index=True)

# ===================== Tab 3: Pronunciation Guide =========================
with tab_pronounce:
    st.subheader("🗣️ Pronunciation Guide")

    pron_input = st.text_input(
        "Enter a medical term",
        placeholder="e.g. arrhythmia, dyspnea, tachycardia",
        key="pron_input",
    )

    if st.button("Look Up", type="primary", key="btn_pronounce"):
        if pron_input.strip():
            result = get_pronunciation(pron_input.strip())
            if result:
                st.success(f"**{pron_input.strip()}** → {result}")
            else:
                st.warning(f"Pronunciation for '{pron_input.strip()}' not found in our database.")
        else:
            st.warning("Please enter a term.")

    st.divider()
    st.subheader("📋 Full Pronunciation Guide")

    pron_data = [
        {"Term": k, "Pronunciation": v}
        for k, v in sorted(PRONUNCIATION_GUIDE.items())
    ]
    st.dataframe(pron_data, use_container_width=True, hide_index=True)
