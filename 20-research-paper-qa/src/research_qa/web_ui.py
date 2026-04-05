"""Streamlit web interface for the Research Paper QA."""

import streamlit as st

from .core import (
    load_paper,
    build_system_prompt,
    build_multi_paper_content,
    ask_question,
    suggest_followup_questions,
    extract_citations,
)
from .config import load_config
from .utils import setup_sys_path

setup_sys_path()
from common.llm_client import check_ollama_running


def run():
    """Launch the Streamlit web UI."""
    config = load_config()

    st.set_page_config(page_title="🔍 Research Paper QA", page_icon="🔍", layout="wide")
    st.title("🔍 Research Paper Q&A")
    st.markdown("Upload research papers and ask questions with citation tracking.")

    # Initialize session state
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    if "system_prompt" not in st.session_state:
        st.session_state.system_prompt = None
    if "papers_loaded" not in st.session_state:
        st.session_state.papers_loaded = []

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")

        if check_ollama_running():
            st.success("✅ Ollama is running")
        else:
            st.error("❌ Ollama is not running. Start with: `ollama serve`")
            return

        st.subheader("📄 Papers")
        uploaded_files = st.file_uploader(
            "Upload research papers",
            type=["txt", "md"],
            accept_multiple_files=True,
        )

        if uploaded_files:
            papers = {}
            for uf in uploaded_files:
                content = uf.read().decode("utf-8")
                if content.strip():
                    papers[uf.name] = content

            if papers:
                paper_content = build_multi_paper_content(papers)
                st.session_state.system_prompt = build_system_prompt(paper_content)
                st.session_state.papers_loaded = list(papers.keys())

                st.success(f"✅ {len(papers)} paper(s) loaded")
                for name in papers:
                    word_count = len(papers[name].split())
                    st.write(f"• {name} ({word_count:,} words)")

        # Citation sidebar
        if st.session_state.conversation_history:
            st.subheader("📚 Citations")
            all_citations = []
            for msg in st.session_state.conversation_history:
                if msg["role"] == "assistant":
                    all_citations.extend(extract_citations(msg["content"]))
            if all_citations:
                for c in set(all_citations):
                    st.write(f"• {c}")
            else:
                st.write("No citations found yet.")

        # Export notes
        if st.session_state.conversation_history:
            notes_text = ""
            for msg in st.session_state.conversation_history:
                role = "**Q:**" if msg["role"] == "user" else "**A:**"
                notes_text += f"{role} {msg['content']}\n\n---\n\n"
            st.download_button(
                "📥 Export Notes",
                data=notes_text,
                file_name="research_qa_notes.md",
                mime="text/markdown",
            )

    # Main chat interface
    if st.session_state.system_prompt is None:
        st.info("👈 Upload research paper(s) in the sidebar to begin.")
        return

    # Display conversation history
    for msg in st.session_state.conversation_history:
        if msg["role"] == "user":
            st.chat_message("user").markdown(msg["content"])
        else:
            st.chat_message("assistant").markdown(msg["content"])

    # Chat input
    question = st.chat_input("Ask a question about the paper(s)...")

    if question:
        st.chat_message("user").markdown(question)

        with st.spinner("Thinking..."):
            answer = ask_question(
                question,
                st.session_state.conversation_history,
                st.session_state.system_prompt,
                config=config,
            )

        st.chat_message("assistant").markdown(answer)

        # Show citations
        citations = extract_citations(answer)
        if citations:
            st.caption("📚 Citations: " + ", ".join(citations))

    # Follow-up suggestions
    if st.session_state.conversation_history and st.button("💡 Suggest Follow-up Questions"):
        with st.spinner("Generating suggestions..."):
            suggestions = suggest_followup_questions(
                st.session_state.conversation_history,
                st.session_state.system_prompt,
                config=config,
            )
        st.markdown(suggestions)

    # Clear conversation
    if st.session_state.conversation_history:
        if st.button("🗑️ Clear Conversation"):
            st.session_state.conversation_history = []
            st.rerun()


if __name__ == "__main__":
    run()
