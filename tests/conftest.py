import os
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def use_dev_config(monkeypatch):
    """Ensure all tests run against development configuration."""
    monkeypatch.setenv("APP_ENV", "dev")


@pytest.fixture()
def client(use_dev_config):
    # Import app after env is set so get_config() picks up dev
    from app.main import app
    return TestClient(app, raise_server_exceptions=False)
