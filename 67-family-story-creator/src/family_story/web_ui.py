#!/usr/bin/env python3
"""Family Story Creator - Streamlit Web UI."""

import sys
import os
import streamlit as st


# Custom CSS for professional dark theme
st.set_page_config(page_title="Family Story Creator", page_icon="🎯", layout="wide")

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

# Ensure project root is on path for LLM client
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from .core import (
    STORY_STYLES,
    load_config,
    load_stories,
    save_story,
    delete_story,
    create_character,
    create_story,
    create_chapter,
    create_book,
    continue_story,
    create_poem,
    export_story,
)

CONFIG_PATH = os.environ.get("FAMILY_STORY_CONFIG", "config.yaml")


def get_config():
    """Load and cache config."""
    if "config" not in st.session_state:
        st.session_state.config = load_config(CONFIG_PATH)
    return st.session_state.config


def story_creator_page():
    """Story Creator page."""
    st.header("✍️ Story Creator")
    cfg = get_config()

    with st.form("story_form"):
        col1, col2 = st.columns(2)
        with col1:
            name1 = st.text_input("Member 1 Name", placeholder="e.g. Mom")
            age1 = st.number_input("Member 1 Age", min_value=0, max_value=150, value=0, step=1)
            rel1 = st.text_input("Member 1 Relationship", placeholder="e.g. mother")
        with col2:
            name2 = st.text_input("Member 2 Name", placeholder="e.g. Dad")
            age2 = st.number_input("Member 2 Age", min_value=0, max_value=150, value=0, step=1)
            rel2 = st.text_input("Member 2 Relationship", placeholder="e.g. father")

        extra_members = st.text_input("Additional Members (comma-separated)", placeholder="e.g. Sam, Emma, Grandma")
        event = st.text_area("Event Description", placeholder="Describe the family event or memory...")
        style = st.selectbox("Story Style", list(STORY_STYLES.keys()), index=0)
        photos = st.text_area("Photo Descriptions (optional)", placeholder="Describe any photos you want woven into the story...")
        length = st.selectbox("Story Length", ["short", "medium", "long"], index=1)
        submitted = st.form_submit_button("📖 Generate Story", type="primary")

    if submitted and event:
        members_list = []
        if name1:
            members_list.append(create_character(name1, age1 if age1 > 0 else None, "", rel1))
        if name2:
            members_list.append(create_character(name2, age2 if age2 > 0 else None, "", rel2))
        if extra_members:
            for m in extra_members.split(","):
                m = m.strip()
                if m:
                    members_list.append(create_character(m))

        if not members_list:
            st.error("Please add at least one family member.")
            return

        with st.spinner("Crafting your family story..."):
            story_text = create_story(
                members=members_list, event=event, style=style,
                photos=photos, length=length, config=cfg,
            )

        st.session_state["last_story"] = story_text
        st.session_state["last_story_meta"] = {
            "members": ", ".join(m["name"] for m in members_list),
            "event": event, "style": style,
        }
        st.markdown(story_text)

        col_save, col_export = st.columns(2)
        with col_save:
            if st.button("💾 Save Story"):
                meta = st.session_state["last_story_meta"]
                saved = save_story({**meta, "story": story_text}, cfg.get("stories_file"))
                st.success(f"Story saved! (id: {saved['id']})")
        with col_export:
            fmt = st.selectbox("Export Format", ["markdown", "html"], key="export_fmt")
            if st.button("📤 Export"):
                meta = st.session_state["last_story_meta"]
                exported = export_story({**meta, "story": story_text}, format=fmt)
                st.download_button(f"Download .{fmt[:4]}", exported, file_name=f"story.{'md' if fmt == 'markdown' else 'html'}")


