"""
Nutrition Label Analyzer - Streamlit Web UI.

Provides an interactive web interface for food analysis, daily tracking,
allergen checking, and dietary goal management.

⚠ EDUCATIONAL USE ONLY. Not medical or dietary advice.
"""

import sys
import os

# Ensure common.llm_client is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import streamlit as st

from src.nutrition_analyzer.core import (
    DISCLAIMER,
    DV_REFERENCE,
    COMMON_ALLERGENS,
    PRESET_GOALS,
    MealTracker,
    analyze_food,
    analyze_label,
    compare_foods,
    calculate_daily_values,
    check_allergens,
    check_ollama_running,
)

# ---------------------------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Nutrition Label Analyzer",
    page_icon="🍽️",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Medical Disclaimer (always visible at top)
# ---------------------------------------------------------------------------

st.warning(
    "⚠ **DISCLAIMER:** This tool is for **EDUCATIONAL purposes ONLY**. "
    "Nutrition data and health insights are **AI-generated estimates** and may be "
    "inaccurate. This is **NOT** medical or dietary advice. Always consult a qualified "
    "healthcare professional or registered dietitian before making dietary changes."
)

# ---------------------------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------------------------

if "tracker" not in st.session_state:
    st.session_state.tracker = MealTracker()

# ---------------------------------------------------------------------------
# Sidebar Navigation
# ---------------------------------------------------------------------------

page = st.sidebar.radio(
    "Navigate",
    [
        "🍽️ Food Analysis",
        "📊 Daily Tracker",
        "⚠️ Allergen Check",
        "🎯 Dietary Goals",
    ],
)

# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------


def food_analysis_page():
    """Food analysis page – analyze a single food item via LLM."""
    st.header("🍽️ Food Analysis")
    st.markdown("Enter a food item to get an AI-generated nutritional breakdown.")

    food = st.text_input("Food item", placeholder="e.g. Big Mac, avocado toast, Greek yogurt")

    if st.button("Analyze", type="primary"):
        if not food.strip():
            st.error("Please enter a food item.")
            return

        if not check_ollama_running():
            st.error("Ollama is not running. Please start the Ollama service first.")
            return

        with st.spinner("Analyzing nutrition data..."):
            try:
                result = analyze_food(food.strip())
                st.success("Analysis complete!")
                st.text(result)
            except Exception as e:
                st.error(f"Error during analysis: {e}")

    st.divider()

    st.subheader("📋 Analyze a Nutrition Label")
    label_text = st.text_area("Paste nutrition label text here", height=150)
    if st.button("Analyze Label"):
        if not label_text.strip():
            st.error("Please paste nutrition label text.")
            return
        if not check_ollama_running():
            st.error("Ollama is not running. Please start the Ollama service first.")
            return
        with st.spinner("Analyzing label..."):
            try:
                result = analyze_label(label_text.strip())
                st.success("Label analysis complete!")
                st.text(result)
            except Exception as e:
                st.error(f"Error during label analysis: {e}")

    st.divider()

    st.subheader("⚖️ Compare Foods")
    foods_input = st.text_input("Comma-separated foods", placeholder="Big Mac, Grilled Chicken Salad")
    if st.button("Compare"):
        food_list = [f.strip() for f in foods_input.split(",") if f.strip()]
        if len(food_list) < 2:
            st.error("Please provide at least 2 food items separated by commas.")
            return
        if not check_ollama_running():
            st.error("Ollama is not running.")
            return
        with st.spinner("Comparing..."):
            try:
                result = compare_foods(food_list)
                st.success("Comparison complete!")
                st.text(result)
            except Exception as e:
                st.error(f"Error during comparison: {e}")


