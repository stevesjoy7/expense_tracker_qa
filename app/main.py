import datetime

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

app = FastAPI(title="Expense Tracker")
expenses = []


class Expense(BaseModel):
    title: str = Field(min_length=1)
    amount: float = Field(gt=0)
    category: str = Field(min_length=1)
    date: datetime.date


def _next_id():
    return max((e["id"] for e in expenses), default=0) + 1


def _find(expense_id: int):
    for e in expenses:
        if e["id"] == expense_id:
            return e
    raise HTTPException(status_code=404, detail="Expense not found")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/expenses")
def list_expenses():
    return expenses


@app.get("/expenses/{expense_id}")
def get_expense(expense_id: int):
    return _find(expense_id)


@app.post("/expenses", status_code=201)
def add_expense(expense: Expense):
    record = {"id": _next_id(), **expense.model_dump()}
    expenses.append(record)
    return record


@app.put("/expenses/{expense_id}")
def update_expense(expense_id: int, expense: Expense):
    record = _find(expense_id)
    record.update(expense.model_dump())
    return record


@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int):
    record = _find(expense_id)
    expenses.remove(record)
    return {"message": "Expense deleted"}


@app.get("/summary")
def monthly_summary(
    year: int = Query(ge=2000, le=2100),
    month: int = Query(ge=1, le=12),
):
    by_category = {}
    for e in expenses:
        if e["date"].year == year and e["date"].month == month:
            by_category[e["category"]] = by_category.get(
                e["category"], 0) + e["amount"]
    by_category = {k: round(v, 2) for k, v in by_category.items()}
    return {
        "year": year,
        "month": month,
        "total": round(sum(by_category.values()), 2),
        "by_category": by_category,
    }
