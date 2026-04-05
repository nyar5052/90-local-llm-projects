"""Streamlit Web UI for Poem & Lyrics Generator."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

import streamlit as st  # noqa: E402

from common.llm_client import check_ollama_running  # noqa: E402
from poem_gen.core import (  # noqa: E402
    STYLES,
    MOODS,
    STYLE_INSTRUCTIONS,
    Poem,
    generate_poem,
    generate_with_rhyme_scheme,
    mix_styles,
    analyze_poem,
    format_poem,
    manage_collection,
)

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
# Custom CSS for professional dark theme
st.set_page_config(page_title="Poem & Lyrics Generator", page_icon="🎯", layout="wide")

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

# ---------------------------------------------------------------------------
# Sidebar — style descriptions and examples
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("📖 Style Guide")

    style_examples = {
        "haiku": "An old silent pond…\nA frog jumps into the pond—\nSplash! Silence again.",
        "sonnet": "Shall I compare thee to a summer's day?\nThou art more lovely and more temperate…",
        "free-verse": "I celebrate myself, and sing myself,\nAnd what I assume you shall assume…",
        "limerick": "There once was a man from Nantucket…",
        "rap": "Look, if you had one shot, one opportunity…",
        "ballad": "It was many and many a year ago,\nIn a kingdom by the sea…",
        "acrostic": "Sunshine warms my face\nUplifting spirits within\nMorning birds call out…",
    }

    for s in STYLES:
        with st.expander(f"**{s.title()}**"):
            st.caption(STYLE_INSTRUCTIONS.get(s, ""))
            st.code(style_examples.get(s, ""), language=None)

    st.divider()
    st.caption("Poem & Lyrics Generator v2.0 • Powered by Ollama")

# ---------------------------------------------------------------------------
# Main content
# ---------------------------------------------------------------------------
st.title("✨ Poem & Lyrics Generator")
st.markdown("Generate beautiful poems and song lyrics using a local LLM.")

# Check Ollama
if not check_ollama_running():
    st.error("⚠️ Ollama is not running. Start it with: `ollama serve`")
    st.stop()

# ---------------------------------------------------------------------------
# Input section
# ---------------------------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    theme = st.text_input("🎨 Theme / Subject", placeholder="e.g. ocean sunset, lost love, city life")
    style = st.selectbox("📝 Style", STYLES, index=STYLES.index("free-verse"))
    mood = st.selectbox("🎭 Mood (optional)", ["(none)"] + MOODS)
    if mood == "(none)":
        mood = None
    title_input = st.text_input("📌 Title (optional)", placeholder="Leave blank for auto-generated")
    title_val = title_input.strip() or None

with col2:
    st.markdown("**Advanced Options**")
    rhyme_scheme = st.text_input(
        "🔤 Rhyme Scheme (optional)",
        placeholder="e.g. ABAB, AABB, ABCABC",
    ).strip().upper() or None

    st.markdown("**Style Mixing**")
    enable_mix = st.checkbox("Mix two styles")
    mix_style1, mix_style2 = None, None
    if enable_mix:
        mc1, mc2 = st.columns(2)
        with mc1:
            mix_style1 = st.selectbox("Style 1", STYLES, key="mix1")
        with mc2:
            mix_style2 = st.selectbox("Style 2", STYLES, index=1, key="mix2")

# ---------------------------------------------------------------------------
# Generate
# ---------------------------------------------------------------------------
generate_btn = st.button("🚀 Generate Poem", type="primary", use_container_width=True)

if generate_btn:
    if not theme:
        st.warning("Please enter a theme.")
        st.stop()

    with st.spinner(f"Composing {style} poem…"):
        if enable_mix and mix_style1 and mix_style2:
            result = mix_styles(theme, [mix_style1, mix_style2], mood)
        elif rhyme_scheme:
            result = generate_with_rhyme_scheme(theme, rhyme_scheme, mood)
        else:
            result = generate_poem(theme, style, mood, title_val)

    st.session_state["last_poem"] = result
    st.session_state["last_style"] = style
    st.session_state["last_mood"] = mood
    st.session_state["last_theme"] = theme
    st.session_state["last_title"] = title_val or "Untitled"

# ---------------------------------------------------------------------------
# Display poem
# ---------------------------------------------------------------------------
if "last_poem" in st.session_state:
    result = st.session_state["last_poem"]
    poem_style = st.session_state.get("last_style", "free-verse")

    formatted = format_poem(result, poem_style)
    st.divider()
    st.subheader(f"✨ {poem_style.title()}")
    st.text(formatted)

    # Download button
    st.download_button(
        "📥 Download Poem",
        data=result,
        file_name="poem.txt",
        mime="text/plain",
    )

    # Analysis section
    with st.expander("📊 Poem Analysis"):
        analysis = analyze_poem(result)
        ac1, ac2, ac3 = st.columns(3)
        ac1.metric("Lines", analysis["line_count"])
        ac2.metric("Words", analysis["word_count"])
        ac3.metric("Rhyme Scheme", analysis["detected_rhyme_scheme"] or "—")
        if analysis["syllables_per_line"]:
            st.bar_chart(
                {"Syllables per Line": analysis["syllables_per_line"]},
            )

    # Collection manager
    st.divider()
    st.subheader("📚 Collection Manager")
    col_name = st.text_input("Collection Name", value="my-poems", key="col_name")

    save_col, view_col = st.columns(2)
    with save_col:
        if st.button("💾 Save to Collection"):
            poem_obj = Poem(
                title=st.session_state.get("last_title", "Untitled"),
                content=result,
                style=poem_style,
                mood=st.session_state.get("last_mood"),
                theme=st.session_state.get("last_theme"),
            )
            coll = manage_collection(col_name, "add", poem_obj)
            st.success(f"Saved! Collection now has {len(coll.poems)} poem(s).")

    with view_col:
        if st.button("📖 View Collection"):
            coll = manage_collection(col_name, "list")
            if not coll.poems:
                st.info("Collection is empty.")
            else:
                for i, p in enumerate(coll.poems, 1):
                    with st.expander(f"#{i} — {p.title} [{p.style}]"):
                        st.text(p.content)
                # Download entire collection
                import json as _json

                coll_json = _json.dumps(coll.to_dict(), indent=2, ensure_ascii=False)
                st.download_button(
                    "📥 Download Collection (JSON)",
                    data=coll_json,
                    file_name=f"{col_name}.json",
                    mime="application/json",
                    key="dl_coll",
                )
