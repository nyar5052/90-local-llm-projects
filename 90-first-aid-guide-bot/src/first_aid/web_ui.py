"""
First Aid Guide Bot - Streamlit Web UI.

🚨 EMERGENCY DISCLAIMER: This tool is NOT a substitute for emergency medical services.
If someone is seriously injured or in a life-threatening situation, CALL 911 IMMEDIATELY.
This is NOT medical advice. Always seek professional medical help for injuries and illness.
"""

import time

import streamlit as st


# Custom CSS for professional dark theme
st.set_page_config(page_title="First Aid Guide Bot", page_icon="🎯", layout="wide")

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

from first_aid.core import (
    COMMON_SCENARIOS,
    SYSTEM_PROMPT,
    EmergencyContact,
    EmergencyContactManager,
    chat,
    check_ollama_running,
    evaluate_emergency,
    generate,
    get_cpr_steps,
    get_supply_checklist,
)

# ---------------------------------------------------------------------------
# Session state initialization
# ---------------------------------------------------------------------------
if "contact_manager" not in st.session_state:
    st.session_state.contact_manager = EmergencyContactManager()

# ---------------------------------------------------------------------------
# VERY PROMINENT emergency disclaimer
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div style="background-color:#ff0000;padding:16px;border-radius:8px;text-align:center;margin-bottom:8px;">
        <h1 style="color:white;margin:0;">🚨 FOR EMERGENCIES CALL 911 🚨</h1>
        <p style="color:white;font-size:1.2em;margin:4px 0 0 0;">Poison Control: 1-800-222-1222</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.error(
    "⚠️ **EMERGENCY DISCLAIMER** — This tool is **NOT** a substitute for emergency "
    "medical services. This is **NOT** medical advice. For life-threatening emergencies, "
    "**CALL 911** immediately. For poison control, call **1-800-222-1222**. "
    "Always seek professional medical evaluation for injuries."
)

# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------
st.sidebar.title("🏥 First Aid Guide Bot")
page = st.sidebar.radio(
    "Navigate",
    [
        "🏥 Situation Guide",
        "🔀 Emergency Triage",
        "📦 Supply Checklist",
        "❤️ CPR Guide",
        "📞 Emergency Contacts",
    ],
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "**🚨 Emergency Numbers**\n"
    "- **911** — Emergency Services\n"
    "- **1-800-222-1222** — Poison Control\n"
    "- **988** — Crisis Lifeline"
)


# ===================================================================
# PAGE: Situation Guide
# ===================================================================
if page == "🏥 Situation Guide":
    st.header("🏥 Situation Guide")
    st.write("Select a common scenario or describe your situation to receive first aid guidance.")

    scenario_names = [f"{icon} {name}" for name, _, icon, _ in COMMON_SCENARIOS]
    scenario_names.insert(0, "— Select a scenario —")

    selected = st.selectbox("Common scenarios", scenario_names)
    custom_situation = st.text_input("Or describe your situation", placeholder="e.g., minor burn on hand")

    situation = ""
    if selected != "— Select a scenario —":
        situation = selected.split(" ", 1)[1] if " " in selected else selected
    if custom_situation.strip():
        situation = custom_situation.strip()

    if st.button("🏥 Get First Aid Guide", type="primary", disabled=not situation):
        if not check_ollama_running():
            st.error("❌ Ollama is not running. Please start it first.")
        else:
            with st.spinner("Generating first aid instructions…"):
                try:
                    response = generate(
                        prompt=(
                            f"Provide comprehensive first aid instructions for: {situation}\n\n"
                            f"Format your response with:\n"
                            f"1. Emergency warning signs (when to call 911)\n"
                            f"2. Step-by-step first aid instructions (numbered)\n"
                            f"3. What NOT to do (common mistakes)\n"
                            f"4. When to seek professional medical help\n\n"
                            f"Remember: This is for general information only, not medical advice."
                        ),
                        system_prompt=SYSTEM_PROMPT,
                        temperature=0.3,
                        max_tokens=1500,
                    )
                    guide_text = response.get("response", "")
                    if guide_text:
                        st.markdown(guide_text)
                    else:
                        st.warning("No response received. Please try again.")
                except Exception as e:
                    st.error(f"Error: {e}")

            st.warning(
                "⚠️ **Reminder:** This information is for general reference only. "
                "Always seek professional medical evaluation for any injury or illness."
            )

