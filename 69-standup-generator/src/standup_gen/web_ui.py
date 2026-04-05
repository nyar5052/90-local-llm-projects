#!/usr/bin/env python3
"""Streamlit Web UI for Standup Generator."""

import json
import os
import sys

import streamlit as st

# Ensure package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from standup_gen.core import (  # noqa: E402
    STANDUP_TEMPLATES,
    categorize_tasks,
    check_ollama_running,
    extract_ticket_refs,
    format_ticket_refs,
    generate_sprint_review,
    generate_standup,
    generate_weekly_summary,
    get_git_branches,
    get_git_log,
    get_team_standup,
    load_config,
    load_standup_history,
    save_standup,
)


def init_session_state():
    """Initialize Streamlit session state defaults."""
    defaults = {
        "config": load_config(),
        "standup_result": "",
        "team_members": [],
        "git_repo_path": ".",
        "default_template": "daily",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def page_generate():
    """Generate Standup page."""
    st.header("📝 Generate Standup")
    config = st.session_state.config

    col1, col2 = st.columns(2)
    with col1:
        team_name = st.text_input("Team Name", value=config.get("team", {}).get("name", ""))
    with col2:
        project_name = st.text_input("Project Name")

    template = st.selectbox(
        "Template",
        list(STANDUP_TEMPLATES.keys()),
        index=list(STANDUP_TEMPLATES.keys()).index(
            st.session_state.default_template
        ),
    )

    input_mode = st.radio("Task Input Mode", ["Quick Entry", "JSON Input"], horizontal=True)

    tasks = {}
    if input_mode == "Quick Entry":
        completed = st.text_area(
            "✅ Completed Tasks (one per line)",
            height=100,
            placeholder="Fixed login bug\nUpdated documentation",
        )
        today = st.text_area(
            "🎯 Today's Tasks (one per line)",
            height=100,
            placeholder="Implement user profile\nReview PR #42",
        )
        blockers = st.text_area(
            "🚧 Blockers (one per line)",
            height=80,
            placeholder="Waiting for API keys",
        )
        tasks = {
            "completed": [{"title": t.strip(), "status": "done"} for t in completed.strip().split("\n") if t.strip()],
            "today": [{"title": t.strip(), "status": "in_progress"} for t in today.strip().split("\n") if t.strip()],
            "blockers": [{"title": t.strip(), "status": "blocked"} for t in blockers.strip().split("\n") if t.strip()],
        }
    else:
        json_input = st.text_area(
            "Tasks JSON",
            height=200,
            placeholder='{\n  "completed": [{"title": "Task A", "status": "done"}],\n  "today": [{"title": "Task B"}]\n}',
        )
        if json_input.strip():
            try:
                tasks = json.loads(json_input)
            except json.JSONDecodeError as e:
                st.error(f"Invalid JSON: {e}")
                return

    # Git integration
    use_git = st.checkbox("Include Git Activity", value=config.get("git", {}).get("enabled", False))
    git_log_text = ""
    if use_git:
        git_path = st.text_input("Git Repo Path", value=st.session_state.git_repo_path)
        st.session_state.git_repo_path = git_path
        git_days = st.slider("Git History (days)", 1, 14, 1)
        git_log_text = get_git_log(git_path, git_days)
        if git_log_text:
            st.code(git_log_text, language="text")
            branches = get_git_branches(git_path)
            if branches:
                st.caption(f"Branches: {', '.join(branches[:5])}")
        else:
            st.info("No git activity found for the selected period.")

    # Preview
    if tasks and any(tasks.values()) if isinstance(tasks, dict) else tasks:
        categorized = categorize_tasks(tasks)
        with st.expander("📋 Task Preview", expanded=False):
            for cat, items in categorized.items():
                if items:
                    emoji = {"completed": "✅", "in_progress": "🔄", "planned": "📝", "blocked": "🚧"}.get(cat, "📋")
                    st.write(f"**{emoji} {cat.replace('_', ' ').title()}** ({len(items)})")
                    for item in items:
                        title = item.get("title", str(item)) if isinstance(item, dict) else str(item)
                        st.write(f"  - {title}")

    # Generate
    col_gen, col_save = st.columns(2)
    with col_gen:
        generate_btn = st.button("🚀 Generate Standup", type="primary", use_container_width=True)
    with col_save:
        save_btn = st.button("💾 Save to History", use_container_width=True)

    if generate_btn:
        if not tasks or (isinstance(tasks, dict) and not any(tasks.values())):
            st.warning("Please enter some tasks first.")
            return

        if not check_ollama_running():
            st.error("Ollama is not running. Start it with: `ollama serve`")
            return

        with st.spinner("Generating standup..."):
            if template == "weekly":
                result = generate_weekly_summary(tasks, git_log_text, config)
            elif template == "sprint_review":
                result = generate_sprint_review(tasks, config=config)
            else:
                result = generate_standup(tasks, git_log_text, team_name, project_name, template, config)

        st.session_state.standup_result = result

    if st.session_state.standup_result:
        st.divider()
        st.subheader("Generated Standup")
        st.markdown(st.session_state.standup_result)

        # Ticket references
        refs = extract_ticket_refs(st.session_state.standup_result)
        if refs:
            st.caption(f"🎫 Ticket references found: {', '.join(set(refs))}")

        st.code(st.session_state.standup_result, language="markdown")

    if save_btn and st.session_state.standup_result:
        history_file = config.get("standup", {}).get("history_file", "standup_history.json")
        entry = save_standup(st.session_state.standup_result, team_name, history_file)
        st.success(f"Saved to history ({entry['date']})")


def page_history():
    """History page."""
    st.header("📜 Standup History")
    config = st.session_state.config
    history_file = config.get("standup", {}).get("history_file", "standup_history.json")

    col1, col2 = st.columns(2)
    with col1:
        days = st.slider("Show last N days", 1, 90, 7)
    with col2:
        member_filter = st.text_input("Filter by member", "")

    entries = load_standup_history(history_file, days)
    if member_filter:
        entries = [e for e in entries if member_filter.lower() in e.get("team_member", "").lower()]

    if not entries:
        st.info("No standup history found for the selected period.")
        return

    # Stats
    st.subheader("📊 Stats")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("Total Standups", len(entries))
    with col_b:
        unique_dates = len(set(e.get("date", "") for e in entries))
        st.metric("Active Days", unique_dates)
    with col_c:
        members = set(e.get("team_member", "") for e in entries if e.get("team_member"))
        st.metric("Team Members", len(members) if members else 1)

    st.divider()

    for i, entry in enumerate(reversed(entries)):
        with st.expander(f"📋 {entry.get('date', 'Unknown')} - {entry.get('team_member', 'Default')}", expanded=(i == 0)):
            st.markdown(entry.get("content", ""))


def page_team_view():
    """Team View page."""
    st.header("👥 Team View")
    config = st.session_state.config

    team_members = st.text_area(
        "Team Members (one per line)",
        value="\n".join(st.session_state.team_members),
        height=100,
    )
    members = [m.strip() for m in team_members.strip().split("\n") if m.strip()]
    st.session_state.team_members = members

    tasks_dir = st.text_input("Tasks Directory", value=".")

    if members:
        st.write(f"**Team ({len(members)} members):** {', '.join(members)}")

        if st.button("🚀 Generate Team Standup", type="primary"):
            if not check_ollama_running():
                st.error("Ollama is not running. Start it with: `ollama serve`")
                return

            with st.spinner("Generating team standup..."):
                result = get_team_standup(members, tasks_dir, config)

            st.markdown(result)
    else:
        st.info("Add team members to generate a combined standup.")

    # Individual member standups from history
    st.divider()
    st.subheader("📜 Recent Individual Standups")
    history_file = config.get("standup", {}).get("history_file", "standup_history.json")
    entries = load_standup_history(history_file, 7)
    if entries:
        for member in members:
            member_entries = [e for e in entries if e.get("team_member", "") == member]
            if member_entries:
                with st.expander(f"👤 {member} ({len(member_entries)} standups)"):
                    for entry in reversed(member_entries):
                        st.caption(entry.get("date", ""))
                        st.markdown(entry.get("content", ""))
                        st.divider()
    else:
        st.caption("No history available yet.")


def page_settings():
    """Settings page."""
    st.header("⚙️ Settings")
    config = st.session_state.config

    st.subheader("Git Configuration")
    git_path = st.text_input("Default Git Repo Path", value=config.get("git", {}).get("repo_path", "."))
    git_enabled = st.checkbox("Enable Git Integration", value=config.get("git", {}).get("enabled", True))
    git_branches = st.checkbox("Include Branch Info", value=config.get("git", {}).get("include_branches", True))

    st.subheader("Standup Defaults")
    default_template = st.selectbox(
        "Default Template",
        list(STANDUP_TEMPLATES.keys()),
        index=list(STANDUP_TEMPLATES.keys()).index(
            config.get("standup", {}).get("default_template", "daily")
        ),
    )
    auto_save = st.checkbox("Auto-save Standups", value=config.get("standup", {}).get("auto_save", True))

    st.subheader("LLM Configuration")
    model = st.text_input("Model", value=config.get("llm", {}).get("model", "llama3.2"))
    temperature = st.slider("Temperature", 0.0, 1.0, config.get("llm", {}).get("temperature", 0.4))

    st.subheader("Team Members")
    team_name = st.text_input("Team Name", value=config.get("team", {}).get("name", ""))
    team_members_str = st.text_area(
        "Members (one per line)",
        value="\n".join(config.get("team", {}).get("members", [])),
    )

    if st.button("💾 Save Settings", type="primary"):
        config["git"]["repo_path"] = git_path
        config["git"]["enabled"] = git_enabled
        config["git"]["include_branches"] = git_branches
        config["standup"]["default_template"] = default_template
        config["standup"]["auto_save"] = auto_save
        config["llm"]["model"] = model
        config["llm"]["temperature"] = temperature
        config["team"]["name"] = team_name
        config["team"]["members"] = [m.strip() for m in team_members_str.strip().split("\n") if m.strip()]

        st.session_state.config = config
        st.session_state.default_template = default_template
        st.success("Settings saved for this session.")

    # Ollama status
    st.divider()
    st.subheader("🔌 System Status")
    if check_ollama_running():
        st.success("✅ Ollama is running")
    else:
        st.error("❌ Ollama is not running. Start it with: `ollama serve`")


def run():
    """Main Streamlit application entry point."""
    st.set_page_config(
        page_title="Standup Generator",
        page_icon="📋",
        layout="wide",
    )

    init_session_state()

    st.sidebar.title("📋 Standup Generator")
    st.sidebar.caption("AI-powered standup updates")

    page = st.sidebar.radio(
        "Navigation",
        ["Generate Standup", "History", "Team View", "Settings"],
        label_visibility="collapsed",
    )

    if page == "Generate Standup":
        page_generate()
    elif page == "History":
        page_history()
    elif page == "Team View":
        page_team_view()
    elif page == "Settings":
        page_settings()


if __name__ == "__main__":
    run()
