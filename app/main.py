from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="Expense Tracker")
expenses = []


class Expense(BaseModel):
    title: str = Field(min_length=1)
    amount: float = Field(gt=0)
    category: str = Field(min_length=1)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/expenses")
def list_expenses():
    return expenses


@app.post("/expenses", status_code=201)
def add_expense(expense: Expense):
    expenses.append(expense.model_dump())
    return expense
