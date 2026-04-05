"""Streamlit Web UI for Docker Compose Generator."""

import streamlit as st


# Custom CSS for professional dark theme
st.set_page_config(page_title="Docker Compose Generator", page_icon="🎯", layout="wide")

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

from .core import (
    generate_compose,
    explain_compose,
    extract_yaml,
    validate_compose,
    COMMON_STACKS,
    SERVICE_CATALOG,
    ENV_PROFILES,
    check_ollama_running,
)


def render_service_card(name: str, info: dict):
    """Render a service card in the sidebar."""
    selected = st.checkbox(f"**{name}** — `{info['image']}`  (:{info['port']})", key=f"svc_{name}")
    return selected


def main():
    st.title("🐳 Docker Compose Generator")
    st.caption("Generate production-ready Docker Compose files with AI")

    if not check_ollama_running():
        st.error("⚠️ Ollama is not running. Start with: `ollama serve`")
        return

    tab_generate, tab_explain, tab_catalog = st.tabs(["🏗️ Stack Builder", "📖 Explain Compose", "📦 Service Catalog"])

    # ---- Stack Builder Tab ----
    with tab_generate:
        col_config, col_output = st.columns([1, 1])

        with col_config:
            st.subheader("Stack Configuration")

            stack_mode = st.radio("Input mode", ["Natural Language", "Quick Stack", "Service Picker"], horizontal=True)

            stack_desc = ""
            selected_services = []

            if stack_mode == "Natural Language":
                stack_desc = st.text_area("Describe your stack", placeholder="e.g. Python Flask API with PostgreSQL, Redis cache, and Nginx reverse proxy", height=100)
            elif stack_mode == "Quick Stack":
                chosen = st.selectbox("Select a common stack", list(COMMON_STACKS.keys()), format_func=lambda x: f"{x.upper()} — {COMMON_STACKS[x]}")
                stack_desc = f"{chosen} stack ({COMMON_STACKS[chosen]})"
            else:
                st.markdown("**Select services from the catalog:**")
                for category, services in SERVICE_CATALOG.items():
                    with st.expander(f"📁 {category.replace('_', ' ').title()}", expanded=False):
                        for name, info in services.items():
                            if render_service_card(name, info):
                                selected_services.append(name)
                if selected_services:
                    stack_desc = f"Stack with: {', '.join(selected_services)}"

            st.divider()
            st.subheader("🌍 Environment")
            env_tabs = st.tabs(list(ENV_PROFILES.keys()))
            selected_env = "development"
            for i, (env_name, profile) in enumerate(ENV_PROFILES.items()):
                with env_tabs[i]:
                    st.json(profile)
                    if st.button(f"Use {env_name.title()}", key=f"env_{env_name}"):
                        selected_env = env_name
                        st.success(f"Selected: {env_name}")

            selected_env = st.selectbox("Active environment", list(ENV_PROFILES.keys()), index=0)

            network_mode = st.selectbox("Network mode", ["simple", "isolated", "overlay"])

            generate_btn = st.button("🚀 Generate Compose", type="primary", use_container_width=True, disabled=not stack_desc)

        with col_output:
            st.subheader("Generated Docker Compose")

            if generate_btn and stack_desc:
                with st.spinner("Generating Docker Compose file..."):
                    result = generate_compose(
                        stack_desc,
                        selected_env,
                        selected_services if selected_services else None,
                        network_mode,
                    )
                    yaml_content = extract_yaml(result)
                    st.session_state["generated_yaml"] = yaml_content

            if "generated_yaml" in st.session_state:
                yaml_content = st.session_state["generated_yaml"]

                validation = validate_compose(yaml_content)
                if validation["valid"]:
                    st.success("✅ Valid YAML")
                else:
                    for err in validation["errors"]:
                        st.warning(f"⚠️ {err}")

                st.code(yaml_content, language="yaml")

                st.download_button("💾 Download docker-compose.yml", yaml_content, file_name="docker-compose.yml", mime="text/yaml")
            else:
                st.info("Configure your stack and click Generate to create a docker-compose.yml")

    # ---- Explain Tab ----
    with tab_explain:
        st.subheader("📖 Explain an Existing Compose File")
        uploaded = st.file_uploader("Upload docker-compose.yml", type=["yml", "yaml"])
        paste_content = st.text_area("Or paste compose content", height=200)

        content = ""
        if uploaded:
            content = uploaded.read().decode("utf-8")
        elif paste_content:
            content = paste_content

        if content and st.button("🔍 Explain", type="primary"):
            with st.spinner("Analyzing..."):
                explanation = explain_compose(content)
            st.markdown(explanation)

    # ---- Service Catalog Tab ----
    with tab_catalog:
        st.subheader("📦 Service Catalog")
        for category, services in SERVICE_CATALOG.items():
            st.markdown(f"### {category.replace('_', ' ').title()}")
            cols = st.columns(min(len(services), 4))
            for i, (name, info) in enumerate(services.items()):
                with cols[i % len(cols)]:
                    st.metric(name.title(), info["image"].split(":")[0], f"Port {info['port']}")


if __name__ == "__main__":
    main()
