#!/usr/bin/env python3
"""Streamlit web interface for the Household Budget Analyzer."""

import sys
import os

# LLM client integration
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import streamlit as st
import pandas as pd
import io

from budget_analyzer.core import (
    load_expenses,
    compute_category_breakdown,
    compute_total,
    filter_by_month,
    analyze_budget,
    compare_months,
    categorize_expense,
    compare_budget_vs_actual,
    SavingsGoal,
    detect_recurring,
    compute_monthly_trends,
    get_top_expenses,
    get_config,
    setup_logging,
)
from common.llm_client import check_ollama_running

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Household Budget Analyzer", page_icon="💰", layout="wide")
setup_logging()

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
st.sidebar.title("💰 Budget Analyzer")

# CSV Upload
st.sidebar.header("📁 Upload Data")
uploaded_file = st.file_uploader("Upload expenses CSV", type=["csv"], label_visibility="collapsed")

# Budget Settings
st.sidebar.header("⚙️ Budget Settings")
config = get_config()
budget_categories = config.get("budget", {}).get("categories", {})

edited_budgets = {}
for cat, default_val in budget_categories.items():
    edited_budgets[cat] = st.sidebar.number_input(
        f"{cat} budget ($)", min_value=0, value=default_val, step=50, key=f"budget_{cat}"
    )

# Savings Goals
st.sidebar.header("🐷 Savings Goals")
goal_name = st.sidebar.text_input("Goal Name", value="Emergency Fund")
goal_target = st.sidebar.number_input("Target ($)", min_value=0.0, value=1000.0, step=100.0)
goal_current = st.sidebar.number_input("Currently Saved ($)", min_value=0.0, value=0.0, step=50.0)
goal_monthly = st.sidebar.number_input("Monthly Contribution ($)", min_value=0.0, value=100.0, step=25.0)

# ---------------------------------------------------------------------------
# Main content
# ---------------------------------------------------------------------------
st.title("💰 Household Budget Analyzer")
st.markdown("*AI-powered expense analysis and budgeting*")

