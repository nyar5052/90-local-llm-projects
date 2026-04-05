#!/usr/bin/env python3
"""Personal Knowledge Base - Streamlit Web Interface."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import streamlit as st


# Custom CSS for professional dark theme
st.set_page_config(page_title="Personal Knowledge Base", page_icon="🎯", layout="wide")

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

from knowledge_base.core import (
    add_note,
    delete_note,
    load_kb,
    search_notes,
    search_fulltext,
    get_all_tags,
    get_notes_by_tag,
    find_backlinks,
    get_note,
    get_templates,
    apply_template,
    export_notes,
    import_notes,
    config,
)
from common.llm_client import check_ollama_running

# ── Page config ──────────────────────────────────────────────────────────

# ── Sidebar navigation ──────────────────────────────────────────────────

st.sidebar.title("📚 Knowledge Base")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigate",
    ["Add Note", "Search", "Browse", "Tags", "Backlinks", "Templates", "Export / Import"],
    index=0,
)

# ── Helper ───────────────────────────────────────────────────────────────


def _reload_kb():
    """Force reload of the knowledge base (clear any cached data)."""
    return load_kb()


# ── Add Note ─────────────────────────────────────────────────────────────

if page == "Add Note":
    st.header("📝 Add Note")

    # Template selector
    templates = get_templates()
    template_names = ["(none)"] + list(templates.keys())
    selected_template = st.selectbox("Start from template", template_names)

    default_title = ""
    default_content = ""
    if selected_template != "(none)":
        tpl = templates[selected_template]
        default_title = tpl["title"]
        default_content = tpl["content"]

    title = st.text_input("Title", value=default_title)
    content = st.text_area("Content", value=default_content, height=300)
    tags_input = st.text_input("Tags (comma-separated)")

    if st.button("💾 Save Note", type="primary"):
        if not title.strip():
            st.error("Title is required.")
        else:
            tag_list = [t.strip() for t in tags_input.split(',') if t.strip()]
            note = add_note(title.strip(), content.strip(), tag_list)
            st.success(f"✅ Note #{note['id']} saved: {title}")

# ── Search ───────────────────────────────────────────────────────────────

elif page == "Search":
    st.header("🔍 Search")

    search_type = st.radio("Search mode", ["Full-text (fast)", "AI Semantic (LLM)"], horizontal=True)
    query = st.text_input("Search query")

    if st.button("Search", type="primary") and query.strip():
        if search_type == "Full-text (fast)":
            results = search_fulltext(query)
            if results:
                st.success(f"Found {len(results)} result(s)")
                for note in results:
                    with st.expander(f"#{note['id']} – {note['title']}", expanded=True):
                        st.markdown(f"**Tags:** {', '.join(note.get('tags', [])) or 'none'}")
                        st.markdown(note["content"])
            else:
                st.warning("No matching notes found.")
        else:
            if not check_ollama_running():
                st.error("Ollama is not running. Start it with: `ollama serve`")
            else:
                with st.spinner("Searching with AI..."):
                    result = search_notes(query)
                st.markdown(result)

# ── Browse ───────────────────────────────────────────────────────────────

elif page == "Browse":
    st.header("📖 Browse Notes")
    kb = _reload_kb()
    notes = kb["notes"]

    if not notes:
        st.info("Knowledge base is empty. Add some notes first!")
    else:
        st.write(f"**{len(notes)}** note(s) in your knowledge base")

        for note in reversed(notes):
            with st.expander(f"#{note['id']} – {note['title']}"):
                st.markdown(f"**Tags:** {', '.join(note.get('tags', [])) or 'none'}")
                st.markdown(f"**Created:** {note.get('created', 'N/A')}")
                st.markdown("---")
                st.markdown(note["content"])

                if st.button(f"🗑️ Delete note #{note['id']}", key=f"del_{note['id']}"):
                    delete_note(note["id"])
                    st.success(f"Note #{note['id']} deleted.")
                    st.rerun()

# ── Tags ─────────────────────────────────────────────────────────────────

elif page == "Tags":
    st.header("🏷️ Tag Browser")
    all_tags = get_all_tags()

    if not all_tags:
        st.info("No tags found. Add tags when creating notes.")
    else:
        cols = st.columns(min(len(all_tags), 4))
        for idx, (tag, count) in enumerate(sorted(all_tags.items(), key=lambda x: -x[1])):
            with cols[idx % len(cols)]:
                st.metric(label=tag, value=count)

        st.markdown("---")
        selected_tag = st.selectbox("Filter by tag", list(all_tags.keys()))
        if selected_tag:
            tag_notes = get_notes_by_tag(selected_tag)
            for note in tag_notes:
                with st.expander(f"#{note['id']} – {note['title']}"):
                    st.markdown(note["content"])

# ── Backlinks ────────────────────────────────────────────────────────────

elif page == "Backlinks":
    st.header("🔗 Backlinks")
    kb = _reload_kb()
    notes = kb["notes"]

    if not notes:
        st.info("No notes yet.")
    else:
        note_options = {f"#{n['id']} – {n['title']}": n["id"] for n in notes}
        selected = st.selectbox("Select a note", list(note_options.keys()))

        if selected:
            note_id = note_options[selected]
            links = find_backlinks(note_id)
            if links:
                st.success(f"{len(links)} note(s) reference this note")
                for link in links:
                    with st.expander(f"#{link['id']} – {link['title']}"):
                        st.markdown(link["content"])
            else:
                st.info("No backlinks found for this note.")

# ── Templates ────────────────────────────────────────────────────────────

elif page == "Templates":
    st.header("📝 Note Templates")
    templates = get_templates()

    for name, tpl in templates.items():
        with st.expander(f"**{name}**", expanded=False):
            st.markdown(f"**Title pattern:** `{tpl['title']}`")
            st.markdown("**Content:**")
            st.code(tpl["content"], language="markdown")

# ── Export / Import ──────────────────────────────────────────────────────

elif page == "Export / Import":
    st.header("📦 Export / Import")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Export")
        if st.button("📤 Export to Markdown", type="primary"):
            path = export_notes()
            st.success(f"✅ Exported to: {path}")
            with open(path, 'r', encoding='utf-8') as f:
                st.download_button("⬇️ Download", f.read(), file_name="knowledge_base_export.md")

    with col2:
        st.subheader("Import")
        uploaded = st.file_uploader("Upload Markdown export", type=["md"])
        if uploaded is not None:
            import tempfile
            temp_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', '_import_temp.md')
            with open(temp_path, 'wb') as tmp:
                tmp.write(uploaded.getbuffer())
            try:
                count = import_notes(temp_path)
                st.success(f"✅ Imported {count} note(s)")
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
