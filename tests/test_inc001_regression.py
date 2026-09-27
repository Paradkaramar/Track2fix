"""Regression test for INC-001.

POST /payments with a non-USD currency under production configuration must
return HTTP 200 with a clear error — not an uncontrolled HTTP 500 TypeError.



Before the fix : HTTP 500 (unguarded float * NoneType in app/payment.py)
After the fix  : HTTP 422 or similar explicit error (defensive guard raises
                 a handled exception when EXCHANGE_RATE is absent from config)
"""
import os
import pytest


@pytest.fixture()
def prod_client(monkeypatch):
    """Client that runs against production configuration (APP_ENV=prod)."""
    monkeypatch.setenv("APP_ENV", "prod")
    # Import after env is set so get_config() picks up prod.yaml
    from app.main import app
    from fastapi.testclient import TestClient
    return TestClient(app, raise_server_exceptions=False)


def test_non_usd_payment_prod_config_no_unhandled_500(prod_client):
    """Non-USD payment under prod config must not produce an uncontrolled HTTP 500.

    INC-001: EXCHANGE_RATE is absent from config/prod.yaml.  Before the fix
    the application crashes with TypeError and returns 500.  After the fix it
    returns an explicit error response (not 500).
    """
    response = prod_client.post("/payments", json={
        "order_id": "ORD-INC001",
        "amount": 250.0,
        "currency": "EUR",
    })
    assert response.status_code != 500, (
        "INC-001 regression: POST /payments returned uncontrolled HTTP 500 "
        "for a non-USD currency under production configuration. "
        "Expected an explicit, handled error response."
    )
