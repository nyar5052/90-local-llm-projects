"""Streamlit web interface for IT Helpdesk Bot."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

import streamlit as st

from .config import load_config, setup_logging
from .core import check_ollama_running, get_response, CATEGORIES
from .utils import save_ticket, load_tickets, search_knowledge_base, load_knowledge_base

# Custom CSS for professional dark theme
st.set_page_config(page_title="IT Helpdesk Bot", page_icon="🎯", layout="wide")

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


def init_state():
    defaults = {"history": [], "config": load_config(), "category": "7"}
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def sidebar():
    cfg = st.session_state.config
    st.sidebar.title("⚙️ Settings")

    cfg["model"]["name"] = st.sidebar.text_input("Model", value=cfg["model"]["name"])
    cfg["model"]["temperature"] = st.sidebar.slider("Temperature", 0.0, 1.0, cfg["model"]["temperature"], 0.1)

    st.sidebar.markdown("---")
    st.sidebar.subheader("📂 Category")
    cat_options = {k: v[0] for k, v in CATEGORIES.items()}
    st.session_state.category = st.sidebar.selectbox("Select category", list(cat_options.keys()), format_func=lambda k: cat_options[k])

    st.sidebar.markdown("---")
    st.sidebar.subheader("🎫 Ticket History")
    tickets = load_tickets(cfg.get("tickets", {}).get("storage_file", "tickets.json"))
    if tickets:
        for t in tickets[-10:]:
            status_color = "🟢" if t["status"] == "closed" else "🔴"
            st.sidebar.markdown(f"{status_color} **{t['id']}** — {t['category']}")
    else:
        st.sidebar.info("No tickets yet.")

    if st.sidebar.button("🗑️ Clear Chat"):
        st.session_state.history = []
        st.rerun()


def main():
    init_state()
    cfg = st.session_state.config
    setup_logging(cfg)

    st.title("🖥️ IT Helpdesk Bot")
    st.caption("AI-powered IT support — describe your issue and get step-by-step help.")

    sidebar()

    tab_chat, tab_kb = st.tabs(["💬 Chat", "📖 Knowledge Base"])

    with tab_kb:
        st.subheader("Knowledge Base")
        kb = load_knowledge_base(cfg.get("knowledge_base", {}).get("file", "knowledge_base.json"))
        search = st.text_input("🔍 Search knowledge base")
        display_kb = search_knowledge_base(search, kb) if search else kb
        for entry in display_kb:
            with st.expander(entry["topic"]):
                st.markdown(entry["solution"])

    with tab_chat:
        for msg in st.session_state.history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input("Describe your IT issue..."):
            st.chat_message("user").markdown(prompt)
            st.session_state.history.append({"role": "user", "content": prompt})

            with st.spinner("Diagnosing..."):
                if not check_ollama_running():
                    st.error("❌ Ollama is not running. Start with: `ollama serve`")
                    return
                answer = get_response(
                    prompt,
                    st.session_state.history[:-1],
                    model=cfg["model"]["name"],
                    temperature=cfg["model"]["temperature"],
                )

            st.chat_message("assistant").markdown(answer)
            st.session_state.history.append({"role": "assistant", "content": answer})

            # Auto-create ticket
            cat_name = CATEGORIES.get(st.session_state.category, ("General", ""))[0]
            save_ticket(cat_name, prompt[:200], resolution=answer[:200], storage_file=cfg.get("tickets", {}).get("storage_file", "tickets.json"))


if __name__ == "__main__":
    main()
