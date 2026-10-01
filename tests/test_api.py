from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_add_expense():
    payload = {"title": "Milk", "amount": 55.0, "category": "Groceries"}
    response = client.post("/expenses", json=payload)
    assert response.status_code == 201
    assert response.json()["title"] == "Milk"
