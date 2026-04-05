"""
Streamlit Web UI for Unit Test Generator.
Features: code input, generated tests, framework selector, download.
"""

import sys
import os
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from common.llm_client import chat, check_ollama_running

from .core import (
    load_config,
    extract_code_info,
    generate_tests,
    analyze_coverage,
    organize_test_structure,
    SUPPORTED_FRAMEWORKS,
)

# Custom CSS for professional dark theme
st.set_page_config(page_title="Unit Test Generator", page_icon="🎯", layout="wide")

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

    st.title("🧪 Unit Test Generator")
    st.markdown("*Generate comprehensive unit tests for Python code using a local LLM*")

    if not check_ollama_running():
        st.error("⚠️ Ollama is not running. Start it with: `ollama serve`")
        return

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        framework = st.selectbox("Testing Framework", SUPPORTED_FRAMEWORKS, index=0)
        st.divider()
        st.header("📊 Info")
        st.caption("Supports pytest and unittest frameworks")
        st.caption("Auto-detects edge cases and error handling")

    # Input
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📄 Source Code")

        uploaded = st.file_uploader("Upload Python file", type=["py"])
        source_code = ""
        filepath = None

        if uploaded:
            source_code = uploaded.read().decode("utf-8", errors="replace")
            # Write to temp-like location in project dir
            filepath = os.path.join(".", uploaded.name)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(source_code)
        else:
            source_code = st.text_area(
                "Or paste your Python code",
                height=400,
                placeholder="def add(a, b):\n    return a + b",
            )
            if source_code:
                filepath = os.path.join(".", "_temp_input.py")
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(source_code)

        if source_code:
            st.code(source_code, language="python")

    with col2:
        st.subheader("🧪 Generated Tests")

        if filepath and source_code:
            info = extract_code_info(filepath)
            coverage = analyze_coverage(info)

            # Show metrics
            m1, m2, m3 = st.columns(3)
            m1.metric("Functions", coverage["total_functions"])
            m2.metric("Methods", coverage["total_methods"])
            m3.metric("Edge Cases", coverage["edge_case_count"])

            if coverage["edge_cases_detected"]:
                st.caption(f"Detected: {', '.join(coverage['edge_cases_detected'])}")

            generate_btn = st.button("🚀 Generate Tests", type="primary", use_container_width=True)

            if generate_btn:
                with st.spinner(f"Generating {framework} tests..."):
                    result = generate_tests(filepath, chat, framework, config)

                st.markdown(result)

                # Download button
                st.download_button(
                    "📥 Download Tests",
                    data=result,
                    file_name=f"test_{os.path.splitext(os.path.basename(filepath))[0]}.py",
                    mime="text/x-python",
                )

                # Cleanup temp file
                if filepath.endswith("_temp_input.py") and os.path.exists(filepath):
                    os.remove(filepath)

    # Test structure suggestion
    if filepath and source_code:
        with st.expander("📁 Suggested Test Structure"):
            info = extract_code_info(filepath)
            structure = organize_test_structure(info)
            for tf in structure["test_files"]:
                st.text(f"📄 {tf['filename']}: {', '.join(tf['covers'])}")


if __name__ == "__main__":
    main()
