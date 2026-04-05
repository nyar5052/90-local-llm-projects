#!/usr/bin/env python3
"""Sales Email Generator - Streamlit Web UI."""

import streamlit as st


# Custom CSS for professional dark theme
st.set_page_config(page_title="Sales Email Generator", page_icon="🎯", layout="wide")

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
    TONE_DESCRIPTIONS,
    TEMPLATE_LIBRARY,
    check_ollama_running,
    generate_email,
    generate_variants,
    generate_follow_up_sequence,
    research_prospect,
    score_personalization,
    list_templates,
    get_template,
)

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

st.sidebar.title("✉️ Sales Email Generator")
st.sidebar.markdown("---")

tone = st.sidebar.selectbox(
    "Tone",
    options=list(TONE_DESCRIPTIONS.keys()),
    format_func=lambda t: f"{t.title()} – {TONE_DESCRIPTIONS[t]}",
)

st.sidebar.markdown("---")
st.sidebar.subheader("📋 Quick Templates")
for name in list_templates():
    tmpl = get_template(name)
    st.sidebar.markdown(f"**{name.replace('_', ' ').title()}** – {tmpl['description']}")

# Ollama status
ollama_ok = check_ollama_running()
if ollama_ok:
    st.sidebar.success("✅ Ollama is running")
else:
    st.sidebar.error("❌ Ollama is not running – start with `ollama serve`")

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------

tab_prospect, tab_emails, tab_sequence, tab_templates = st.tabs(
    ["📝 Prospect Form", "✉️ Generated Emails", "📧 Sequence Builder", "📋 Template Browser"]
)

# ---------------------------------------------------------------------------
# Tab 1 – Prospect Form
# ---------------------------------------------------------------------------

with tab_prospect:
    st.header("Prospect Information")
    col1, col2 = st.columns(2)

    with col1:
        prospect_name = st.text_input("Prospect Name", placeholder="Jane Smith")
        company = st.text_input("Company", placeholder="Acme Corp")
        role = st.text_input("Role / Title", placeholder="CTO")

    with col2:
        product = st.text_input("Your Product / Service", placeholder="AI Analytics Platform")
        context = st.text_area("Additional Context", placeholder="Met at SaaS conference last week…")
        follow_up = st.checkbox("Follow-up email")

    prospect_str = f"{role} at {company}" if role and company else prospect_name or ""

    num_variants = st.slider("A/B Variants (0 = single email)", 0, 5, 0)

    generate_btn = st.button("🚀 Generate Email", type="primary", disabled=not ollama_ok)

    if generate_btn and prospect_str and product:
        if num_variants > 0:
            with st.spinner(f"Generating {num_variants} variants…"):
                results = generate_variants(prospect_str, product, tone, num_variants)
            st.session_state["generated_emails"] = results
        else:
            with st.spinner("Generating email…"):
                result = generate_email(prospect_str, product, tone, context, follow_up)
            st.session_state["generated_emails"] = [result]
        st.session_state["prospect_str"] = prospect_str
        st.success("Emails generated! Switch to the **Generated Emails** tab.")
    elif generate_btn:
        st.warning("Please fill in at least Prospect and Product fields.")

# ---------------------------------------------------------------------------
# Tab 2 – Generated Emails
# ---------------------------------------------------------------------------

with tab_emails:
    st.header("Generated Emails")
    emails = st.session_state.get("generated_emails", [])
    p_str = st.session_state.get("prospect_str", "")

    if not emails:
        st.info("No emails generated yet. Use the Prospect Form tab to generate.")
    else:
        for idx, email in enumerate(emails):
            title = f"Variant {idx + 1}" if len(emails) > 1 else "Generated Email"
            with st.expander(f"✉️ {title} – {email['subject']}", expanded=True):
                st.markdown(f"**Subject:** {email['subject']}")
                st.markdown("---")
                st.markdown(email["body"])
                st.code(f"Subject: {email['subject']}\n\n{email['body']}", language="text")

                # Personalisation score
                if p_str and st.button(f"📊 Score Personalisation", key=f"score_{idx}"):
                    with st.spinner("Scoring…"):
                        score_result = score_personalization(email["body"], p_str)
                    col_a, col_b = st.columns([1, 3])
                    with col_a:
                        st.metric("Score", f"{score_result['score']}/100")
                    with col_b:
                        for s in score_result.get("suggestions", []):
                            st.markdown(f"- {s}")

# ---------------------------------------------------------------------------
# Tab 3 – Sequence Builder
# ---------------------------------------------------------------------------

with tab_sequence:
    st.header("Follow-Up Sequence Builder")

    seq_prospect = st.text_input("Prospect", key="seq_prospect", placeholder="VP Engineering at Acme Corp")
    seq_product = st.text_input("Product", key="seq_product", placeholder="DevOps Platform")
    seq_count = st.slider("Emails in sequence", 2, 6, 4)

    seq_btn = st.button("📧 Build Sequence", type="primary", disabled=not ollama_ok)

    if seq_btn and seq_prospect and seq_product:
        with st.spinner(f"Building {seq_count}-email sequence…"):
            seq = generate_follow_up_sequence(seq_prospect, seq_product, tone, seq_count)

        st.markdown("### 📅 Sequence Timeline")
        for i, email in enumerate(seq):
            delay = email.get("delay_days", 0)
            step = email.get("step", "").replace("_", " ").title()
            col_t, col_e = st.columns([1, 4])
            with col_t:
                st.markdown(f"#### Day {delay}")
                st.caption(step)
            with col_e:
                with st.expander(f"✉️ {email['subject']}", expanded=(i == 0)):
                    st.markdown(email["body"])
    elif seq_btn:
        st.warning("Please fill in Prospect and Product fields.")

# ---------------------------------------------------------------------------
# Tab 4 – Template Browser
# ---------------------------------------------------------------------------

with tab_templates:
    st.header("Template Browser")

    template_names = list_templates()
    selected = st.selectbox("Select a template", template_names,
                            format_func=lambda n: n.replace("_", " ").title())

    if selected:
        tmpl = get_template(selected)
        st.markdown(f"### {selected.replace('_', ' ').title()}")
        st.markdown(f"**Description:** {tmpl['description']}")
        st.markdown(f"**Recommended word count:** {tmpl['word_count']}")
        st.markdown("**Structure:**")
        st.text(tmpl.get("structure", "N/A"))

        st.markdown("---")
        st.subheader("Preview with your prospect")
        tmpl_prospect = st.text_input("Prospect", key="tmpl_prospect", placeholder="CMO at enterprise")
        tmpl_product = st.text_input("Product", key="tmpl_product", placeholder="Marketing Analytics")
        if st.button("✨ Generate from Template", disabled=not ollama_ok):
            if tmpl_prospect and tmpl_product:
                with st.spinner("Generating…"):
                    email = generate_email(
                        tmpl_prospect,
                        tmpl_product,
                        tone,
                        context=f"Use the '{selected}' template style: {tmpl['description']}. "
                                f"Structure: {tmpl.get('structure', '')}",
                    )
                st.markdown(f"**Subject:** {email['subject']}")
                st.markdown("---")
                st.markdown(email["body"])
            else:
                st.warning("Please fill in Prospect and Product fields.")
