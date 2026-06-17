"""
Database module: SQLite setup and CRUD operations for expenses and budgets.
"""

import sqlite3
from datetime import datetime
from config import DB_NAME


def get_connection():
    """Return a new SQLite connection."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't already exist."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            date TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            month TEXT NOT NULL,
            limit_amount REAL NOT NULL,
            UNIQUE(category, month)
        )
    """)

    conn.commit()
    conn.close()


# ---------------- Expense CRUD ----------------

def add_expense(amount, category, description, date):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO expenses (amount, category, description, date, created_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (amount, category, description, date, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def get_all_expenses():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM expenses ORDER BY date DESC")
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_expenses_by_month(month):
    """month format: 'YYYY-MM'"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM expenses WHERE date LIKE ? ORDER BY date DESC",
        (f"{month}%",),
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def update_expense(expense_id, amount, category, description, date):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE expenses SET amount=?, category=?, description=?, date=? WHERE id=?",
        (amount, category, description, date, expense_id),
    )
    conn.commit()
    conn.close()


def delete_expense(expense_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
    conn.commit()
    conn.close()


# ---------------- Budget CRUD ----------------

def set_budget(category, month, limit_amount):
    """Insert or update a budget limit for a category/month."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO budgets (category, month, limit_amount)
        VALUES (?, ?, ?)
        ON CONFLICT(category, month) DO UPDATE SET limit_amount=excluded.limit_amount
        """,
        (category, month, limit_amount),
    )
    conn.commit()
    conn.close()


def get_budgets_by_month(month):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM budgets WHERE month=?", (month,))
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def delete_budget(budget_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM budgets WHERE id=?", (budget_id,))
    conn.commit()
    conn.close()
