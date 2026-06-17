"""
Charts module: builds matplotlib figures for the Streamlit app.
"""

import matplotlib.pyplot as plt
import pandas as pd


def category_pie_chart(expenses):
    """Pie chart: spending breakdown by category."""
    if not expenses:
        return None

    df = pd.DataFrame(expenses)
    grouped = df.groupby("category")["amount"].sum().sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.pie(grouped.values, labels=grouped.index, autopct="%1.1f%%", startangle=90)
    ax.set_title("Spending by Category")
    ax.axis("equal")
    return fig


def spending_trend_chart(expenses):
    """Line chart: total spending per day over time."""
    if not expenses:
        return None

    df = pd.DataFrame(expenses)
    df["date"] = pd.to_datetime(df["date"])
    daily = df.groupby("date")["amount"].sum().sort_index()

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(daily.index, daily.values, marker="o", linewidth=2)
    ax.set_title("Spending Trend Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Amount")
    fig.autofmt_xdate()
    return fig


def budget_vs_actual_chart(expenses, budgets):
    """Bar chart: budget limit vs actual spend per category."""
    if not budgets:
        return None

    df = pd.DataFrame(expenses) if expenses else pd.DataFrame(columns=["category", "amount"])
    actual_by_cat = df.groupby("category")["amount"].sum().to_dict() if not df.empty else {}

    categories = [b["category"] for b in budgets]
    limits = [b["limit_amount"] for b in budgets]
    actuals = [actual_by_cat.get(cat, 0) for cat in categories]

    x = range(len(categories))
    fig, ax = plt.subplots(figsize=(7, 4))
    width = 0.35
    ax.bar([i - width / 2 for i in x], limits, width, label="Budget")
    ax.bar([i + width / 2 for i in x], actuals, width, label="Actual")
    ax.set_xticks(list(x))
    ax.set_xticklabels(categories, rotation=30, ha="right")
    ax.set_ylabel("Amount")
    ax.set_title("Budget vs Actual Spending")
    ax.legend()
    fig.tight_layout()
    return fig
