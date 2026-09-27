"""
Deterministic reproducer for INC-001.

Runs the payment service under production configuration using FastAPI TestClient
and issues the affected payment request. Prints the HTTP status and response body.
No live server is required.
"""
import os
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore", category=DeprecationWarning)

# Ensure the project root is on the path when the script is run from any directory
sys.path.insert(0, str(Path(__file__).parent.parent))

os.environ["APP_ENV"] = "prod"

from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402

PAYLOAD = {
    "order_id": "ORD-INC001",
    "amount": 250.0,
    "currency": "EUR",
}

REQUEST_ID = "req-1842"


def main():
    client = TestClient(app, raise_server_exceptions=False)

    print("=" * 50)
    print("INC-001 Reproducer")
    print("=" * 50)
    print(f"Endpoint  : POST /payments")
    print(f"Payload   : {PAYLOAD}")
    print(f"Request-ID: {REQUEST_ID}")
    print("-" * 50)

    response = client.post(
        "/payments",
        json=PAYLOAD,
        headers={"X-Request-ID": REQUEST_ID},
    )

    print(f"HTTP Status : {response.status_code}")
    print(f"Response    : {response.text}")
    print("=" * 50)

    if response.status_code == 500:
        print("Incident reproduced: production failure confirmed (HTTP 500).")
        sys.exit(0)
    else:
        print(f"Unexpected status {response.status_code} — incident not reproduced.")
        sys.exit(1)


if __name__ == "__main__":
    main()
