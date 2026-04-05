"""Streamlit Web UI for Math Problem Solver."""

import streamlit as st

# Custom CSS for professional dark theme
st.set_page_config(page_title="Math Problem Solver", page_icon="🎯", layout="wide")

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

import json
import logging

from .core import (
    solve_problem,
    generate_practice_problems,
    get_formula_library,
    check_service,
    MathProblemResult,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

def main():
    st.title("📐 Math Problem Solver")
    st.caption("Powered by Local LLM — Step-by-step solutions with LaTeX output")

    if not check_service():
        st.error("⚠️ Ollama is not running. Start it with: `ollama serve`")
        return

    tab_solve, tab_formulas, tab_practice = st.tabs(
        ["🔢 Solve Problem", "📖 Formula Reference", "🏋️ Practice Mode"]
    )

    # ------------------------------------------------------------------
    # Tab 1: Solve Problem
    # ------------------------------------------------------------------
    with tab_solve:
        col1, col2 = st.columns([3, 1])
        with col1:
            problem = st.text_area(
                "Enter your math problem",
                placeholder="e.g., Solve 2x + 5 = 15",
                height=100,
            )
        with col2:
            category = st.selectbox(
                "Category",
                ["auto-detect", "algebra", "calculus", "geometry", "statistics",
                 "arithmetic", "trigonometry"],
            )
            show_steps = st.checkbox("Show step-by-step solution", value=True)

        if st.button("🚀 Solve", type="primary", use_container_width=True):
            if not problem.strip():
                st.warning("Please enter a math problem.")
            else:
                cat = "" if category == "auto-detect" else category
                with st.spinner("Working on solution..."):
                    try:
                        result = solve_problem(problem, show_steps, cat)
                        _display_solution(result, show_steps)
                    except Exception as e:
                        st.error(f"Error solving problem: {e}")

    # ------------------------------------------------------------------
    # Tab 2: Formula Reference
    # ------------------------------------------------------------------
    with tab_formulas:
        st.subheader("📖 Formula Reference Library")
        selected_cat = st.selectbox(
            "Select Category",
            ["all", "algebra", "geometry", "calculus", "trigonometry"],
            key="formula_cat",
        )
        cat = "" if selected_cat == "all" else selected_cat
        data = get_formula_library(cat)

        if "categories" in data:
            for cat_name, formulas in data["categories"].items():
                with st.expander(f"📐 {cat_name.title()}", expanded=True):
                    _display_formula_table(formulas)
        else:
            _display_formula_table(data.get("formulas", []))

    # ------------------------------------------------------------------
    # Tab 3: Practice Mode
    # ------------------------------------------------------------------
    with tab_practice:
        st.subheader("🏋️ Practice Mode")
        pcol1, pcol2, pcol3 = st.columns(3)
        with pcol1:
            p_category = st.selectbox("Category", ["algebra", "calculus", "geometry",
                                                      "statistics", "trigonometry"], key="p_cat")
        with pcol2:
            p_difficulty = st.selectbox("Difficulty", ["basic", "intermediate", "advanced"], key="p_diff")
        with pcol3:
            p_count = st.slider("Number of problems", 1, 10, 5, key="p_count")

        if st.button("🎯 Generate Practice Problems", use_container_width=True):
            with st.spinner("Generating practice problems..."):
                try:
                    data = generate_practice_problems(p_category, p_difficulty, p_count)
                    _display_practice(data)
                except Exception as e:
                    st.error(f"Error generating problems: {e}")


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------


def _display_solution(result: MathProblemResult, show_steps: bool) -> None:
    st.divider()
    col1, col2, col3 = st.columns(3)
    col1.metric("Category", result.category.title())
    col2.metric("Difficulty", result.difficulty.title())
    col3.metric("Answer", result.solution.answer if result.solution else "N/A")

    if show_steps and result.solution and result.solution.steps:
        st.subheader("📝 Solution Steps")
        for step in result.solution.steps:
            with st.expander(f"Step {step.step_number}: {step.description}", expanded=True):
                if step.work:
                    st.code(step.work, language="text")
                if step.explanation:
                    st.info(step.explanation)

    if result.solution:
        st.success(f"✅ **Answer:** {result.solution.answer}")

    if result.latex_output:
        st.subheader("📄 LaTeX Output")
        st.latex(result.latex_output)

    if result.concepts_used:
        st.subheader("📖 Concepts Used")
        for c in result.concepts_used:
            st.markdown(f"- {c}")

    if result.tips:
        st.subheader("💡 Tips")
        for t in result.tips:
            st.markdown(f"- {t}")

    if result.related_problems:
        st.subheader("🔗 Practice These Next")
        for p in result.related_problems:
            st.markdown(f"- {p}")

    st.download_button(
        "📥 Download Solution (JSON)",
        data=json.dumps(result.to_dict(), indent=2),
        file_name="solution.json",
        mime="application/json",
    )


def _display_formula_table(formulas: list) -> None:
    for f in formulas:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(f"**{f.get('name', '')}**")
            if f.get("latex"):
                st.latex(f["latex"])
        with col2:
            st.markdown(f.get("description", ""))
            st.code(f.get("formula", ""), language="text")


def _display_practice(data: dict) -> None:
    problems = data.get("problems", [])
    for p in problems:
        with st.expander(f"Problem {p.get('number', '?')}: {p.get('problem', '')}", expanded=False):
            st.info(f"💡 **Hint:** {p.get('hint', '')}")
            if st.button(f"Show Answer #{p.get('number', '')}", key=f"ans_{p.get('number')}"):
                st.success(f"**Answer:** {p.get('answer', '')}")


if __name__ == "__main__":
    main()