def chapter_builder_page():
    """Chapter Builder page."""
    st.header("📚 Chapter Builder")
    cfg = get_config()

    book_title = st.text_input("Book Title", placeholder="e.g. Our Family Adventures")
    members = st.text_input("Family Members", placeholder="e.g. Mom, Dad, Sam, Emma")

    if "chapters" not in st.session_state:
        st.session_state.chapters = []

    st.subheader("Add Chapter")
    with st.form("add_chapter"):
        ch_title = st.text_input("Chapter Title")
        ch_events = st.text_area("Chapter Events")
        add = st.form_submit_button("➕ Add Chapter")
        if add and ch_title:
            st.session_state.chapters.append({"title": ch_title, "events": ch_events})
            st.success(f"Added: {ch_title}")

    if st.session_state.chapters:
        st.subheader("Chapters")
        for i, ch in enumerate(st.session_state.chapters):
            st.write(f"**{i + 1}.** {ch['title']}")

        if st.button("📖 Generate Full Book", type="primary"):
            if not book_title or not members:
                st.error("Please provide a book title and family members.")
                return
            with st.spinner(f"Creating book with {len(st.session_state.chapters)} chapters..."):
                result = create_book(book_title, st.session_state.chapters, members, config=cfg)

            st.markdown(f"# {result['title']}")
            st.markdown("## Table of Contents")
            for i, t in enumerate(result["toc"], 1):
                st.markdown(f"{i}. {t}")
            st.divider()
            for ch_text in result["chapters"]:
                st.markdown(ch_text)
                st.divider()


def story_browser_page():
    """Story Browser page."""
    st.header("📂 Story Browser")
    cfg = get_config()
    stories = load_stories(cfg.get("stories_file"))

    if not stories:
        st.info("No saved stories yet. Create one in the Story Creator!")
        return

    for s in stories:
        with st.expander(f"📖 {s.get('event', 'Untitled')} — {s.get('style', '')} (id: {s.get('id', '')})"):
            st.markdown(f"**Members:** {s.get('members', '')}")
            st.markdown(f"**Created:** {s.get('created', '')}")
            preview = s.get("story", "")[:300]
            st.markdown(preview + ("..." if len(s.get("story", "")) > 300 else ""))

            col_view, col_continue, col_delete = st.columns(3)
            with col_view:
                if st.button("👁️ View Full", key=f"view_{s['id']}"):
                    st.markdown(s.get("story", ""))
            with col_continue:
                prompt = st.text_input("Continue with...", key=f"cont_input_{s['id']}")
                if st.button("▶️ Continue", key=f"cont_{s['id']}") and prompt:
                    with st.spinner("Continuing story..."):
                        continued = continue_story(s.get("story", ""), prompt, config=cfg)
                    st.markdown(continued)
            with col_delete:
                if st.button("🗑️ Delete", key=f"del_{s['id']}"):
                    delete_story(s["id"], cfg.get("stories_file"))
                    st.success("Deleted!")
                    st.rerun()


def poem_creator_page():
    """Poem Creator page."""
    st.header("🎭 Poem Creator")
    cfg = get_config()

    with st.form("poem_form"):
        members = st.text_input("Family Members", placeholder="e.g. Mom, Dad, Sam, Emma")
        event = st.text_input("Event", placeholder="e.g. Christmas morning")
        style = st.selectbox("Poem Style", ["rhyming", "free-verse", "haiku", "sonnet", "limerick"])
        submitted = st.form_submit_button("🎭 Generate Poem", type="primary")

    if submitted and members and event:
        with st.spinner("Writing your family poem..."):
            result = create_poem(members, event, style, config=cfg)
        st.markdown(result)


def main():
    """Streamlit app entry point."""
    st.sidebar.title("📖 Family Story Creator")
    st.sidebar.markdown("---")
    page = st.sidebar.radio(
        "Navigation",
        ["Story Creator", "Chapter Builder", "Story Browser", "Poem Creator"],
    )

    pages = {
        "Story Creator": story_creator_page,
        "Chapter Builder": chapter_builder_page,
        "Story Browser": story_browser_page,
        "Poem Creator": poem_creator_page,
    }
    pages[page]()


if __name__ == "__main__":
    main()