def daily_tracker_page():
    """Daily tracker page – add meals and view running totals."""
    st.header("📊 Daily Tracker")
    tracker: MealTracker = st.session_state.tracker

    st.subheader("Add a Meal")
    col1, col2 = st.columns(2)
    with col1:
        meal_name = st.text_input("Meal name", placeholder="Lunch")
    with col2:
        st.markdown("**Nutrient values**")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        cal = st.number_input("Calories", min_value=0, value=0, step=50)
    with c2:
        protein = st.number_input("Protein (g)", min_value=0.0, value=0.0, step=1.0)
    with c3:
        carbs = st.number_input("Carbs (g)", min_value=0.0, value=0.0, step=1.0)
    with c4:
        fat = st.number_input("Fat (g)", min_value=0.0, value=0.0, step=1.0)

    if st.button("Add Meal", type="primary"):
        if not meal_name.strip():
            st.error("Please enter a meal name.")
        else:
            nutrients = {
                "calories": cal,
                "protein": protein,
                "carbs": carbs,
                "fat": fat,
            }
            tracker.add_meal(meal_name.strip(), nutrients)
            st.success(f"Added: {meal_name.strip()}")

    st.divider()

    st.subheader("Today's Meals")
    if tracker.meals:
        for i, m in enumerate(tracker.meals, 1):
            st.markdown(f"**{i}. {m['name']}** — {m['nutrients']}")
    else:
        st.info("No meals tracked yet.")

    st.divider()

    st.subheader("Running Totals")
    totals = tracker.get_daily_totals()
    if totals:
        st.json(totals)
    else:
        st.info("Add meals to see totals.")

    st.subheader("Remaining Budget (Balanced Goal)")
    remaining = tracker.get_remaining_budget()
    st.json(remaining)

    if st.button("🔄 Reset Tracker"):
        tracker.reset()
        st.success("Tracker reset!")
        st.rerun()


def allergen_check_page():
    """Allergen check page – scan food descriptions for allergens."""
    st.header("⚠️ Allergen Check")
    food = st.text_input("Food name or description", placeholder="e.g. peanut butter sandwich with wheat bread")

    selected = st.multiselect(
        "Allergens to check",
        options=COMMON_ALLERGENS,
        default=COMMON_ALLERGENS,
    )

    if st.button("Check Allergens", type="primary"):
        if not food.strip():
            st.error("Please enter a food description.")
            return
        found = check_allergens(food.strip(), selected)
        if found:
            st.error(f"⚠ Potential allergens detected: **{', '.join(found)}**")
        else:
            st.success("✔ No selected allergens detected in the food description.")


def dietary_goals_page():
    """Dietary goals page – view and select macro presets."""
    st.header("🎯 Dietary Goals")

    preset_key = st.selectbox("Select a preset", list(PRESET_GOALS.keys()))
    goal = PRESET_GOALS[preset_key]

    st.markdown(f"### {goal.name}")
    st.metric("Daily Calories", f"{goal.daily_calories} kcal")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Protein", f"{int(goal.protein_pct * 100)}%")
        st.caption(f"≈ {round(goal.daily_calories * goal.protein_pct / 4, 1)}g")
    with col2:
        st.metric("Carbohydrates", f"{int(goal.carb_pct * 100)}%")
        st.caption(f"≈ {round(goal.daily_calories * goal.carb_pct / 4, 1)}g")
    with col3:
        st.metric("Fat", f"{int(goal.fat_pct * 100)}%")
        st.caption(f"≈ {round(goal.daily_calories * goal.fat_pct / 9, 1)}g")

    st.divider()
    st.subheader("All Presets")
    rows = []
    for k, g in PRESET_GOALS.items():
        rows.append({
            "Key": k,
            "Name": g.name,
            "Calories": g.daily_calories,
            "Protein %": int(g.protein_pct * 100),
            "Carb %": int(g.carb_pct * 100),
            "Fat %": int(g.fat_pct * 100),
        })
    st.table(rows)


# ---------------------------------------------------------------------------
# Page Router
# ---------------------------------------------------------------------------

if page == "🍽️ Food Analysis":
    food_analysis_page()
elif page == "📊 Daily Tracker":
    daily_tracker_page()
elif page == "⚠️ Allergen Check":
    allergen_check_page()
elif page == "🎯 Dietary Goals":
    dietary_goals_page()
