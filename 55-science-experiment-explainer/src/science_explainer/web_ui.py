#!/usr/bin/env python3
"""
Science Experiment Explainer — Streamlit Web UI.

Launch with:  streamlit run src/science_explainer/web_ui.py
"""

import json
import streamlit as st


# Custom CSS for professional dark theme
st.set_page_config(page_title="Science Experiment Explainer", page_icon="🎯", layout="wide")

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
    check_ollama_running,
    explain_experiment,
    search_experiments,
    export_experiment,
    validate_experiment_data,
    SafetyDatabase,
    EquipmentManager,
    ConfigManager,
)

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

config = ConfigManager()
safety_db = SafetyDatabase()
equip_mgr = EquipmentManager()

SUBJECTS = config.get("experiment", "subjects", [
    "Chemistry", "Physics", "Biology", "Earth Science", "Environmental Science",
])
GRADE_LEVELS = config.get("experiment", "grade_levels", [
    "elementary", "middle school", "high school", "college",
])
DIFFICULTY_LABELS = {1: "Beginner", 2: "Intermediate", 3: "Advanced", 4: "Expert"}

# ---------------------------------------------------------------------------
# Sidebar — search / filter options
# ---------------------------------------------------------------------------

with st.sidebar:
    st.header("🔎 Search & Filter")
    subject_filter = st.selectbox("Subject", ["All"] + SUBJECTS)
    grade_filter = st.selectbox("Grade Level", ["All"] + GRADE_LEVELS)
    difficulty_filter = st.select_slider(
        "Difficulty",
        options=list(DIFFICULTY_LABELS.values()),
        value="Beginner",
    )
    st.divider()
    st.caption("🔬 Science Experiment Explainer v1.0.0")

# ---------------------------------------------------------------------------
# Connection check
# ---------------------------------------------------------------------------

ollama_ok = check_ollama_running()

# ---------------------------------------------------------------------------
# Main area — tabs
# ---------------------------------------------------------------------------

tab_explore, tab_guide, tab_safety, tab_materials = st.tabs([
    "🔬 Explore Experiment",
    "📋 Step-by-Step Guide",
    "🛡️ Safety Center",
    "📦 Materials & Equipment",
])

# ---- Explore Experiment ---------------------------------------------------

with tab_explore:
    st.header("🔬 Explore Experiment")

    if not ollama_ok:
        st.error("⚠️ Ollama is not running. Start it with `ollama serve`.")

    col1, col2 = st.columns([3, 1])
    with col1:
        experiment_name = st.text_input("Experiment name", placeholder="e.g. baking soda volcano")
    with col2:
        detail_level = st.selectbox("Detail", ["brief", "medium", "detailed"], index=1)

    level = grade_filter if grade_filter != "All" else "middle school"

    if st.button("🚀 Generate Explanation", type="primary", disabled=not ollama_ok):
        if not experiment_name:
            st.warning("Please enter an experiment name.")
        else:
            with st.spinner("Researching experiment..."):
                try:
                    data = explain_experiment(experiment_name, level, detail_level)
                    st.session_state["experiment_data"] = data
                except Exception as exc:
                    st.error(f"Error: {exc}")

    if "experiment_data" in st.session_state:
        data = st.session_state["experiment_data"]
        errors = validate_experiment_data(data)
        if errors:
            for e in errors:
                st.warning(f"⚠️ {e}")

        st.subheader(data.get("experiment_name", "Experiment"))
        c1, c2, c3 = st.columns(3)
        c1.metric("Subject", data.get("subject", "N/A"))
        c2.metric("Grade Level", data.get("grade_level", "N/A"))
        c3.metric("Duration", data.get("duration", "N/A"))

        if data.get("objective"):
            st.info(f"🎯 **Objective:** {data['objective']}")
        if data.get("scientific_concepts"):
            st.write("**📖 Scientific Concepts:**")
            for c in data["scientific_concepts"]:
                st.write(f"- {c}")
        if data.get("explanation"):
            with st.expander("🧪 Why It Works", expanded=False):
                st.write(data["explanation"])
        if data.get("variations"):
            with st.expander("🔄 Variations to Try"):
                for v in data["variations"]:
                    st.write(f"- {v}")
        if data.get("discussion_questions"):
            with st.expander("❓ Discussion Questions"):
                for i, q in enumerate(data["discussion_questions"], 1):
                    st.write(f"{i}. {q}")

    st.divider()
    st.subheader("🔍 Search Experiments")
    search_topic = st.text_input("Search topic", placeholder="e.g. chemical reactions")
    if st.button("Search", disabled=not ollama_ok):
        if search_topic:
            with st.spinner("Searching..."):
                try:
                    subj = subject_filter if subject_filter != "All" else ""
                    results = search_experiments(search_topic, subj, difficulty_filter)
                    for r in results:
                        st.write(f"- **{r.get('name', '')}** ({r.get('subject', '')}) — {r.get('description', '')}")
                except Exception as exc:
                    st.error(f"Search error: {exc}")

