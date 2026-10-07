import pytest
from fastapi.testclient import TestClient
from app.main import app, expenses

client = TestClient(app)

SAMPLE = {"title": "Milk", "amount": 55.0,
          "category": "Groceries", "date": "2026-10-01"}


@pytest.fixture(autouse=True)
def clear_expenses():
    expenses.clear()


def add(title="Milk", amount=55.0, category="Groceries", date="2026-10-01"):
    payload = {"title": title, "amount": amount,
               "category": category, "date": date}
    return client.post("/expenses", json=payload).json()


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_add_expense():
    response = client.post("/expenses", json=SAMPLE)
    assert response.status_code == 201
    assert response.json()["title"] == "Milk"
    assert response.json()["id"] == 1
    assert response.json()["date"] == "2026-10-01"


def test_list_expenses_empty():
    response = client.get("/expenses")
    assert response.status_code == 200
    assert response.json() == []


def test_list_expenses_after_adding():
    add()
    response = client.get("/expenses")
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Milk"


def test_rejects_negative_amount():
    response = client.post("/expenses", json={**SAMPLE, "amount": -5})
    assert response.status_code == 422


def test_rejects_missing_field():
    response = client.post("/expenses", json={"title": "Milk"})
    assert response.status_code == 422


def test_rejects_invalid_date():
    response = client.post("/expenses", json={**SAMPLE, "date": "not-a-date"})
    assert response.status_code == 422


def test_get_expense_by_id():
    created = add()
    response = client.get(f"/expenses/{created['id']}")
    assert response.status_code == 200
    assert response.json()["title"] == "Milk"


def test_get_expense_not_found():
    assert client.get("/expenses/999").status_code == 404


def test_update_expense():
    created = add()
    updated = {"title": "Bread", "amount": 40.0,
               "category": "Groceries", "date": "2026-10-02"}
    response = client.put(f"/expenses/{created['id']}", json=updated)
    assert response.status_code == 200
    assert response.json()["title"] == "Bread"
    assert response.json()["amount"] == 40.0


def test_update_expense_not_found():
    assert client.put("/expenses/999", json=SAMPLE).status_code == 404


def test_delete_expense():
    created = add()
    response = client.delete(f"/expenses/{created['id']}")
    assert response.status_code == 200
    assert client.get("/expenses").json() == []


def test_delete_expense_not_found():
    assert client.delete("/expenses/999").status_code == 404


def test_summary_empty_month():
    response = client.get("/summary", params={"year": 2026, "month": 10})
    assert response.status_code == 200
    assert response.json()["total"] == 0
    assert response.json()["by_category"] == {}


def test_summary_totals_by_category():
    add("Milk", 55.0, "Groceries", "2026-10-01")
    add("Bread", 40.5, "Groceries", "2026-10-15")
    add("Bus", 20.25, "Transport", "2026-10-03")
    response = client.get("/summary", params={"year": 2026, "month": 10})
    assert response.json()["total"] == 115.75
    assert response.json()["by_category"] == {
        "Groceries": 95.5, "Transport": 20.25}


def test_summary_excludes_other_months_and_years():
    add("Oct item", 100.0, "Groceries", "2026-10-10")
    add("Sept item", 50.0, "Groceries", "2026-09-30")
    add("Last year", 70.0, "Groceries", "2025-10-10")
    response = client.get("/summary", params={"year": 2026, "month": 10})
    assert response.json()["total"] == 100.0


def test_summary_rejects_invalid_month():
    response = client.get("/summary", params={"year": 2026, "month": 13})
    assert response.status_code == 422


def test_summary_requires_parameters():
    assert client.get("/summary").status_code == 422
