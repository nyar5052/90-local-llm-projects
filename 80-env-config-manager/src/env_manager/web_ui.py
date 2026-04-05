"""Streamlit Web UI for Environment Config Manager."""

import streamlit as st

from .core import (
    parse_env_file,
    validate_env,
    generate_env_template,
    suggest_missing_vars,
    generate_env_documentation,
    detect_secrets,
    compare_envs,
    generate_migration_script,
    PROJECT_TYPES,
    SECRET_PATTERNS,
    check_ollama_running,
)


def main():
    st.set_page_config(page_title="⚙️ Env Config Manager", page_icon="⚙️", layout="wide")
    st.title("⚙️ Environment Config Manager")
    st.caption("Manage, validate, compare, and document .env files with AI")

    if not check_ollama_running():
        st.error("⚠️ Ollama is not running. Start with: `ollama serve`")
        return

    tab_upload, tab_compare, tab_security, tab_docs = st.tabs([
        "📁 Env File Upload", "🔄 Comparison View", "🔐 Security Alerts", "📄 Doc Generator"
    ])

    # ---- Upload Tab ----
    with tab_upload:
        col_input, col_result = st.columns([1, 1])

        with col_input:
            st.subheader("Upload .env File")
            uploaded = st.file_uploader("Upload .env file", type=["env", "txt"], key="main_upload")
            paste_content = st.text_area("Or paste .env content", height=200, placeholder="APP_NAME=MyApp\nDEBUG=true\nSECRET_KEY=changeme")

            content = ""
            if uploaded:
                content = uploaded.read().decode("utf-8")
            elif paste_content:
                content = paste_content

            if content:
                # Write to temp-like session state for processing
                st.session_state["env_content"] = content

                # Parse and display
                lines = content.strip().split("\n")
                env_vars = {}
                for line in lines:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        k, _, v = line.partition("=")
                        env_vars[k.strip()] = v.strip().strip('"').strip("'")
                st.session_state["parsed_env"] = env_vars

                st.success(f"Parsed {len(env_vars)} variables")

                # Show parsed vars
                for key, value in env_vars.items():
                    is_secret = any(p.search(key) for p in SECRET_PATTERNS.values())
                    display_val = "***" if is_secret and value else (value or "(empty)")
                    icon = "🔑" if is_secret else "✅" if value else "⚠️"
                    st.markdown(f"{icon} `{key}` = `{display_val}`")

            st.divider()
            st.subheader("🔧 Actions")
            action = st.radio("Select action", ["Validate", "Suggest Variables", "Generate Template"], horizontal=True)

            if action == "Validate" and content:
                if st.button("🔍 Validate", type="primary"):
                    # Save to temp file for validation
                    import tempfile, os
                    with st.spinner("Validating..."):
                        tf = os.path.join(os.path.dirname(__file__), "_temp_env")
                        with open(tf, "w") as f:
                            f.write(content)
                        try:
                            result = validate_env(tf)
                            st.session_state["validation_result"] = result
                        finally:
                            os.remove(tf)

            elif action == "Suggest Variables":
                project_type = st.selectbox("Project type", PROJECT_TYPES)
                if content and st.button("💡 Suggest", type="primary"):
                    import os
                    with st.spinner("Analyzing..."):
                        tf = os.path.join(os.path.dirname(__file__), "_temp_env")
                        with open(tf, "w") as f:
                            f.write(content)
                        try:
                            result = suggest_missing_vars(tf, project_type)
                            st.session_state["suggestion_result"] = result
                        finally:
                            os.remove(tf)

            elif action == "Generate Template":
                project_type = st.selectbox("Project type", PROJECT_TYPES, key="gen_project")
                env_name = st.selectbox("Environment", ["development", "staging", "production"])
                if st.button("📝 Generate", type="primary"):
                    with st.spinner("Generating template..."):
                        result = generate_env_template(project_type, env_name)
                        st.session_state["template_result"] = result

        with col_result:
            st.subheader("Results")
            if "validation_result" in st.session_state:
                st.markdown(st.session_state["validation_result"])
            elif "suggestion_result" in st.session_state:
                st.markdown(st.session_state["suggestion_result"])
            elif "template_result" in st.session_state:
                st.code(st.session_state["template_result"])
                st.download_button("💾 Download .env", st.session_state["template_result"], file_name=".env.example")
            else:
                st.info("Upload a file and run an action to see results")

    # ---- Comparison Tab ----
    with tab_compare:
        st.subheader("🔄 Multi-Environment Comparison")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Environment 1**")
            env1_content = st.text_area("Paste .env (Env 1)", height=200, key="env1")

        with col2:
            st.markdown("**Environment 2**")
            env2_content = st.text_area("Paste .env (Env 2)", height=200, key="env2")

        if env1_content and env2_content and st.button("🔄 Compare", type="primary"):
            env1 = {}
            env2 = {}
            for line in env1_content.strip().split("\n"):
                if "=" in line and not line.strip().startswith("#"):
                    k, _, v = line.partition("=")
                    env1[k.strip()] = v.strip().strip('"').strip("'")
            for line in env2_content.strip().split("\n"):
                if "=" in line and not line.strip().startswith("#"):
                    k, _, v = line.partition("=")
                    env2[k.strip()] = v.strip().strip('"').strip("'")

            result = compare_envs(env1, env2)

            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Env 1 vars", result["total_first"])
            col_b.metric("Env 2 vars", result["total_second"])
            col_c.metric("Different", len(result["different_values"]))

            if result["only_in_first"]:
                st.warning(f"**Only in Env 1:** {', '.join(result['only_in_first'])}")
            if result["only_in_second"]:
                st.warning(f"**Only in Env 2:** {', '.join(result['only_in_second'])}")
            if result["different_values"]:
                st.markdown("**Different values:**")
                for k, v in result["different_values"].items():
                    st.markdown(f"- `{k}`: `{v['env1']}` → `{v['env2']}`")

            # Migration script
            st.divider()
            script = generate_migration_script(env1, env2, "Environment 2")
            with st.expander("📜 Migration Script"):
                st.code(script, language="bash")
                st.download_button("💾 Download Script", script, file_name="migrate.sh")

    # ---- Security Tab ----
    with tab_security:
        st.subheader("🔐 Security Analysis")
        parsed_env = st.session_state.get("parsed_env", {})

        if parsed_env:
            findings = detect_secrets(parsed_env)
            if findings:
                for f in findings:
                    icon = "🔴" if f["severity"] == "critical" else "🟡" if f["severity"] == "warning" else "ℹ️"
                    st.markdown(f"{icon} **{f['severity'].upper()}** — {f['message']}")
            else:
                st.success("✅ No security issues detected")
        else:
            st.info("Upload an .env file in the Upload tab first")

    # ---- Documentation Tab ----
    with tab_docs:
        st.subheader("📄 Environment Documentation Generator")
        env_content = st.session_state.get("env_content", "")

        if env_content:
            if st.button("📝 Generate Documentation", type="primary"):
                import os
                with st.spinner("Generating documentation..."):
                    tf = os.path.join(os.path.dirname(__file__), "_temp_env")
                    with open(tf, "w") as f:
                        f.write(env_content)
                    try:
                        result = generate_env_documentation(tf)
                        st.session_state["env_docs"] = result
                    finally:
                        os.remove(tf)

            if "env_docs" in st.session_state:
                st.markdown(st.session_state["env_docs"])
                st.download_button("💾 Download Docs", st.session_state["env_docs"], file_name="env-docs.md", mime="text/markdown")
        else:
            st.info("Upload an .env file in the Upload tab first")


if __name__ == "__main__":
    main()
