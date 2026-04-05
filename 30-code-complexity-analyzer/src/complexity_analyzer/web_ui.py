"""
Streamlit Web UI for Code Complexity Analyzer.
Features: file uploader, metrics dashboard, charts, suggestions panel.
"""

import sys
import os
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from common.llm_client import chat, check_ollama_running

from .core import (
    load_config,
    analyze_file,
    get_llm_suggestions,
    save_trend,
    load_trends,
    analyze_dependencies,
)

st.set_page_config(page_title="📊 Code Complexity Analyzer", page_icon="📊", layout="wide")


def main():
    config = load_config()

    st.title("📊 Code Complexity Analyzer")
    st.markdown("*Analyze code complexity and get AI-powered improvement suggestions*")

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        cc_low = st.slider("CC Low Threshold", 1, 10, config.get("cc_threshold_low", 5))
        cc_high = st.slider("CC High Threshold", 5, 20, config.get("cc_threshold_high", 10))
        st.divider()

        st.header("📈 Trends")
        trends = load_trends(config.get("trends_file", "complexity_trends.json"))
        if trends:
            for fname, points in trends.items():
                latest = points[-1]
                st.caption(f"📄 {fname}: MI={latest['maintainability_index']}")
        else:
            st.caption("No trend data yet")

    # File input
    uploaded = st.file_uploader("📂 Upload Python file", type=["py"])

    if uploaded:
        source_code = uploaded.read().decode("utf-8", errors="replace")
        filepath = os.path.join(".", uploaded.name)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(source_code)

        # Analyze
        metrics = analyze_file(filepath)

        if "error" in metrics:
            st.error(f"Error parsing file: {metrics['error']}")
            return

        # Dashboard metrics
        st.subheader("📊 Metrics Dashboard")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Maintainability Index", f"{metrics['maintainability_index']}/100")
        col2.metric("Avg Cyclomatic", metrics["avg_cyclomatic"])
        col3.metric("Code Lines", metrics["lines"]["code"])
        col4.metric("Functions", len(metrics["functions"]))

        # Line counts
        st.subheader("📏 Line Breakdown")
        lines = metrics["lines"]
        line_data = {"Code": lines["code"], "Blank": lines["blank"], "Comments": lines["comments"]}
        st.bar_chart(line_data)

        # Function complexity chart
        if metrics["functions"]:
            st.subheader("🔍 Function Complexity")

            func_data = {
                "Function": [f["name"] for f in metrics["functions"]],
                "Cyclomatic": [f["cyclomatic"] for f in metrics["functions"]],
                "Cognitive": [f["cognitive"] for f in metrics["functions"]],
            }
            st.bar_chart(
                data={f["name"]: f["cyclomatic"] for f in metrics["functions"]},
            )

            # Detailed table
            for func in sorted(metrics["functions"], key=lambda x: x["cyclomatic"], reverse=True):
                rating = "🟢" if func["cyclomatic"] <= cc_low else ("🟡" if func["cyclomatic"] <= cc_high else "🔴")
                st.text(f"{rating} {func['name']} (line {func['lineno']}): CC={func['cyclomatic']}, Cognitive={func['cognitive']}, Args={func['args_count']}")

        # Dependencies
        if metrics.get("dependencies"):
            with st.expander("📦 Dependencies"):
                for dep in metrics["dependencies"]:
                    st.text(f"  • {dep}")

        # Source code
        with st.expander("📄 Source Code"):
            st.code(source_code, language="python")

        # AI Suggestions
        st.subheader("💡 AI Suggestions")
        if not check_ollama_running():
            st.warning("Ollama is not running. Start it for AI suggestions.")
        else:
            if st.button("🤖 Get AI Suggestions", type="primary"):
                with st.spinner("Analyzing with AI..."):
                    suggestions = get_llm_suggestions(filepath, metrics, chat, config)
                st.markdown(suggestions)

        # Track trends
        if st.button("📈 Save Trend Point"):
            save_trend(filepath, metrics, config.get("trends_file", "complexity_trends.json"))
            st.success("✅ Saved!")
            st.rerun()

        # Cleanup
        if os.path.exists(filepath) and filepath.startswith("."):
            os.remove(filepath)


if __name__ == "__main__":
    main()
