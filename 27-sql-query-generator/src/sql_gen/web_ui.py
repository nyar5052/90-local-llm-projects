"""
Streamlit Web UI for SQL Query Generator.
Features: schema editor, NL input, generated SQL with syntax highlighting, history.
"""

import sys
import os
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from common.llm_client import chat, check_ollama_running

from .core import (
    load_config,
    parse_schema_text,
    visualize_schema,
    generate_sql,
    generate_sql_no_schema,
    optimize_query,
    load_history,
    save_to_history,
    SUPPORTED_DIALECTS,
)

st.set_page_config(page_title="🗃️ SQL Query Generator", page_icon="🗃️", layout="wide")


def main():
    config = load_config()

    st.title("🗃️ SQL Query Generator")
    st.markdown("*Convert natural language questions to SQL queries using a local LLM*")

    if not check_ollama_running():
        st.error("⚠️ Ollama is not running. Start it with: `ollama serve`")
        return

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        dialect = st.selectbox("SQL Dialect", SUPPORTED_DIALECTS, index=0)
        st.divider()

        st.header("📜 History")
        hist = load_history(config.get("history_file", "query_history.json"))
        if hist:
            for i, entry in enumerate(hist[-10:]):
                if st.button(f"🔄 {entry.get('query', '')[:30]}", key=f"hist_{i}"):
                    st.session_state["nl_query"] = entry.get("query", "")
        else:
            st.caption("No history yet")

    # Schema input
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Schema Definition")
        schema_text = st.text_area(
            "Paste your SQL schema here (optional)",
            height=250,
            placeholder="CREATE TABLE customers (\n  id INTEGER PRIMARY KEY,\n  name VARCHAR(100)\n);",
        )

        if schema_text:
            tables = parse_schema_text(schema_text)
            if tables:
                st.markdown("**Detected Tables:**")
                viz = visualize_schema(tables)
                st.code(viz, language="text")

    with col2:
        st.subheader("💬 Natural Language Query")
        query = st.text_area(
            "Describe what you want in plain English",
            value=st.session_state.get("nl_query", ""),
            height=100,
            placeholder="e.g., Show top 10 customers by total order amount",
        )

        generate_btn = st.button("🚀 Generate SQL", type="primary", use_container_width=True)

        if generate_btn and query:
            with st.spinner("🔄 Generating SQL..."):
                if schema_text:
                    result = generate_sql(schema_text, query, chat, dialect, config)
                else:
                    result = generate_sql_no_schema(query, chat, dialect, config)

            st.subheader("📝 Generated SQL")
            st.markdown(result)

            save_to_history(
                {"query": query, "dialect": dialect, "result_preview": result[:200]},
                config.get("history_file", "query_history.json"),
            )

            # Optimization
            with st.expander("💡 Optimization Suggestions"):
                if st.button("Analyze Query"):
                    with st.spinner("Analyzing..."):
                        suggestions = optimize_query(result, chat, dialect)
                    st.markdown(suggestions)

        elif generate_btn:
            st.warning("Please enter a query.")


if __name__ == "__main__":
    main()
