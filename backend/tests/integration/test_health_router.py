from fastapi.testclient import TestClient


def test_get_health_returns_200_and_status_ok(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
