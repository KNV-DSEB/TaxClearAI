import asyncio
import secrets
from collections.abc import AsyncGenerator
from uuid import uuid4

import httpx
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from src.core.config import get_settings
from src.core.database import get_db
from src.core.security import hash_password
from src.main import create_app
from src.models.auth import User
from src.modules.auth.repository import AuthRepository

ORIGIN = {"Origin": "http://localhost:3000"}
PAYLOAD = {
    "questionnaireVersion": "b2-draft-1",
    "answers": {
        "businessType": "company",
        "goal": "dissolution",
        "establishedYear": 2010,
        "revenueStatus": "yes",
        "revenueStartedYear": 2011,
        "filingStatus": "unknown",
        "recordsStatus": "partial",
        "taxNoticeStatus": "unknown",
        "laborInsuranceStatus": "unknown",
        "assetsInventoryStatus": "yes",
        "receivablesPayablesStatus": "unknown",
    },
}


@pytest.fixture
def live_client():
    url = get_settings().test_database_url
    if not url or not url.endswith("/tax_clear_ai_test"):
        pytest.fail("Cần TEST_DATABASE_URL trỏ đúng DB riêng tax_clear_ai_test.")
    engine = create_async_engine(url, poolclass=NullPool)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    username, password = f"test_{uuid4().hex[:16]}", secrets.token_urlsafe(20)

    async def seed():
        async with sessions() as session:
            await AuthRepository(session).bootstrap(username, hash_password(password))

    asyncio.run(seed())

    async def db() -> AsyncGenerator[AsyncSession]:
        async with sessions() as session:
            yield session

    application = create_app()
    application.dependency_overrides[get_db] = db

    async def cleanup():
        async with sessions.begin() as session:
            await session.execute(delete(User).where(User.username == username))

    try:
        with TestClient(application) as client:
            yield client, username, password
    finally:
        asyncio.run(cleanup())
        asyncio.run(engine.dispose())


def login(client, username, password):
    response = client.post(
        "/api/v1/auth/sessions", headers=ORIGIN, json={"username": username, "password": password}
    )
    assert response.status_code == 201, response.text
    assert "HttpOnly" in response.headers["set-cookie"]


def test_real_postgres_flow_saves_and_reopens_checklist(live_client):
    client, username, password = live_client
    login(client, username, password)
    questions = client.get("/api/v1/questionnaires/b2")
    assert len(questions.json()["data"]["questions"]) == 11
    created = client.post("/api/v1/assessments", headers=ORIGIN, json=PAYLOAD)
    assert created.status_code == 201, created.text
    case = created.json()["data"]
    location = created.headers["location"]
    assert case["summary"]["scope"] == "b2"
    assert len(case["checklist"]) == 19
    item_id = case["checklist"][0]["id"]
    changed = client.patch(
        f"{location}/checklist-items/{item_id}", headers=ORIGIN, json={"status": "available"}
    )
    assert changed.status_code == 200, changed.text
    reopened = client.get(location).json()["data"]
    assert (
        next(item for item in reopened["checklist"] if item["id"] == item_id)["status"]
        == "available"
    )
    assert client.delete(location, headers=ORIGIN).status_code == 204
    assert client.get(location).status_code == 404


def test_foreign_owner_cannot_read_change_or_delete_case(live_client):
    client, username, password = live_client
    login(client, username, password)
    created = client.post("/api/v1/assessments", headers=ORIGIN, json=PAYLOAD)
    location = created.headers["location"]
    item_id = created.json()["data"]["checklist"][0]["id"]
    from src.modules.auth.dependencies import get_current_user
    from src.modules.auth.domain import UserRecord

    client.app.dependency_overrides[get_current_user] = lambda: UserRecord(
        uuid4(), "other", "", True
    )
    assert client.get(location).status_code == 404
    assert (
        client.patch(
            f"{location}/checklist-items/{item_id}", headers=ORIGIN, json={"status": "missing"}
        ).status_code
        == 404
    )
    assert client.delete(location, headers=ORIGIN).status_code == 404


def test_invalid_input_and_stale_version_return_safe_problem_details(live_client):
    client, username, password = live_client
    login(client, username, password)
    invalid = client.post(
        "/api/v1/assessments", headers=ORIGIN, json=PAYLOAD | {"ownerId": str(uuid4())}
    )
    assert invalid.status_code == 422
    assert invalid.headers["content-type"].startswith("application/problem+json")
    assert "ownerId" not in invalid.text
    assert (
        client.post(
            "/api/v1/assessments", headers=ORIGIN, json=PAYLOAD | {"questionnaireVersion": "old"}
        ).status_code
        == 409
    )


def test_refresh_rotates_and_logout_revokes_refresh(live_client):
    client, username, password = live_client
    login(client, username, password)
    old = client.cookies.get("refresh_token")
    refreshed = client.post("/api/v1/auth/refreshes", headers=ORIGIN)
    assert refreshed.status_code == 200, refreshed.text
    assert old != client.cookies.get("refresh_token")
    assert client.delete("/api/v1/auth/sessions/current", headers=ORIGIN).status_code == 204
    assert client.get("/api/v1/questionnaires/b2").status_code == 401
    assert client.post("/api/v1/auth/refreshes", headers=ORIGIN).status_code == 401


def test_csrf_body_limit_and_public_login_rate_limit(live_client):
    client, _, _ = live_client
    assert client.post("/api/v1/auth/sessions", json={}).status_code == 403
    assert (
        client.post("/api/v1/auth/sessions", headers=ORIGIN, content="a" * 9000).status_code == 413
    )
    for _ in range(3):
        client.post("/api/v1/auth/sessions", headers=ORIGIN, json={})
    limited = client.post("/api/v1/auth/sessions", headers=ORIGIN, json={})
    assert limited.status_code == 429
    assert limited.headers["retry-after"] == "60"


def test_chat_api_requires_consent_and_never_accepts_case_or_history(live_client):
    from src.modules.chat.provider import GeminiProvider

    client, username, password = live_client
    login(client, username, password)
    transport = httpx.MockTransport(
        lambda _: httpx.Response(
            200,
            json={
                "candidates": [
                    {
                        "content": {
                            "parts": [
                                {
                                    "text": (
                                        '{"reply":"Chọn trạng thái cho giấy tờ.",'
                                        '"sourceIds":["product-guide"]}'
                                    )
                                }
                            ]
                        }
                    }
                ],
            },
        )
    )
    client.app.state.chat_service.provider = GeminiProvider(
        "unit-test-only", "gemini-3.5-flash-lite", transport
    )
    payload = {"message": "Tôi dùng checklist thế nào?", "disclosureAccepted": True}
    response = client.post("/api/v1/chat/messages", headers=ORIGIN, json=payload)
    assert response.status_code == 200, response.text
    assert response.json()["data"]["providerUsed"] is True
    assert response.json()["data"]["citations"][0]["kind"] == "product"
    for changes in (
        {"disclosureAccepted": False},
        {"assessmentId": str(uuid4())},
        {"history": []},
        {"message": " "},
        {"message": "a" * 1501},
    ):
        assert (
            client.post("/api/v1/chat/messages", headers=ORIGIN, json=payload | changes).status_code
            == 422
        )
