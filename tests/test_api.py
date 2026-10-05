import pytest
from fastapi.testclient import TestClient
from app.main import app, expenses

client = TestClient(app)

SAMPLE = {"title": "Milk", "amount": 55.0, "category": "Groceries"}


@pytest.fixture(autouse=True)
def clear_expenses():
    expenses.clear()


def add_sample():
    return client.post("/expenses", json=SAMPLE).json()


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_add_expense():
    response = client.post("/expenses", json=SAMPLE)
    assert response.status_code == 201
    assert response.json()["title"] == "Milk"
    assert response.json()["id"] == 1


def test_list_expenses_empty():
    response = client.get("/expenses")
    assert response.status_code == 200
    assert response.json() == []


def test_list_expenses_after_adding():
    add_sample()
    response = client.get("/expenses")
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Milk"


def test_rejects_negative_amount():
    payload = {**SAMPLE, "amount": -5}
    response = client.post("/expenses", json=payload)
    assert response.status_code == 422


def test_rejects_missing_field():
    response = client.post("/expenses", json={"title": "Milk"})
    assert response.status_code == 422


def test_get_expense_by_id():
    created = add_sample()
    response = client.get(f"/expenses/{created['id']}")
    assert response.status_code == 200
    assert response.json()["title"] == "Milk"


def test_get_expense_not_found():
    response = client.get("/expenses/999")
    assert response.status_code == 404


def test_update_expense():
    created = add_sample()
    updated = {"title": "Bread", "amount": 40.0, "category": "Groceries"}
    response = client.put(f"/expenses/{created['id']}", json=updated)
    assert response.status_code == 200
    assert response.json()["title"] == "Bread"
    assert response.json()["amount"] == 40.0


def test_update_expense_not_found():
    response = client.put("/expenses/999", json=SAMPLE)
    assert response.status_code == 404


def test_delete_expense():
    created = add_sample()
    response = client.delete(f"/expenses/{created['id']}")
    assert response.status_code == 200
    assert client.get("/expenses").json() == []


def test_delete_expense_not_found():
    response = client.delete("/expenses/999")
    assert response.status_code == 404
