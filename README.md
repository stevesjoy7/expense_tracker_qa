# Expense Tracker (with automated testing)

A simple expense tracker built with Python and FastAPI, designed to
demonstrate software testing practices.

## Planned features
- Add, view, edit, and delete expenses
- Monthly totals by category
- SQLite storage

## Testing plan
- Unit tests (pytest)
- API tests
- UI tests (Playwright)
- CI with GitHub Actions

## Run locally
    pip install -r requirements.txt
    uvicorn app.main:app --reload

## Run tests
    python -m pytest