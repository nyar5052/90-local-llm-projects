"""Streamlit web interface for Regex Gen."""

import sys
import os
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

import streamlit as st

from .config import load_config, REGEX_FLAVORS, PATTERN_LIBRARY
from .core import generate_regex, explain_regex
from .utils import run_regex_test, validate_regex, highlight_matches


def run():
    """Launch the Streamlit web UI."""
    # Custom CSS for professional dark theme
    st.set_page_config(page_title="Regex Generator", page_icon="🎯", layout="wide")

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

    st.markdown("# 🔤 Regex Generator")
    st.markdown("*Generate, explain, and test regular expressions with AI*")
    st.divider()

    config = load_config()

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        config.model = st.text_input("Model", value=config.model)
        config.temperature = st.slider("Temperature", 0.0, 1.0, config.temperature, 0.1)
        flavor = st.selectbox("Regex Flavor", REGEX_FLAVORS, index=0)

        st.subheader("📚 Pattern Library")
        selected_pattern = st.selectbox("Quick Patterns", ["(none)"] + list(PATTERN_LIBRARY.keys()))
        if selected_pattern != "(none)":
            st.code(PATTERN_LIBRARY[selected_pattern])

    # Tabs
    tab_gen, tab_explain, tab_test = st.tabs(["✨ Generate", "📖 Explain", "🧪 Test"])

    with tab_gen:
        description = st.text_input(
            "Describe what you want to match:",
            placeholder="email addresses, phone numbers, URLs, etc.",
        )

        test_strings_input = st.text_area(
            "Test strings (one per line):",
            placeholder="user@example.com\ninvalid-email\ntest@test.co",
            height=100,
        )

        if st.button("✨ Generate Regex", type="primary", use_container_width=True):
            if not description.strip():
                st.warning("Please describe what you want to match.")
            else:
                with st.spinner("✨ Generating regex..."):
                    result = generate_regex(description, flavor, config)

                st.markdown("### 🎯 Generated Regex")
                st.markdown(result["explanation"])

                if result.get("primary_pattern") and test_strings_input.strip():
                    strings = [s.strip() for s in test_strings_input.splitlines() if s.strip()]
                    _show_test_results_st(result["primary_pattern"], strings)

    with tab_explain:
        pattern = st.text_input(
            "Enter regex pattern to explain:",
            placeholder=r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        )

        if selected_pattern != "(none)":
            if st.button(f"📚 Explain '{selected_pattern}' from library"):
                pattern = PATTERN_LIBRARY[selected_pattern]

        if st.button("📖 Explain Pattern", type="primary", use_container_width=True):
            if not pattern.strip():
                st.warning("Please enter a regex pattern.")
            else:
                val = validate_regex(pattern)
                if val["valid"]:
                    st.success(f"✅ Valid pattern ({val.get('groups', 0)} groups)")
                else:
                    st.error(f"❌ Invalid pattern: {val.get('error')}")

                with st.spinner("📖 Analyzing..."):
                    result = explain_regex(pattern, config)
                st.markdown("### 📖 Explanation")
                st.markdown(result["explanation"])

    with tab_test:
        test_pattern = st.text_input("Regex Pattern:", key="test_pattern", placeholder=r"\d+")
        test_input = st.text_area(
            "Test strings (one per line):",
            key="test_input",
            height=200,
            placeholder="abc123\nhello\n42",
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🧪 Test Pattern", type="primary", use_container_width=True):
                if test_pattern and test_input.strip():
                    strings = [s.strip() for s in test_input.splitlines() if s.strip()]
                    _show_test_results_st(test_pattern, strings)
                else:
                    st.warning("Enter both a pattern and test strings.")

        with col2:
            if st.button("📋 Validate Only"):
                if test_pattern:
                    val = validate_regex(test_pattern)
                    if val["valid"]:
                        st.success(f"✅ Valid ({val.get('groups', 0)} capture groups)")
                    else:
                        st.error(f"❌ Invalid: {val.get('error')}")


def _show_test_results_st(pattern: str, strings: list[str]):
    """Display test results in Streamlit."""
    results = run_regex_test(pattern, strings)
    st.markdown("### 🧪 Test Results")
    for r in results:
        if r.get("error"):
            st.error(f"Error: {r['error']}")
            return
        icon = "✅" if r.get("matches") else "❌"
        match_info = f" → `{r.get('match_text')}`" if r.get("match_text") else ""
        st.markdown(f"{icon} `{r['string']}`{match_info}")


if __name__ == "__main__":
    run()