# ===================================================================
# PAGE: Emergency Triage
# ===================================================================
elif page == "🔀 Emergency Triage":
    st.header("🔀 Emergency Triage Assessment")
    st.write("Answer the following questions for a quick triage evaluation.")

    col1, col2, col3 = st.columns(3)
    with col1:
        conscious = st.radio("Is the person conscious?", ["Yes", "No"], index=0) == "Yes"
    with col2:
        breathing = st.radio("Is the person breathing?", ["Yes", "No"], index=0) == "Yes"
    with col3:
        bleeding = st.radio("Is there severe bleeding?", ["Yes", "No"], index=1) == "Yes"

    if st.button("🔀 Evaluate", type="primary"):
        result = evaluate_emergency(conscious, breathing, bleeding)

        severity = result["severity"]
        if severity == "critical":
            color = "red"
        elif severity == "high":
            color = "orange"
        elif severity == "low":
            color = "green"
        else:
            color = "yellow"

        st.markdown(f"### Result: **{result['action']}**")
        st.markdown(f"**Severity:** :{color}[{severity.upper()}]")

        if result["call_911"]:
            st.error("🚨 **CALL 911 IMMEDIATELY**")
        else:
            st.info("Monitor the situation. Seek medical attention if condition worsens.")

        st.markdown("#### Instructions:")
        for i, instruction in enumerate(result["instructions"], 1):
            st.markdown(f"{i}. {instruction}")

# ===================================================================
# PAGE: Supply Checklist
# ===================================================================
elif page == "📦 Supply Checklist":
    st.header("📦 First Aid Supply Checklist")

    tab_all, tab_essential, tab_recommended, tab_optional = st.tabs(
        ["All", "Essential", "Recommended", "Optional"]
    )

    def _render_checklist(items: list[dict], key_prefix: str) -> None:
        checked = 0
        for item in items:
            val = st.checkbox(
                f"**{item['item']}** — {item['quantity']} ({item['purpose']})",
                key=f"{key_prefix}_{item['item']}",
            )
            if val:
                checked += 1
        st.progress(checked / len(items) if items else 0)
        st.caption(f"{checked}/{len(items)} items checked")

    with tab_all:
        _render_checklist(get_supply_checklist("all"), "all")
    with tab_essential:
        _render_checklist(get_supply_checklist("essential"), "ess")
    with tab_recommended:
        _render_checklist(get_supply_checklist("recommended"), "rec")
    with tab_optional:
        _render_checklist(get_supply_checklist("optional"), "opt")

# ===================================================================
# PAGE: CPR Guide
# ===================================================================
elif page == "❤️ CPR Guide":
    st.header("❤️ CPR Guide")
    st.error("🚨 **ALWAYS CALL 911 FIRST** before starting CPR.")

    steps = get_cpr_steps()
    for step in steps:
        duration = step["duration_seconds"]
        timing = f"⏱️ ~{duration}s" if duration > 0 else "🔄 Repeat continuously"
        with st.container():
            st.subheader(f"Step {step['step_number']}: {step['action']}")
            st.write(step["details"])
            st.caption(timing)
            st.divider()

    st.subheader("⏱️ Practice Mode")
    st.write("Use this timer to practice CPR compressions at the correct rate (100-120 per minute).")
    if st.button("▶️ Start 30-Compression Timer"):
        placeholder = st.empty()
        for count in range(1, 31):
            placeholder.markdown(f"### Compression **{count}** / 30")
            time.sleep(0.5)  # ~120 per minute pace
        placeholder.markdown("### ✅ 30 compressions complete — give 2 rescue breaths!")

    st.markdown(
        "**Key Points:**\n"
        "- Push hard and fast (100-120 compressions per minute)\n"
        "- Allow full chest recoil between compressions\n"
        "- Minimize interruptions\n"
        "- Use an AED as soon as one is available"
    )

# ===================================================================
# PAGE: Emergency Contacts
# ===================================================================
elif page == "📞 Emergency Contacts":
    st.header("📞 Emergency Contacts")

    st.error(
        "**Built-in Emergency Numbers:**\n"
        "- 🚨 Emergency Services: **911**\n"
        "- ☠️ Poison Control: **1-800-222-1222**\n"
        "- 💬 Crisis Lifeline: **988**"
    )

    st.subheader("Add a Personal Emergency Contact")
    with st.form("add_contact_form"):
        name = st.text_input("Name")
        number = st.text_input("Phone Number")
        relationship = st.text_input("Relationship")
        is_default = st.checkbox("Set as default contact")
        submitted = st.form_submit_button("➕ Add Contact")

        if submitted and name and number:
            contact = EmergencyContact(
                name=name,
                number=number,
                relationship=relationship,
                is_default=is_default,
            )
            st.session_state.contact_manager.add_contact(contact)
            st.success(f"✅ Added contact: {name} ({number})")

    st.subheader("Your Emergency Contacts")
    all_contacts = st.session_state.contact_manager.get_contacts()
    if all_contacts:
        for c in all_contacts:
            col1, col2, col3, col4 = st.columns([3, 3, 3, 1])
            col1.write(f"**{c.name}**{' ⭐' if c.is_default else ''}")
            col2.write(c.number)
            col3.write(c.relationship)
            if col4.button("🗑️", key=f"del_{c.name}"):
                st.session_state.contact_manager.remove_contact(c.name)
                st.rerun()
    else:
        st.info("No personal emergency contacts saved yet. Use the form above to add one.")
