#!/usr/bin/env python3
"""Streamlit Web UI for Home Automation Scripter."""

import os
import sys

import streamlit as st

# Ensure package imports work when executed via `streamlit run`
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from home_automation.core import (  # noqa: E402
    PLATFORM_TEMPLATES,
    delete_rule,
    explain_automation,
    generate_automation,
    generate_from_template,
    get_template,
    get_template_categories,
    list_rules,
    list_templates,
    load_config,
    save_rule,
    validate_script,
)

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Home Automation Scripter",
    page_icon="🏠",
    layout="wide",
)

# ---------------------------------------------------------------------------
# LLM availability check
# ---------------------------------------------------------------------------


def _llm_available() -> bool:
    """Return True if Ollama is reachable."""
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        from common.llm_client import check_ollama_running
        return check_ollama_running()
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Session state defaults
# ---------------------------------------------------------------------------

if "config" not in st.session_state:
    cfg_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "config.yaml")
    st.session_state.config = load_config(cfg_path if os.path.exists(cfg_path) else None)

if "generated_script" not in st.session_state:
    st.session_state.generated_script = ""

if "explanation" not in st.session_state:
    st.session_state.explanation = ""

if "llm_ok" not in st.session_state:
    st.session_state.llm_ok = _llm_available()

config = st.session_state.config
platform_names = {k: v["name"] for k, v in PLATFORM_TEMPLATES.items()}

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("🏠 Home Automation")
    st.markdown("---")

    selected_platform = st.selectbox(
        "Default Platform",
        options=list(platform_names.keys()),
        format_func=lambda k: platform_names[k],
        index=list(platform_names.keys()).index(config.get("default_platform", "homeassistant")),
    )

    st.markdown("---")
    page = st.radio("Navigate", ["Rule Builder", "Template Browser", "Saved Rules", "Script Explainer"])

    st.markdown("---")
    if st.session_state.llm_ok:
        st.success("✅ LLM connected")
    else:
        st.warning("⚠️ LLM offline – mock mode")

# ---------------------------------------------------------------------------
# Page: Rule Builder
# ---------------------------------------------------------------------------

if page == "Rule Builder":
    st.header("🔧 Rule Builder")
    st.write("Describe an automation in plain English and generate a production-ready script.")

    rule_text = st.text_area("Describe your automation rule", height=120,
                             placeholder="e.g. Turn off all lights when everyone leaves home")

    col1, col2 = st.columns(2)
    with col1:
        platform = st.selectbox("Platform", list(platform_names.keys()),
                                format_func=lambda k: platform_names[k], key="rb_platform")
    with col2:
        st.write("")  # spacer

    if st.button("🚀 Generate Script", type="primary", disabled=not rule_text):
        if st.session_state.llm_ok:
            with st.spinner("Generating…"):
                st.session_state.generated_script = generate_automation(rule_text, platform, config)
        else:
            st.session_state.generated_script = (
                f"# Mock mode – LLM not available\n# Rule: {rule_text}\n# Platform: {platform}\n"
                "automation:\n  alias: 'Mock Automation'\n  trigger: []\n  action: []"
            )

    if st.session_state.generated_script:
        st.subheader("Generated Script")
        st.code(st.session_state.generated_script, language="yaml")

        vcol1, vcol2 = st.columns(2)
        with vcol1:
            if st.button("✅ Validate"):
                result = validate_script(st.session_state.generated_script, platform)
                if result["valid"]:
                    st.success("Script is valid!")
                else:
                    for err in result["errors"]:
                        st.error(err)
                for warn in result.get("warnings", []):
                    st.warning(warn)
        with vcol2:
            if st.button("💾 Save Rule"):
                save_rule({
                    "description": rule_text,
                    "platform": platform,
                    "script": st.session_state.generated_script,
                }, config)
                st.success("Rule saved!")

# ---------------------------------------------------------------------------
# Page: Template Browser
# ---------------------------------------------------------------------------

elif page == "Template Browser":
    st.header("📦 Template Browser")

    categories = ["all"] + get_template_categories()
    selected_cat = st.selectbox("Filter by category", categories)
    cat_filter = None if selected_cat == "all" else selected_cat

    templates = list_templates(cat_filter)
    if not templates:
        st.info("No templates found for this category.")
    else:
        for tpl in templates:
            with st.expander(f"**{tpl['name']}** — _{tpl['category']}_"):
                st.write(tpl["description"])
                st.write(f"**Parameters:** {', '.join(tpl['parameters'])}")

                with st.form(key=f"tpl_form_{tpl['id']}"):
                    params = {}
                    for p in tpl["parameters"]:
                        params[p] = st.text_input(p, key=f"{tpl['id']}_{p}")
                    tpl_platform = st.selectbox("Platform", list(platform_names.keys()),
                                                format_func=lambda k: platform_names[k],
                                                key=f"tpl_plat_{tpl['id']}")
                    submitted = st.form_submit_button("Generate from template")
                    if submitted:
                        rendered = generate_from_template(tpl["id"], tpl_platform, params)
                        if rendered:
                            st.code(rendered, language="yaml")
                        else:
                            st.warning("Template not available for this platform or missing parameters.")

# ---------------------------------------------------------------------------
# Page: Saved Rules
# ---------------------------------------------------------------------------

elif page == "Saved Rules":
    st.header("📋 Saved Rules")

    rules = list_rules(config)
    if not rules:
        st.info("No saved rules yet. Generate and save one from the Rule Builder.")
    else:
        for rule in rules:
            cols = st.columns([1, 4, 2, 2, 1])
            cols[0].write(f"**#{rule.get('id', '')}**")
            cols[1].write(rule.get("description", ""))
            cols[2].write(rule.get("platform", ""))
            cols[3].write(rule.get("created", "")[:10])
            if cols[4].button("🗑️", key=f"del_{rule.get('id')}"):
                delete_rule(rule["id"], config)
                st.rerun()

# ---------------------------------------------------------------------------
# Page: Script Explainer
# ---------------------------------------------------------------------------

elif page == "Script Explainer":
    st.header("🔍 Script Explainer")
    st.write("Paste an existing automation script and get a plain-English explanation.")

    script_input = st.text_area("Paste script here", height=200)
    explain_platform = st.selectbox("Platform", list(platform_names.keys()),
                                    format_func=lambda k: platform_names[k], key="exp_platform")

    if st.button("📖 Explain", disabled=not script_input):
        if st.session_state.llm_ok:
            with st.spinner("Analysing…"):
                st.session_state.explanation = explain_automation(script_input, explain_platform, config)
        else:
            st.session_state.explanation = (
                "**Mock mode** – LLM not available.\n\n"
                "The script appears to be a home automation rule. "
                "Connect to Ollama for a detailed explanation."
            )

    if st.session_state.explanation:
        st.markdown(st.session_state.explanation)