if uploaded_file is not None:
    # Read CSV data
    content = uploaded_file.read().decode("utf-8")
    df = pd.read_csv(io.StringIO(content))
    expenses = df.to_dict("records")

    # Normalize column names
    col_map = {}
    for col in df.columns:
        lower = col.lower()
        if lower in ("date",):
            col_map[col] = "date"
        elif lower in ("category",):
            col_map[col] = "category"
        elif lower in ("description", "desc"):
            col_map[col] = "description"
        elif lower in ("amount",):
            col_map[col] = "amount"
    df = df.rename(columns=col_map)

    # Month filter
    months_available = []
    if "date" in df.columns:
        try:
            df["_parsed_date"] = pd.to_datetime(df["date"], format="mixed", dayfirst=False)
            months_available = sorted(df["_parsed_date"].dt.to_period("M").unique().astype(str))
        except Exception:
            pass

    selected_month = st.selectbox("Filter by Month", ["All"] + months_available)

    filtered_expenses = expenses
    if selected_month != "All":
        from datetime import datetime as _dt
        try:
            parts = selected_month.split("-")
            month_dt = _dt(int(parts[0]), int(parts[1]), 1)
            month_label = month_dt.strftime("%B %Y")
            filtered_expenses = filter_by_month(expenses, month_label)
        except Exception:
            filtered_expenses = expenses

    # Metrics row
    categories = compute_category_breakdown(filtered_expenses)
    total = compute_total(filtered_expenses)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💵 Total Spent", f"${total:,.2f}")
    col2.metric("📊 Categories", str(len(categories)))
    col3.metric("🧾 Transactions", str(len(filtered_expenses)))
    avg_txn = total / len(filtered_expenses) if filtered_expenses else 0
    col4.metric("📈 Avg Transaction", f"${avg_txn:,.2f}")

    st.divider()

    # ---- Tabs ----
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Category Breakdown",
        "📋 Budget vs Actual",
        "🐷 Savings Goals",
        "📈 Monthly Trends",
        "🔄 Recurring Expenses",
        "🤖 AI Analysis",
    ])

    # Tab 1: Category pie chart
    with tab1:
        st.subheader("Category Breakdown")
        if categories:
            cat_df = pd.DataFrame(list(categories.items()), columns=["Category", "Amount"])
            left, right = st.columns(2)
            with left:
                st.bar_chart(cat_df.set_index("Category"))
            with right:
                st.dataframe(cat_df.style.format({"Amount": "${:,.2f}"}), use_container_width=True)
        else:
            st.info("No expense data to display.")

    # Tab 2: Budget vs Actual
    with tab2:
        st.subheader("Budget vs Actual Comparison")
        # Override config with sidebar values
        override_config = dict(config)
        override_config.setdefault("budget", {})["categories"] = edited_budgets
        bva = compare_budget_vs_actual(categories, override_config)
        if bva:
            bva_df = pd.DataFrame(bva)
            bva_df["status_icon"] = bva_df["status"].apply(lambda s: "✅ Under" if s == "under" else "⚠️ Over")
            st.dataframe(
                bva_df[["category", "budget", "actual", "difference", "status_icon"]].rename(
                    columns={"category": "Category", "budget": "Budget", "actual": "Actual",
                             "difference": "Difference", "status_icon": "Status"}
                ).style.format({"Budget": "${:,.2f}", "Actual": "${:,.2f}", "Difference": "${:,.2f}"}),
                use_container_width=True,
            )
            total_budget = sum(r["budget"] for r in bva)
            total_actual = sum(r["actual"] for r in bva)
            bc1, bc2, bc3 = st.columns(3)
            bc1.metric("Total Budget", f"${total_budget:,.2f}")
            bc2.metric("Total Spent", f"${total_actual:,.2f}")
            bc3.metric("Remaining", f"${total_budget - total_actual:,.2f}",
                       delta=f"${total_budget - total_actual:,.2f}")

    # Tab 3: Savings Goals
    with tab3:
        st.subheader("🐷 Savings Goal Tracker")
        goal = SavingsGoal(
            name=goal_name,
            target_amount=goal_target,
            current_amount=goal_current,
            monthly_contribution=goal_monthly,
        )
        progress = goal.track_progress()
        est = goal.estimate_completion()

        gc1, gc2, gc3 = st.columns(3)
        gc1.metric("🎯 Target", f"${progress['target']:,.2f}")
        gc2.metric("💵 Saved", f"${progress['current']:,.2f}")
        gc3.metric("📅 Est. Completion", est or "N/A")

        st.progress(min(progress['percent_complete'] / 100, 1.0), text=f"{progress['percent_complete']}% complete")
        st.caption(f"Remaining: ${progress['remaining']:,.2f}")

    # Tab 4: Monthly Trends
    with tab4:
        st.subheader("Monthly Spending Trends")
        monthly = compute_monthly_trends(expenses)
        if monthly:
            trend_df = pd.DataFrame(list(monthly.items()), columns=["Month", "Total"])
            st.line_chart(trend_df.set_index("Month"))
            st.dataframe(trend_df.style.format({"Total": "${:,.2f}"}), use_container_width=True)
        else:
            st.info("Not enough data for trend analysis.")

        st.subheader("💸 Top Expenses")
        top = get_top_expenses(expenses, n=10)
        if top:
            st.dataframe(
                pd.DataFrame(top).style.format({"amount": "${:,.2f}"}),
                use_container_width=True,
            )

    # Tab 5: Recurring Expenses
    with tab5:
        st.subheader("Recurring Expenses")
        rec = detect_recurring(expenses)
        if rec:
            rec_df = pd.DataFrame(rec)
            rec_df["months"] = rec_df["months"].apply(lambda m: ", ".join(m))
            st.dataframe(
                rec_df.rename(columns={
                    "description": "Description",
                    "avg_amount": "Avg Amount",
                    "occurrences": "Occurrences",
                    "months": "Months",
                }).style.format({"Avg Amount": "${:,.2f}"}),
                use_container_width=True,
            )
            total_rec = sum(r["avg_amount"] for r in rec)
            st.metric("Estimated Monthly Recurring Total", f"${total_rec:,.2f}")
        else:
            st.info("No recurring expenses detected. Upload data spanning multiple months.")

    # Tab 6: AI Analysis
    with tab6:
        st.subheader("🤖 AI Budget Analysis")
        if check_ollama_running():
            if st.button("Run AI Analysis", type="primary"):
                with st.spinner("Analyzing your budget with AI..."):
                    result = analyze_budget(filtered_expenses, categories, total, selected_month)
                st.markdown(result)

            if st.button("Compare Months"):
                with st.spinner("Comparing monthly trends..."):
                    result = compare_months(expenses)
                st.markdown(result)
        else:
            st.warning("⚠️ Ollama is not running. Start with `ollama serve` for AI features.")

else:
    st.info("👈 Upload a CSV file in the sidebar to get started.")
    st.markdown("""
    ### Expected CSV Format
    ```
    date,category,description,amount
    2024-03-01,Groceries,Weekly shopping,150.00
    2024-03-05,Utilities,Electric bill,95.50
    ```

    ### Features
    - 📊 **Category Breakdown** – Visual spending analysis
    - 📋 **Budget vs Actual** – Compare against limits
    - 🐷 **Savings Goals** – Track your progress
    - 📈 **Monthly Trends** – Spending over time
    - 🔄 **Recurring Expenses** – Detect patterns
    - 🤖 **AI Analysis** – Powered by local LLM
    """)
