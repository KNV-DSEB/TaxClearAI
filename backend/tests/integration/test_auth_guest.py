from sqlalchemy import delete, select

from src.models.auth import User
from tests.integration.test_assessment_flow import ORIGIN, PAYLOAD, live_client, login
from tests.integration.test_assessment_list import run_in_test_db

__all__ = ["live_client"]


def remove_users(*usernames: str) -> None:
    async def action(session):
        await session.execute(delete(User).where(User.username.in_(usernames)))
        await session.commit()

    run_in_test_db(action)


def user_exists(username: str) -> bool:
    async def action(session):
        return await session.scalar(select(User.id).where(User.username == username)) is not None

    return run_in_test_db(action)


def test_each_guest_session_is_a_separate_user_with_private_cases(live_client):
    client, _, _ = live_client
    first = client.post("/api/v1/auth/guest-sessions", headers=ORIGIN)
    assert first.status_code == 201, first.text
    assert "HttpOnly" in first.headers["set-cookie"]
    assert "SameSite=strict" in first.headers["set-cookie"]
    guest_a = first.json()["data"]["user"]["username"]
    case = client.post("/api/v1/assessments", headers=ORIGIN, json=PAYLOAD).json()["data"]

    second = client.post("/api/v1/auth/guest-sessions", headers=ORIGIN)
    guest_b = second.json()["data"]["user"]["username"]
    try:
        assert guest_a != guest_b
        assert guest_a.startswith("khach-")
        assert client.get(f"/api/v1/assessments/{case['id']}").status_code == 404
        assert client.get("/api/v1/assessments").json()["data"]["total"] == 0
    finally:
        remove_users(guest_a, guest_b)


def test_demo_name_needs_the_real_password_and_is_never_auto_created(live_client):
    client, username, _ = live_client
    wrong = client.post(
        "/api/v1/auth/sessions",
        headers=ORIGIN,
        json={"username": username, "password": "mat-khau-bat-ky-123"},
    )
    assert wrong.status_code == 401
    if not user_exists("demo"):
        response = client.post(
            "/api/v1/auth/sessions",
            headers=ORIGIN,
            json={"username": "demo", "password": "mat-khau-bat-ky-123"},
        )
        assert response.status_code == 401
        assert not user_exists("demo")


def test_writes_from_other_vercel_apps_or_without_origin_are_rejected(live_client):
    client, username, password = live_client
    login(client, username, password)
    for headers in ({"Origin": "https://ke-gian.vercel.app"}, {}):
        response = client.post("/api/v1/assessments", headers=headers, json=PAYLOAD)
        assert response.status_code == 403
    preflight = client.options(
        "/api/v1/assessments",
        headers={
            "Origin": "https://ke-gian.vercel.app",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert "access-control-allow-origin" not in preflight.headers
