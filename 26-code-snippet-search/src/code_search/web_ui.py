"""
Streamlit Web UI for Code Snippet Search.
Features: search box, syntax-highlighted results, bookmarks panel.
"""

import sys
import os
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from common.llm_client import chat, check_ollama_running

from .core import (
    load_config,
    scan_directory,
    search_code,
    rank_files,
    detect_language,
    load_bookmarks,
    save_bookmark,
    remove_bookmark,
)

# Custom CSS for professional dark theme
st.set_page_config(page_title="Code Snippet Search", page_icon="🎯", layout="wide")

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

    st.title("🔎 Code Snippet Search")
    st.markdown("*Search your codebase with natural language queries powered by local LLM*")

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        directory = st.text_input("📁 Directory to search", value=os.getcwd())
        max_files = st.slider("Max files to index", 10, 500, config.get("max_files", 100))
        st.divider()

        st.header("⭐ Bookmarks")
        bookmarks = load_bookmarks(config.get("bookmarks_file", "bookmarks.json"))
        if bookmarks:
            for i, bm in enumerate(bookmarks):
                col1, col2 = st.columns([4, 1])
                with col1:
                    if st.button(f"🔍 {bm.get('query', '')[:30]}", key=f"bm_{i}"):
                        st.session_state["search_query"] = bm.get("query", "")
                with col2:
                    if st.button("🗑️", key=f"rm_bm_{i}"):
                        remove_bookmark(i, config.get("bookmarks_file", "bookmarks.json"))
                        st.rerun()
        else:
            st.caption("No bookmarks yet")

    # Check Ollama
    if not check_ollama_running():
        st.error("⚠️ Ollama is not running. Start it with: `ollama serve`")
        return

    # Search
    col1, col2 = st.columns([5, 1])
    with col1:
        query = st.text_input(
            "🔍 Search query",
            value=st.session_state.get("search_query", ""),
            placeholder="e.g., 'authentication logic', 'database connection handling'",
        )
    with col2:
        st.write("")
        st.write("")
        search_btn = st.button("🔎 Search", type="primary", use_container_width=True)

    if search_btn and query and os.path.isdir(directory):
        with st.spinner("📂 Indexing files..."):
            files = scan_directory(directory, max_files=max_files)

        if not files:
            st.warning("No code files found in the specified directory.")
            return

        st.info(f"📊 Indexed **{len(files)}** files")

        with st.expander("📁 Indexed Files", expanded=False):
            for f in files[:30]:
                st.text(f"  {f['path']} ({f['language']}, {f['lines']} lines)")

        with st.spinner("🔍 Searching with AI..."):
            result = search_code(directory, query, chat, config)

        st.subheader("🎯 Search Results")
        st.markdown(result)

        # Bookmark button
        if st.button("⭐ Bookmark this search"):
            save_bookmark(
                {"query": query, "directory": directory, "result_preview": result[:200]},
                config.get("bookmarks_file", "bookmarks.json"),
            )
            st.success("✅ Bookmarked!")
            st.rerun()

        # Show matching files with syntax highlighting
        ranked = rank_files(files, query)
        if ranked:
            st.subheader("📄 Top Matching Files")
            for f in ranked[:5]:
                with st.expander(f"📄 {f['path']} ({f['language']}, {f['lines']} lines)"):
                    st.code(f["content"][:3000], language=f["language"])

    elif search_btn and not os.path.isdir(directory):
        st.error(f"Directory not found: {directory}")


if __name__ == "__main__":
    main()
