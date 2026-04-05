"""
Streamlit Web UI for Code Translator.
Features: split pane (source/target), language selectors, translate button.
"""

import sys
import os
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from common.llm_client import chat, check_ollama_running

from .core import (
    load_config,
    detect_source_language,
    get_language_name,
    translate_code,
    validate_syntax,
    compare_codes,
    generate_translation_notes,
    SUPPORTED_LANGUAGES,
)

# Custom CSS for professional dark theme
st.set_page_config(page_title="Code Translator", page_icon="🎯", layout="wide")

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


def main():
    config = load_config()

    st.title("🔄 Code Translator")
    st.markdown("*Translate code between programming languages using a local LLM*")

    if not check_ollama_running():
        st.error("⚠️ Ollama is not running. Start it with: `ollama serve`")
        return

    # Language selectors
    lang_keys = list(SUPPORTED_LANGUAGES.keys())
    lang_names = [SUPPORTED_LANGUAGES[k]["name"] for k in lang_keys]

    col_s, col_t = st.columns(2)
    with col_s:
        source_idx = st.selectbox("Source Language", range(len(lang_keys)),
                                   format_func=lambda i: lang_names[i], index=0)
        source_lang = lang_keys[source_idx]
    with col_t:
        target_idx = st.selectbox("Target Language", range(len(lang_keys)),
                                   format_func=lambda i: lang_names[i], index=1)
        target_lang = lang_keys[target_idx]

    # Split pane
    col1, col2 = st.columns(2)

    with col1:
        st.subheader(f"📄 Source ({get_language_name(source_lang)})")
        source_code = st.text_area("Paste source code", height=400,
                                    placeholder="Paste your code here...")

        uploaded = st.file_uploader("Or upload a file", type=[info["ext"].lstrip(".") for info in SUPPORTED_LANGUAGES.values()])
        if uploaded:
            source_code = uploaded.read().decode("utf-8", errors="replace")
            detected = detect_source_language(uploaded.name)
            if detected:
                source_lang = detected
                st.info(f"Detected language: {get_language_name(detected)}")

    with col2:
        st.subheader(f"🔄 Target ({get_language_name(target_lang)})")
        result_placeholder = st.empty()

    # Translate button
    translate_btn = st.button("🚀 Translate", type="primary", use_container_width=True)

    if translate_btn and source_code:
        with st.spinner(f"Translating {get_language_name(source_lang)} → {get_language_name(target_lang)}..."):
            result = translate_code(source_code, source_lang, target_lang, chat, config)

        with col2:
            result_placeholder.markdown(result)

        # Comparison metrics
        comparison = compare_codes(source_code, result)
        st.subheader("📊 Translation Metrics")
        m1, m2, m3 = st.columns(3)
        m1.metric("Source Lines", comparison["source_lines"])
        m2.metric("Target Lines", comparison["target_lines"])
        m3.metric("Line Ratio", comparison["line_ratio"])

        # Validation
        validation = validate_syntax(source_code, source_lang)
        if not validation["valid"]:
            st.warning(f"⚠️ Source code syntax issues: {', '.join(validation['issues'])}")

    elif translate_btn:
        st.warning("Please paste or upload source code.")

    # Translation notes
    with st.expander("📝 Translation Notes"):
        if st.button("Generate Notes"):
            with st.spinner("Generating notes..."):
                notes_text = generate_translation_notes(source_lang, target_lang, chat)
            st.markdown(notes_text)


if __name__ == "__main__":
    main()
