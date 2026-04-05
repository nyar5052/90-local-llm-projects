"""Streamlit Web UI for Password Strength Advisor."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

import streamlit as st


# Custom CSS for professional dark theme
st.set_page_config(page_title="Password Strength Advisor", page_icon="🎯", layout="wide")

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

from src.password_advisor.core import (
    calculate_entropy,
    check_breach_database,
    generate_policy,
    analyze_password_llm,
    generate_password,
    bulk_analyze,
    StrengthLevel,
)
from src.password_advisor.config import load_config

STRENGTH_COLORS = {
    StrengthLevel.VERY_STRONG: "🟢",
    StrengthLevel.STRONG: "🟢",
    StrengthLevel.FAIR: "🟡",
    StrengthLevel.WEAK: "🟠",
    StrengthLevel.VERY_WEAK: "🔴",
}

config = load_config()


def main():
    st.title("🔑 Password Strength Advisor")
    st.caption("Entropy Analysis, Breach Detection, Policy Generation & Bulk Analysis")

    with st.sidebar:
        st.header("⚙️ Settings")
        show_password = st.checkbox("Show password text", value=False)
        st.divider()
        st.markdown("### 🔐 Quick Generate")
        gen_length = st.slider("Length", 8, 64, 16)
        if st.button("Generate Password"):
            pwd = generate_password(gen_length)
            st.code(pwd, language=None)
            ent = calculate_entropy(pwd)
            st.metric("Entropy", f"{ent.entropy_bits:.0f} bits")

    tab_input, tab_meter, tab_policy, tab_bulk = st.tabs(
        ["🔑 Password Input", "📊 Strength Meter", "📋 Policy Editor", "📦 Bulk Analyzer"]
    )

    with tab_input:
        st.subheader("Enter Password to Analyze")
        password = st.text_input(
            "Password",
            type="default" if show_password else "password",
            placeholder="Enter password to analyze...",
        )

        col1, col2 = st.columns(2)
        with col1:
            analyze_btn = st.button("🔍 Analyze", type="primary", use_container_width=True)
        with col2:
            breach_btn = st.button("🛡️ Breach Check", use_container_width=True)

        if analyze_btn and password:
            ent = calculate_entropy(password)
            st.session_state["entropy"] = ent
            breach = check_breach_database(password)
            st.session_state["breach"] = breach

        if breach_btn and password:
            breach = check_breach_database(password)
            if breach.is_compromised:
                st.error(f"⚠️ COMPROMISED: {breach.recommendation}")
            else:
                st.success(f"✅ {breach.recommendation}")

    with tab_meter:
        st.subheader("📊 Password Strength Meter")
        if "entropy" in st.session_state:
            ent = st.session_state["entropy"]
            icon = STRENGTH_COLORS.get(ent.strength, "⚪")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Entropy", f"{ent.entropy_bits:.1f} bits")
            with col2:
                st.metric("Strength", f"{icon} {ent.strength.value.replace('_', ' ').title()}")
            with col3:
                st.metric("Time to Crack", ent.time_to_crack)

            # Strength bar
            strength_pct = min(ent.entropy_bits / 100.0, 1.0)
            st.progress(strength_pct, text=f"Entropy: {ent.entropy_bits:.1f} / 100 bits")

            st.divider()
            col4, col5 = st.columns(2)
            with col4:
                st.markdown("#### Character Composition")
                st.markdown(f"- Charset size: **{ent.charset_size}**")
                st.markdown(f"- Effective length: **{ent.effective_length}**")
                st.markdown(f"- Character types: **{ent.details.get('char_types', 0)}/4**")
            with col5:
                st.markdown("#### Checks")
                if "breach" in st.session_state:
                    breach = st.session_state["breach"]
                    if breach.is_compromised:
                        st.error(f"Found in breach database ({breach.source})")
                    else:
                        st.success("Not found in breach database")
        else:
            st.info("Analyze a password from the Password Input tab.")

    with tab_policy:
        st.subheader("📋 Password Policy Editor")
        rules = generate_policy()
        st.markdown("*Based on NIST SP 800-63B recommendations*")

        for rule in rules:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{rule.name}:** {rule.description}")
            with col2:
                st.checkbox("Enabled", value=rule.enabled, key=f"policy_{rule.name}", disabled=True)

    with tab_bulk:
        st.subheader("📦 Bulk Password Analyzer")
        passwords_text = st.text_area(
            "Enter passwords (one per line):",
            height=200,
            placeholder="password123\nMyStr0ng!Pass\nsecret",
        )
        uploaded = st.file_uploader("Or upload a file", type=["txt", "csv"])
        if uploaded:
            passwords_text = uploaded.read().decode("utf-8", errors="replace")

        if st.button("📊 Analyze All", use_container_width=True) and passwords_text.strip():
            passwords = [p.strip() for p in passwords_text.splitlines() if p.strip()]
            results = bulk_analyze(passwords)

            data = [{
                "#": r.index + 1,
                "Masked": r.masked,
                "Entropy": f"{r.entropy:.0f}b",
                "Strength": f"{STRENGTH_COLORS.get(r.strength, '⚪')} {r.strength.value}",
                "Issues": ", ".join(r.issues) if r.issues else "✅",
            } for r in results]
            st.dataframe(data, use_container_width=True)

            # Summary
            weak_count = sum(1 for r in results if r.strength in (StrengthLevel.VERY_WEAK, StrengthLevel.WEAK))
            st.metric("Weak Passwords", f"{weak_count}/{len(results)}")


if __name__ == "__main__":
    main()
