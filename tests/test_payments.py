def test_payment_usd(client):
    response = client.post("/payments", json={
        "order_id": "ORD-TEST01",
        "amount": 100.0,
        "currency": "USD",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["amount_usd"] == 100.0
    assert data["payment_id"].startswith("PAY-")


def test_payment_currency_conversion(client):
    response = client.post("/payments", json={
        "order_id": "ORD-TEST02",
        "amount": 100.0,
        "currency": "EUR",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["amount_usd"] == 108.0


def test_payment_returns_order_id(client):
    response = client.post("/payments", json={
        "order_id": "ORD-CHECKID",
        "amount": 75.0,
        "currency": "USD",
    })
    assert response.status_code == 200
    assert response.json()["order_id"] == "ORD-CHECKID"
