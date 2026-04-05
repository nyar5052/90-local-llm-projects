"""Streamlit web interface for Meal Planner Bot."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

import streamlit as st

from .config import load_config, setup_logging
from .core import (
    check_ollama_running,
    generate_meal_plan,
    get_recipe_details,
    generate_shopping_list,
    DIETS,
)
from .utils import parse_calories_from_plan, total_calories, save_recipe, load_saved_recipes

st.set_page_config(page_title="🍽️ Meal Planner Bot", page_icon="🍽️", layout="wide")


def init_state():
    defaults = {"config": load_config(), "meal_plan": "", "shopping_list": ""}
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def sidebar():
    cfg = st.session_state.config
    st.sidebar.title("⚙️ Settings")
    cfg["model"]["name"] = st.sidebar.text_input("Model", value=cfg["model"]["name"])
    cfg["model"]["temperature"] = st.sidebar.slider("Temperature", 0.0, 1.0, cfg["model"]["temperature"], 0.1)
    st.sidebar.markdown("---")
    st.sidebar.subheader("📚 Saved Recipes")
    recipes = load_saved_recipes(cfg.get("storage", {}).get("recipes_file", "saved_recipes.json"))
    if recipes:
        for r in recipes[-8:]:
            st.sidebar.markdown(f"- **{r['name']}** ({r['diet']})")
    else:
        st.sidebar.info("No saved recipes yet.")


def main():
    init_state()
    cfg = st.session_state.config
    setup_logging(cfg)

    st.title("🍽️ Meal Planner Bot")
    st.caption("Generate personalized meal plans, shopping lists, and recipes.")

    sidebar()

    tab_plan, tab_shop, tab_recipe = st.tabs(["📋 Meal Plan", "🛒 Shopping List", "📖 Recipe Lookup"])

    with tab_plan:
        col1, col2, col3, col4 = st.columns(4)
        diet = col1.selectbox("Diet", DIETS, index=0)
        days = col2.number_input("Days", 1, 14, 7)
        allergies = col3.text_input("Allergies", placeholder="nuts, dairy...")
        cal_target = col4.number_input("Daily Calories (0 = any)", 0, 5000, 0, step=100)

        if st.button("🍽️ Generate Meal Plan", type="primary"):
            if not check_ollama_running():
                st.error("❌ Ollama is not running.")
                return
            with st.spinner(f"Generating {days}-day {diet} meal plan..."):
                plan = generate_meal_plan(
                    diet, days,
                    allergies=allergies if allergies else None,
                    calories=cal_target if cal_target > 0 else None,
                    model=cfg["model"]["name"],
                    temperature=cfg["model"]["temperature"],
                )
                st.session_state.meal_plan = plan

        if st.session_state.meal_plan:
            st.markdown(st.session_state.meal_plan)
            cal_entries = parse_calories_from_plan(st.session_state.meal_plan)
            if cal_entries:
                st.metric("🔥 Total Estimated Calories", total_calories(cal_entries))

    with tab_shop:
        if st.session_state.meal_plan:
            if st.button("🛒 Generate Shopping List"):
                with st.spinner("Building shopping list..."):
                    sl = generate_shopping_list(st.session_state.meal_plan, model=cfg["model"]["name"])
                    st.session_state.shopping_list = sl
            if st.session_state.shopping_list:
                st.markdown(st.session_state.shopping_list)
        else:
            st.info("Generate a meal plan first to get a shopping list.")

    with tab_recipe:
        meal_name = st.text_input("Meal name")
        diet_for_recipe = st.selectbox("Diet for recipe", DIETS, index=0, key="recipe_diet")
        if st.button("📖 Get Recipe") and meal_name:
            with st.spinner("Looking up recipe..."):
                recipe = get_recipe_details(meal_name, diet_for_recipe, model=cfg["model"]["name"])
            st.markdown(recipe)
            save_recipe(meal_name, recipe, diet_for_recipe, cfg.get("storage", {}).get("recipes_file", "saved_recipes.json"))
            st.success(f"Recipe for '{meal_name}' saved!")


if __name__ == "__main__":
    main()
