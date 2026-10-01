from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Expense Tracker")
expenses = []


class Expense(BaseModel):
    title: str
    amount: float
    category: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/expenses", status_code=201)
def add_expense(expense: Expense):
    expenses.append(expense.model_dump())
    return expense
