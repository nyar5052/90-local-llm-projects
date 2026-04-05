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

st.set_page_config(page_title="🧪 Unit Test Generator", page_icon="🧪", layout="wide")


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
