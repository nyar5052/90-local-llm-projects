"""Streamlit Web UI for Newsletter Editor."""

import sys
import os
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from newsletter_editor.core import (
    generate_newsletter,
    load_config,
    export_to_html,
    archive_newsletter,
    list_archive,
    get_section_templates,
    get_subscriber_segments,
)

# ── Page Configuration ───────────────────────────────────────────────
# Custom CSS for professional dark theme
st.set_page_config(page_title="Newsletter Editor", page_icon="🎯", layout="wide")

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
    st.title("📰 Newsletter Editor")
    st.markdown("*Curate and rewrite content into polished, professional newsletters*")

    config = load_config("config.yaml")
    templates = get_section_templates()
    segments = get_subscriber_segments()

    tab1, tab2, tab3, tab4 = st.tabs(["✍️ Section Builder", "👁️ Preview", "📋 Template Selector", "📤 Export"])

    # ── Section Builder Tab ──────────────────────────────────────────
    with tab1:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.subheader("Input")
            name = st.text_input("Newsletter Name", value="Weekly Digest")
            raw_content = st.text_area("Raw Notes / Content", height=250,
                                       placeholder="Paste your raw notes, links, and ideas here...")
            uploaded_file = st.file_uploader("Or upload a text file", type=["txt", "md"])
            if uploaded_file:
                raw_content = uploaded_file.read().decode("utf-8")
                st.success(f"Loaded {len(raw_content)} chars from {uploaded_file.name}")

        with col2:
            st.subheader("Settings")
            sections = st.slider("Number of Sections", 2, 10, 4)
            tone = st.selectbox("Tone", config["newsletter"]["supported_tones"])
            template = st.selectbox("Section Template", ["None"] + list(templates.keys()),
                                     format_func=lambda x: templates[x]["name"] if x in templates else "No Template")
            segment = st.selectbox("Subscriber Segment", list(segments.keys()),
                                    format_func=lambda x: segments[x]["name"])

            if template == "None":
                template = None

        if st.button("🚀 Generate Newsletter", type="primary", use_container_width=True):
            if not raw_content:
                st.error("Please provide raw content or upload a file.")
            else:
                with st.spinner("Generating newsletter..."):
                    try:
                        result = generate_newsletter(raw_content, name, sections, tone, template, segment, config)
                        st.session_state["newsletter_result"] = result
                        st.session_state["newsletter_name"] = name
                        st.success("Newsletter generated!")
                    except Exception as e:
                        st.error(f"Error: {e}")

    # ── Preview Tab ──────────────────────────────────────────────────
    with tab2:
        if "newsletter_result" in st.session_state:
            st.subheader(f"📰 {st.session_state.get('newsletter_name', 'Newsletter')}")
            st.markdown(st.session_state["newsletter_result"])
        else:
            st.info("Generate a newsletter first to see the preview.")

    # ── Template Selector Tab ────────────────────────────────────────
    with tab3:
        st.subheader("📋 Available Section Templates")
        for key, tmpl in templates.items():
            with st.expander(f"**{tmpl['name']}** — {tmpl['description']}"):
                st.markdown(f"**Prompt Hint:** {tmpl['prompt_hint']}")
                st.code(f"--template {key}", language="bash")

    # ── Export Tab ───────────────────────────────────────────────────
    with tab4:
        if "newsletter_result" in st.session_state:
            result = st.session_state["newsletter_result"]
            nl_name = st.session_state.get("newsletter_name", "newsletter")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.download_button("📄 Download Markdown", result, file_name=f"{nl_name}.md", mime="text/markdown")
            with col2:
                html_content = export_to_html(result, nl_name)
                st.download_button("🌐 Download HTML", html_content, file_name=f"{nl_name}.html", mime="text/html")
            with col3:
                if st.button("🗄️ Archive Newsletter"):
                    path = archive_newsletter(result, nl_name, config)
                    st.success(f"Archived to {path}")

            st.subheader("🗄️ Newsletter Archive")
            archives = list_archive(config)
            if archives:
                for a in archives:
                    st.text(f"  {a['filename']}  ({a['size']:,} B)  {a['modified'][:19]}")
            else:
                st.info("No archived newsletters yet.")
        else:
            st.info("Generate a newsletter first to access export options.")


if __name__ == "__main__":
    main()