# ---- Step-by-Step Guide ---------------------------------------------------

with tab_guide:
    st.header("📋 Step-by-Step Guide")
    if "experiment_data" not in st.session_state:
        st.info("Generate an experiment on the *Explore* tab first.")
    else:
        data = st.session_state["experiment_data"]
        steps = data.get("procedure", [])
        total = len(steps)
        if total == 0:
            st.warning("No procedure steps found.")
        else:
            completed = 0
            for step in steps:
                num = step.get("step", "?")
                done = st.checkbox(
                    f"Step {num}: {step.get('instruction', '')}",
                    key=f"step_{num}",
                )
                if done:
                    completed += 1
                if step.get("tip"):
                    st.caption(f"💡 Tip: {step['tip']}")

            progress = completed / total
            st.progress(progress, text=f"{completed}/{total} steps completed")

        if data.get("expected_results"):
            st.success(f"📊 **Expected Results:** {data['expected_results']}")

# ---- Safety Center --------------------------------------------------------

with tab_safety:
    st.header("🛡️ Safety Center")
    if "experiment_data" not in st.session_state:
        st.info("Generate an experiment on the *Explore* tab first.")
    else:
        data = st.session_state["experiment_data"]
        level_key = data.get("grade_level", "middle school")

        # Age appropriateness
        age_ok = safety_db.check_age_appropriate(data, level_key)
        if age_ok:
            st.success("✅ This experiment is age-appropriate for the selected grade level.")
        else:
            st.error("🚫 This experiment may NOT be appropriate for the selected grade level.")

        # Overall risk
        risk = safety_db.get_risk_level(data)
        risk_icons = {"low": "🟢", "medium": "🟡", "high": "🟠", "critical": "🔴"}
        st.write(f"**Overall Risk Level:** {risk_icons.get(risk, '⚪')} {risk.upper()}")

        # Safety precautions
        if data.get("safety_precautions"):
            st.subheader("⚠️ Safety Warnings")
            for p in data["safety_precautions"]:
                st.warning(p)

        # Material-specific safety
        st.subheader("🧪 Material Safety")
        for mat in data.get("materials", []):
            info = safety_db.get_safety_info(mat.get("item", ""))
            if info:
                icon = risk_icons.get(info.level, "⚪")
                st.write(f"{icon} **{mat.get('item', '')}** — {info.description}")
                st.caption(f"   Precaution: {info.precaution}")

        # Required PPE
        st.subheader("🥽 Required PPE")
        ppe = safety_db.get_required_ppe(data)
        for item in ppe:
            st.checkbox(item, key=f"ppe_{item}")

# ---- Materials & Equipment ------------------------------------------------

with tab_materials:
    st.header("📦 Materials & Equipment")
    if "experiment_data" not in st.session_state:
        st.info("Generate an experiment on the *Explore* tab first.")
    else:
        data = st.session_state["experiment_data"]

        # Materials checklist
        st.subheader("🧾 Materials Checklist")
        for mat in data.get("materials", []):
            label = f"{mat.get('item', '')} — {mat.get('quantity', '')}"
            if mat.get("notes"):
                label += f" ({mat['notes']})"
            st.checkbox(label, key=f"mat_{mat.get('item', '')}")

        # Equipment
        st.subheader("🔧 Equipment")
        equip_list = equip_mgr.get_equipment_list(data)
        if equip_list:
            for eq in equip_list:
                st.write(f"- **{eq.name}** — {eq.description}")
                if eq.alternatives:
                    st.caption(f"  Alternatives: {', '.join(eq.alternatives)}")
        else:
            st.write("No specialised equipment detected.")

        # Cost estimate
        st.subheader("💰 Cost Estimate")
        equip_names = [e.name for e in equip_list]
        cost = equip_mgr.estimate_cost(equip_names)
        st.metric("Estimated Equipment Cost", f"${cost:.2f}")

        # Substitute suggestions
        st.subheader("♻️ Substitute Suggestions")
        for mat in data.get("materials", []):
            alts = equip_mgr.suggest_alternatives(mat.get("item", ""))
            if alts:
                st.write(f"- **{mat.get('item', '')}** → {', '.join(alts)}")

        # Printable shopping list
        st.divider()
        if st.button("🖨️ Generate Printable Shopping List"):
            lines = ["SHOPPING LIST", "=" * 40]
            for mat in data.get("materials", []):
                lines.append(f"☐ {mat.get('item', '')} — {mat.get('quantity', '')}")
            st.code("\n".join(lines), language="text")

        # Export
        st.divider()
        st.subheader("📤 Export")
        exp_fmt = st.selectbox("Format", ["json", "markdown", "checklist"])
        exported = export_experiment(data, exp_fmt)
        st.download_button("Download", data=exported, file_name=f"experiment.{exp_fmt if exp_fmt != 'checklist' else 'txt'}")
