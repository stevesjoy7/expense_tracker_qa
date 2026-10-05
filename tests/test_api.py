import pytest
from fastapi.testclient import TestClient
from app.main import app, expenses

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_expenses():
    expenses.clear()


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_add_expense():
    payload = {"title": "Milk", "amount": 55.0, "category": "Groceries"}
    response = client.post("/expenses", json=payload)
    assert response.status_code == 201
    assert response.json()["title"] == "Milk"


def test_list_expenses_empty():
    response = client.get("/expenses")
    assert response.status_code == 200
    assert response.json() == []


def test_list_expenses_after_adding():
    payload = {"title": "Milk", "amount": 55.0, "category": "Groceries"}
    client.post("/expenses", json=payload)
    response = client.get("/expenses")
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Milk"


def test_rejects_negative_amount():
    payload = {"title": "Milk", "amount": -5, "category": "Groceries"}
    response = client.post("/expenses", json=payload)
    assert response.status_code == 422


def test_rejects_missing_field():
    response = client.post("/expenses", json={"title": "Milk"})
    assert response.status_code == 422
