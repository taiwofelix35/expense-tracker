"""
Configuration settings for the Personal Expense Tracker & Budget Management app.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ----- OpenRouter API settings -----
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Free model on OpenRouter (no cost). You can swap this for any model slug
# from https://openrouter.ai/models
AI_MODEL = "meta-llama/llama-3.1-8b-instruct:free"

# ----- Database -----
DB_NAME = "expenses.db"

# ----- Expense categories -----
CATEGORIES = [
    "Food",
    "Transport",
    "Shopping",
    "Bills & Utilities",
    "Entertainment",
    "Health",
    "Education",
    "Rent",
    "Savings",
    "Other",
]
