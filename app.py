"""
Personal Expense Tracker & Budget Management
Main Streamlit application.
"""

import streamlit as st
from datetime import datetime, date
import calendar

from config import CATEGORIES
import database as db
import ai_helper
import charts

# ---------------- Page setup ----------------
st.set_page_config(page_title="Expense Tracker & Budget Manager", layout="wide")
db.init_db()

st.title("💰 Personal Expense Tracker & Budget Management")

current_month = date.today().strftime("%Y-%m")

tab_add, tab_view, tab_budget, tab_insights = st.tabs(
    ["➕ Add Expense", "📊 View & Charts", "🎯 Budgets", "🤖 AI Insights"]
)

# ---------------- TAB 1: Add Expense ----------------
with tab_add:
    st.subheader("Add a new expense")

    col1, col2 = st.columns(2)
    with col1:
        amount = st.number_input("Amount", min_value=0.0, step=0.5, format="%.2f")
        expense_date = st.date_input("Date", value=date.today())
    with col2:
        description = st.text_input("Description", placeholder="e.g. Lunch at campus cafeteria")
        use_ai = st.checkbox("Auto-categorize with AI", value=True)

    manual_category = None
    if not use_ai:
        manual_category = st.selectbox("Category", CATEGORIES)

    if st.button("Add Expense", type="primary"):
        if amount <= 0:
            st.error("Amount must be greater than 0.")
        elif not description:
            st.error("Please enter a description.")
        else:
            if use_ai:
                with st.spinner("Asking AI to categorize..."):
                    category = ai_helper.categorize_expense(description)
                st.info(f"AI categorized this as: **{category}**")
            else:
                category = manual_category

            db.add_expense(amount, category, description, expense_date.strftime("%Y-%m-%d"))
            st.success(f"Expense added: {amount:.2f} ({category}) on {expense_date}")

# ---------------- TAB 2: View & Charts ----------------
with tab_view:
    st.subheader("Your expenses")

    expenses = db.get_all_expenses()

    if not expenses:
        st.info("No expenses recorded yet. Add one in the first tab.")
    else:
        st.dataframe(
            [
                {
                    "ID": str(e["id"]),
                    "Date": e["date"],
                    "Category": e["category"],
                    "Description": e["description"],
                    "Amount": f"{e['amount']:.2f}",
                }
                for e in expenses
            ],
            use_container_width=True,
            column_config={
                "ID": st.column_config.TextColumn("ID", width="small"),
                "Amount": st.column_config.TextColumn("Amount", width="small"),
            },
        )

        st.markdown("#### Delete an expense")
        del_id = st.number_input("Expense ID to delete", min_value=0, step=1)
        if st.button("Delete"):
            db.delete_expense(del_id)
            st.success(f"Deleted expense #{del_id}. Refresh to see updated list.")

        st.markdown("---")
        st.markdown("#### Charts")

        col1, col2 = st.columns(2)
        with col1:
            fig_pie = charts.category_pie_chart(expenses)
            if fig_pie:
                st.pyplot(fig_pie)
        with col2:
            fig_trend = charts.spending_trend_chart(expenses)
            if fig_trend:
                st.pyplot(fig_trend)

# ---------------- TAB 3: Budgets ----------------
with tab_budget:
    st.subheader(f"Set budgets for {calendar.month_name[date.today().month]} {date.today().year}")

    col1, col2 = st.columns(2)
    with col1:
        budget_category = st.selectbox("Category", CATEGORIES, key="budget_cat")
        budget_amount = st.number_input("Monthly limit", min_value=0.0, step=10.0, format="%.2f")

    if st.button("Set Budget"):
        db.set_budget(budget_category, current_month, budget_amount)
        st.success(f"Budget for {budget_category} set to {budget_amount:.2f} for {current_month}")

    st.markdown("---")
    st.markdown("#### Budget vs Actual Spending (this month)")

    month_expenses = db.get_expenses_by_month(current_month)
    month_budgets = db.get_budgets_by_month(current_month)

    if not month_budgets:
        st.info("No budgets set for this month yet.")
    else:
        spent_by_cat = {}
        for e in month_expenses:
            spent_by_cat[e["category"]] = spent_by_cat.get(e["category"], 0) + e["amount"]

        for b in month_budgets:
            spent = spent_by_cat.get(b["category"], 0)
            limit = b["limit_amount"]
            pct = (spent / limit * 100) if limit > 0 else 0

            st.write(f"**{b['category']}**: {spent:.2f} / {limit:.2f} ({pct:.0f}%)")
            st.progress(min(pct / 100, 1.0))

            if pct >= 100:
                st.error(f"⚠️ Over budget for {b['category']}!")
            elif pct >= 80:
                st.warning(f"⚠️ Approaching budget limit for {b['category']}.")

        fig_budget = charts.budget_vs_actual_chart(month_expenses, month_budgets)
        if fig_budget:
            st.pyplot(fig_budget)

# ---------------- TAB 4: AI Insights ----------------
with tab_insights:
    st.subheader("AI-generated spending insights")

    if st.button("Generate Insights", type="primary"):
        month_expenses = db.get_expenses_by_month(current_month)
        month_budgets = db.get_budgets_by_month(current_month)

        with st.spinner("Analyzing your spending..."):
            insight_text = ai_helper.generate_insights(month_expenses, month_budgets)

        st.markdown("### 📋 Summary")
        st.write(insight_text)