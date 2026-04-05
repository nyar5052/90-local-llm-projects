"""
Streamlit Web UI for the Stress Management Bot.

⚠️ DISCLAIMER: This tool is NOT a substitute for professional mental health care.
If you are in crisis, please contact:
  - 988 Suicide & Crisis Lifeline: Call or text 988
  - Crisis Text Line: Text HOME to 741741
  - Emergency Services: Call 911
"""

import time

import streamlit as st


# Custom CSS for professional dark theme
st.set_page_config(page_title="Stress Management Bot", page_icon="🎯", layout="wide")

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

from stress_manager.core import (
    BREATHING_EXERCISES,
    CBT_WORKSHEETS,
    COPING_TOOLKIT,
    STRESS_QUESTIONS,
    calculate_stress_score,
    get_cbt_worksheet,
    get_coping_suggestions,
)

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Prominent disclaimer
# ---------------------------------------------------------------------------

st.error(
    "⚠️ **IMPORTANT DISCLAIMER** — This tool is **NOT** a substitute for professional "
    "mental health care. It is **NOT medical advice**.\n\n"
    "**If you are in crisis, please contact:**\n"
    "- **988 Suicide & Crisis Lifeline**: Call or text **988**\n"
    "- **Crisis Text Line**: Text HOME to **741741**\n"
    "- **Emergency Services**: Call **911**"
)

# ---------------------------------------------------------------------------
# Session state initialization
# ---------------------------------------------------------------------------

if "journal_entries" not in st.session_state:
    st.session_state.journal_entries = []

# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------

st.sidebar.title("🧘 Stress Management Bot")

page = st.sidebar.radio(
    "Navigate",
    [
        "📊 Stress Assessment",
        "🌬️ Breathing Exercise",
        "🛠️ Coping Tools",
        "📝 Journal",
        "📋 CBT Worksheets",
    ],
)

# Crisis helpline banner in sidebar
st.sidebar.markdown("---")
st.sidebar.error(
    "🆘 **Crisis Helplines**\n\n"
    "- **988** Suicide & Crisis Lifeline\n"
    "- Text HOME → **741741**\n"
    "- Emergency: **911**"
)

# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

if page == "📊 Stress Assessment":
    st.header("📊 Stress Assessment")
    st.write("Rate each area on a scale of 1-10 to receive a personalized stress score.")

    category_keys = [
        "stress_level",
        "sleep_quality",
        "energy_level",
        "anxiety_level",
        "concentration",
    ]

    slider_values: dict[str, int] = {}
    for (question, low, high), cat_key in zip(STRESS_QUESTIONS, category_keys):
        slider_values[cat_key] = st.slider(question, low, high, value=5, key=f"slider_{cat_key}")

    if st.button("Calculate Stress Score", type="primary"):
        result = calculate_stress_score(slider_values)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Score", f"{result['total_score']} / 50")
        with col2:
            severity = result["severity"]
            colour_map = {"low": "🟢", "moderate": "🟡", "high": "🔴", "critical": "🔴🔴"}
            st.metric("Severity", f"{colour_map.get(severity, '')} {severity.upper()}")

        st.subheader("Category Breakdown")
        for cat, info in result["breakdown"].items():
            label = cat.replace("_", " ").title()
            st.write(f"**{label}**: {info['score']}/10 — *{info['severity']}*")

        st.subheader("Recommendations")
        for rec in result["recommendations"]:
            st.write(f"- {rec}")


elif page == "🌬️ Breathing Exercise":
    st.header("🌬️ Breathing Exercise")

    technique = st.selectbox(
        "Choose a technique",
        list(BREATHING_EXERCISES.keys()),
        format_func=lambda k: BREATHING_EXERCISES[k]["name"],
    )
    exercise = BREATHING_EXERCISES[technique]
    st.write(f"**{exercise['name']}** — {exercise['description']}")

    if st.button("Start Exercise", type="primary"):
        placeholder = st.empty()
        progress_bar = st.progress(0)
        total_seconds = sum(d for _, d in exercise["steps"]) * exercise["cycles"]
        elapsed = 0

        for cycle in range(1, exercise["cycles"] + 1):
            for step_name, duration in exercise["steps"]:
                for sec in range(duration):
                    placeholder.markdown(
                        f"### Cycle {cycle}/{exercise['cycles']}  —  **{step_name}**  "
                        f"({sec + 1}/{duration}s)"
                    )
                    elapsed += 1
                    progress_bar.progress(elapsed / total_seconds)
                    time.sleep(1)

        placeholder.markdown("### ✨ Great job! You completed the exercise.")
        progress_bar.progress(1.0)
        st.balloons()


elif page == "🛠️ Coping Tools":
    st.header("🛠️ Coping Toolkit")

    level_filter = st.selectbox(
        "Filter by stress level",
        ["all", "low", "moderate", "high"],
    )

    if level_filter != "all":
        st.subheader(f"Suggestions for {level_filter.upper()} stress")
        suggestions = get_coping_suggestions(level_filter)
        for s in suggestions:
            st.write(f"- {s}")
    else:
        for category, techniques in COPING_TOOLKIT.items():
            with st.expander(f"**{category.upper()}**", expanded=True):
                for t in techniques:
                    st.write(f"- {t}")


elif page == "📝 Journal":
    st.header("📝 Stress Relief Journal")

    st.write("Use the prompt below or write freely about your thoughts and feelings.")

    default_prompt = (
        "What is one thing that brought you peace today, "
        "and how can you create more of that in your life?"
    )
    st.info(f"**Journaling Prompt:** {default_prompt}")

    entry = st.text_area("Write your journal entry here", height=200, key="journal_input")

    if st.button("Save Entry", type="primary"):
        if entry.strip():
            st.session_state.journal_entries.append(entry.strip())
            st.success("Journal entry saved! ✅")
        else:
            st.warning("Please write something before saving.")

    if st.session_state.journal_entries:
        st.subheader("Previous Entries")
        for i, e in enumerate(reversed(st.session_state.journal_entries), 1):
            with st.expander(f"Entry {len(st.session_state.journal_entries) - i + 1}"):
                st.write(e)


elif page == "📋 CBT Worksheets":
    st.header("📋 CBT Worksheets")

    ws_type = st.selectbox(
        "Select a worksheet",
        list(CBT_WORKSHEETS.keys()),
        format_func=lambda k: CBT_WORKSHEETS[k]["name"],
    )

    ws = get_cbt_worksheet(ws_type)
    if ws:
        st.subheader(ws["name"])
        st.write(ws["description"])

        if "columns" in ws:
            st.write("**Fill in the worksheet:**")
            cols = ws["columns"]
            num_rows = st.number_input("Number of rows", min_value=1, max_value=10, value=3)
            for row_idx in range(int(num_rows)):
                st.markdown(f"**Row {row_idx + 1}**")
                row_cols = st.columns(len(cols))
                for col_idx, col_name in enumerate(cols):
                    with row_cols[col_idx]:
                        st.text_input(col_name, key=f"ws_{ws_type}_{row_idx}_{col_idx}")

        if "steps" in ws:
            st.write("**Steps:**")
            for i, step in enumerate(ws["steps"], 1):
                st.write(f"{i}. {step}")
