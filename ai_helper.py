"""
AI helper module: handles calls to the OpenRouter API for
(1) auto-categorizing expenses from their description, and
(2) generating natural-language spending insights.
"""

import json
import requests
from config import OPENROUTER_API_KEY, OPENROUTER_URL, AI_MODEL, CATEGORIES


def _call_openrouter(messages, max_tokens=300):
    """
    Low-level helper to call the OpenRouter chat completions endpoint.
    Returns a tuple: (result_text_or_None, error_message_or_None)
    """
    if not OPENROUTER_API_KEY:
        return None, "OPENROUTER_API_KEY is empty or missing in this environment."

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": AI_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
    }

    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip(), None
    except requests.exceptions.HTTPError as e:
        # Try to pull OpenRouter's own error message out of the response body
        detail = ""
        try:
            detail = e.response.json().get("error", {}).get("message", "")
        except Exception:
            detail = e.response.text[:200] if e.response is not None else ""
        return None, f"HTTP {e.response.status_code if e.response is not None else '?'} - {detail}"
    except Exception as e:
        return None, str(e)


def categorize_expense(description):
    """
    Ask the AI to pick the best matching category for an expense description.
    Falls back to 'Other' if the API call fails or returns something unexpected.
    """
    if not description:
        return "Other"

    category_list = ", ".join(CATEGORIES)
    messages = [
        {
            "role": "system",
            "content": (
                "You are an expense categorization assistant. "
                f"Given an expense description, reply with exactly ONE category "
                f"from this list, nothing else: {category_list}."
            ),
        },
        {"role": "user", "content": f"Expense description: {description}"},
    ]

    result, error = _call_openrouter(messages, max_tokens=20)

    if result:
        # Match the AI's reply against known categories (case-insensitive)
        cleaned = result.strip().strip(".").strip()
        for cat in CATEGORIES:
            if cat.lower() == cleaned.lower() or cat.lower() in cleaned.lower():
                return cat

    return "Other"


def generate_insights(expenses, budgets):
    """
    Given a list of expense dicts and budget dicts for the current month,
    ask the AI to generate a short natural-language spending summary and advice.
    """
    if not expenses:
        return "No expenses recorded yet this month. Add some expenses to get insights!"

    total = sum(e["amount"] for e in expenses)
    by_category = {}
    for e in expenses:
        by_category[e["category"]] = by_category.get(e["category"], 0) + e["amount"]

    summary_data = {
        "total_spent": round(total, 2),
        "spending_by_category": {k: round(v, 2) for k, v in by_category.items()},
        "budgets": {b["category"]: b["limit_amount"] for b in budgets},
    }

    messages = [
        {
            "role": "system",
            "content": (
                "You are a friendly personal finance assistant. Given a user's "
                "monthly spending data and budgets (in JSON), write a concise "
                "3-5 sentence summary: highlight the top spending category, "
                "flag any category that is over or close to its budget, and give "
                "one practical money-saving tip. Keep it conversational, no markdown."
            ),
        },
        {"role": "user", "content": json.dumps(summary_data)},
    ]

    result, error = _call_openrouter(messages, max_tokens=250)

    if result:
        return result

    # Fallback if API call fails: simple rule-based summary
    top_category = max(by_category, key=by_category.get)
    return (
        f"You spent a total of {total:.2f} this month. "
        f"Your top spending category was {top_category} "
        f"({by_category[top_category]:.2f}). "
        f"(AI insights unavailable right now — {error or 'unknown error'})"
    )
