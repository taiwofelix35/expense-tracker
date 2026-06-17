# Setup Guide — Personal Expense Tracker & Budget Management

## 1. Unzip the project
Extract `expense_tracker.zip` and open a terminal inside the `expense_tracker` folder.

## 2. Check Python is installed
Python 3.9+ is required.
```
python3 --version
```

## 3. Install dependencies
```
pip install -r requirements.txt
```

## 4. Get an OpenRouter API key
1. Go to [openrouter.ai](https://openrouter.ai) and sign up.
2. Open the **Keys** section.
3. Create a new API key (free tier works with the default model).

## 5. Add your API key
Place the `.env` file (provided separately) into the `expense_tracker` folder, then open it and replace the placeholder:
```
OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here
```

## 6. Run the app
```
streamlit run app.py
```

## 7. Open in browser
It should open automatically at:
```
http://localhost:8501
```
If not, paste that URL into your browser manually.

## 8. Database
`expenses.db` (SQLite) is created automatically on first run — no manual setup needed.

## 9. Test it
Add an expense in the **Add Expense** tab with AI auto-categorize checked, and confirm it returns a category. Then try **AI Insights** to confirm the API key is working end to end.
