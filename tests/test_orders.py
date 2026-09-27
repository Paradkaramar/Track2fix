def test_create_order(client):
    response = client.post("/orders", json={
        "customer_id": "cust-001",
        "amount": 50.0,
        "currency": "USD",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "pending"
    assert data["customer_id"] == "cust-001"
    assert data["amount"] == 50.0
    assert data["currency"] == "USD"
    assert data["order_id"].startswith("ORD-")


def test_create_order_with_description(client):
    response = client.post("/orders", json={
        "customer_id": "cust-002",
        "amount": 120.0,
        "currency": "USD",
        "description": "Test order",
    })
    assert response.status_code == 200
    assert response.json()["status"] == "pending"


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
