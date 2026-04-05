"""Streamlit Web UI for Infrastructure Doc Generator."""

import streamlit as st

from .core import (
    generate_docs,
    generate_diagram,
    generate_dependency_map,
    detect_config_type,
    extract_dependencies,
    INPUT_FORMATS,
    DOC_FORMATS,
    check_ollama_running,
)


def main():
    st.set_page_config(page_title="📐 Infra Doc Generator", page_icon="📐", layout="wide")
    st.title("📐 Infrastructure Doc Generator")
    st.caption("Generate comprehensive documentation from infrastructure config files")

    if not check_ollama_running():
        st.error("⚠️ Ollama is not running. Start with: `ollama serve`")
        return

    tab_generate, tab_deps, tab_formats = st.tabs(["📄 Generate Docs", "🔗 Dependency Tree", "📋 Supported Formats"])

    # ---- Generate Docs Tab ----
    with tab_generate:
        col_input, col_output = st.columns([1, 1])

        with col_input:
            st.subheader("📁 Config Upload")
            upload_mode = st.radio("Input method", ["Upload File", "Paste Content"], horizontal=True)

            content = ""
            config_type = ""

            if upload_mode == "Upload File":
                uploaded = st.file_uploader(
                    "Upload infrastructure config",
                    type=["yml", "yaml", "tf", "hcl", "json", "toml", "ini", "conf"],
                )
                if uploaded:
                    content = uploaded.read().decode("utf-8")
                    config_type = detect_config_type(uploaded.name, content)
                    st.success(f"Detected: **{config_type}**")
                    st.code(content[:500] + ("..." if len(content) > 500 else ""), language="yaml")
            else:
                content = st.text_area("Paste config content", height=300, placeholder="Paste your Terraform, Docker Compose, K8s, or other config here...")
                if content:
                    filename = st.text_input("Filename hint (for detection)", value="config.yml")
                    config_type = detect_config_type(filename, content)
                    st.info(f"Detected type: **{config_type}**")

            st.divider()
            output_format = st.selectbox("Output format", DOC_FORMATS)
            include_diagram = st.toggle("Include architecture diagram", value=True)

            generate_btn = st.button("📝 Generate Documentation", type="primary", use_container_width=True, disabled=not content)

        with col_output:
            st.subheader("📄 Generated Documentation")

            if generate_btn and content:
                with st.spinner("Generating documentation..."):
                    result = generate_docs(content, config_type, output_format, include_diagram)
                    st.session_state["generated_docs"] = result

            if "generated_docs" in st.session_state:
                st.markdown(st.session_state["generated_docs"])
                st.download_button(
                    "💾 Download Documentation",
                    st.session_state["generated_docs"],
                    file_name=f"infra-docs.{'md' if output_format == 'markdown' else 'txt'}",
                    mime="text/markdown" if output_format == "markdown" else "text/plain",
                )
            else:
                st.info("Upload a config file and click Generate to create documentation")

    # ---- Dependency Tree Tab ----
    with tab_deps:
        st.subheader("🔗 Dependency Tree")

        dep_uploaded = st.file_uploader("Upload config for dependency analysis", type=["yml", "yaml", "tf", "json"], key="dep_upload")
        dep_content = ""

        if dep_uploaded:
            dep_content = dep_uploaded.read().decode("utf-8")
            dep_type = detect_config_type(dep_uploaded.name, dep_content)

            # Local dependency extraction
            local_deps = extract_dependencies(dep_content, dep_type)
            if local_deps:
                st.markdown("### 📊 Detected Dependencies")
                for dep in local_deps:
                    st.markdown(f"- `{dep['from']}` → `{dep['to']}` ({dep['type']})")

            if st.button("🔍 Generate Full Dependency Map", type="primary"):
                with st.spinner("Analyzing dependencies..."):
                    dep_result = generate_dependency_map(dep_content, dep_type)
                st.markdown(dep_result)

            if st.button("📐 Generate Architecture Diagram"):
                with st.spinner("Generating diagram..."):
                    diagram_result = generate_diagram(dep_content, dep_type)
                st.code(diagram_result, language="text")

    # ---- Formats Tab ----
    with tab_formats:
        st.subheader("📋 Supported Input Formats")
        for key, info in INPUT_FORMATS.items():
            with st.expander(f"**{info['name']}** ({key})"):
                st.markdown(f"- **Extensions:** {', '.join(info['extensions'])}")
                st.markdown(f"- **Detection indicators:** {', '.join(info['indicators'])}")

        st.subheader("📄 Output Formats")
        for fmt in DOC_FORMATS:
            st.markdown(f"- **{fmt.title()}**")


if __name__ == "__main__":
    main()
