"""Streamlit Web UI for CI/CD Pipeline Generator."""

import streamlit as st


# Custom CSS for professional dark theme
st.set_page_config(page_title="CI/CD Pipeline Generator", page_icon="🎯", layout="wide")

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
    generate_pipeline,
    explain_pipeline,
    extract_config,
    validate_pipeline_config,
    PLATFORMS,
    LANGUAGES,
    STAGE_CATALOG,
    MATRIX_PRESETS,
    SECRET_TEMPLATES,
    check_ollama_running,
)


def main():
    st.title("🚀 CI/CD Pipeline Generator")
    st.caption("Generate production-ready CI/CD pipelines with AI")

    if not check_ollama_running():
        st.error("⚠️ Ollama is not running. Start with: `ollama serve`")
        return

    tab_build, tab_explain, tab_ref = st.tabs(["🏗️ Pipeline Builder", "📖 Explain Pipeline", "📚 Reference"])

    # ---- Pipeline Builder Tab ----
    with tab_build:
        col_config, col_output = st.columns([1, 1])

        with col_config:
            st.subheader("🔧 Platform Selection")
            platform = st.selectbox(
                "CI/CD Platform",
                list(PLATFORMS.keys()),
                format_func=lambda x: f"{PLATFORMS[x]['name']} ({PLATFORMS[x]['config_path']})",
            )

            st.subheader("💻 Project Configuration")
            language = st.selectbox("Language", LANGUAGES)
            project_name = st.text_input("Project name (optional)")

            st.subheader("📋 Pipeline Stages")
            st.markdown("Select stages for your pipeline:")
            selected_stages = []
            cols = st.columns(3)
            for i, (stage_name, stage_info) in enumerate(sorted(STAGE_CATALOG.items(), key=lambda x: x[1]["order"])):
                with cols[i % 3]:
                    if st.checkbox(f"{stage_name}", value=stage_name in ("lint", "test", "build"), key=f"stage_{stage_name}"):
                        selected_stages.append(stage_name)

            st.divider()

            st.subheader("🔢 Matrix Builds")
            enable_matrix = st.toggle("Enable matrix builds", value=False)
            if enable_matrix:
                preset = MATRIX_PRESETS.get(language, {"versions": ["latest"], "os": ["ubuntu-latest"]})
                st.info(f"Will test across: {', '.join(preset['versions'])} on {', '.join(preset['os'])}")

            st.subheader("🔐 Secrets Management")
            available_secrets = list(SECRET_TEMPLATES.get(platform, {}).keys())
            selected_secrets = st.multiselect("Secret categories", available_secrets) if available_secrets else []

            generate_btn = st.button("🚀 Generate Pipeline", type="primary", use_container_width=True, disabled=not selected_stages)

        with col_output:
            st.subheader("Generated Pipeline Configuration")

            if generate_btn and selected_stages:
                steps_str = ",".join(selected_stages)
                with st.spinner("Generating pipeline..."):
                    result = generate_pipeline(
                        platform, language, steps_str,
                        project_name or None,
                        enable_matrix,
                        selected_secrets or None,
                    )
                    config_content = extract_config(result)
                    st.session_state["generated_pipeline"] = config_content
                    st.session_state["pipeline_platform"] = platform

            if "generated_pipeline" in st.session_state:
                config_content = st.session_state["generated_pipeline"]
                plat = st.session_state.get("pipeline_platform", platform)
                platform_info = PLATFORMS[plat]

                validation = validate_pipeline_config(config_content, plat)
                if validation["valid"]:
                    st.success("✅ Valid configuration")
                else:
                    for w in validation["warnings"]:
                        st.warning(f"⚠️ {w}")

                # Pipeline visualization
                if selected_stages or "last_stages" in st.session_state:
                    stages = selected_stages or st.session_state.get("last_stages", [])
                    st.markdown("**Pipeline Flow:**")
                    st.markdown(" → ".join([f"`{s}`" for s in stages]))

                st.code(config_content, language=platform_info["lang"])

                st.download_button(
                    f"💾 Download {platform_info['config_path']}",
                    config_content,
                    file_name=platform_info["config_path"].split("/")[-1],
                    mime="text/yaml" if platform_info["lang"] == "yaml" else "text/plain",
                )
            else:
                st.info("Configure your pipeline and click Generate")

    # ---- Explain Tab ----
    with tab_explain:
        st.subheader("📖 Explain an Existing Pipeline")
        explain_platform = st.selectbox("Platform hint", [None] + list(PLATFORMS.keys()), format_func=lambda x: x or "Auto-detect")
        uploaded = st.file_uploader("Upload pipeline config", type=["yml", "yaml", "groovy"])
        paste_content = st.text_area("Or paste pipeline config", height=250)

        content = ""
        if uploaded:
            content = uploaded.read().decode("utf-8")
        elif paste_content:
            content = paste_content

        if content and st.button("🔍 Explain", type="primary"):
            with st.spinner("Analyzing pipeline..."):
                explanation = explain_pipeline(content, explain_platform)
            st.markdown(explanation)

    # ---- Reference Tab ----
    with tab_ref:
        st.subheader("📚 Platform Reference")
        for key, info in PLATFORMS.items():
            with st.expander(f"**{info['name']}**"):
                st.markdown(f"- **Config path:** `{info['config_path']}`")
                st.markdown(f"- **File type:** `.{info['ext']}` ({info['lang']})")
                st.markdown(f"- **Docs:** [{info['docs_url']}]({info['docs_url']})")

        st.subheader("🔢 Matrix Presets")
        for lang, preset in MATRIX_PRESETS.items():
            st.markdown(f"**{lang}**: versions {preset['versions']}")


if __name__ == "__main__":
    main()
