"""Streamlit web interface for IT Helpdesk Bot."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

import streamlit as st

from .config import load_config, setup_logging
from .core import check_ollama_running, get_response, CATEGORIES
from .utils import save_ticket, load_tickets, search_knowledge_base, load_knowledge_base

st.set_page_config(page_title="🖥️ IT Helpdesk Bot", page_icon="🖥️", layout="wide")


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
