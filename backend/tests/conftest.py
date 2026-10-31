import pytest
from fastapi.testclient import TestClient

from src.core.rate_limit import reset_rate_limit_state
from src.main import app


@pytest.fixture(autouse=True)
def isolate_rate_limit_state() -> None:
    reset_rate_limit_state()


@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client
