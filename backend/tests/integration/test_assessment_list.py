import asyncio
from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import update
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from src.core.config import get_settings
from src.models.assessment import Assessment
from src.modules.assessments.repository import AssessmentRepository
from tests.integration.test_assessment_flow import ORIGIN, PAYLOAD, live_client, login

__all__ = ["live_client"]

LONG_AGO = datetime(2000, 1, 1, tzinfo=UTC)


def run_in_test_db(action):
    async def runner():
        engine = create_async_engine(get_settings().test_database_url, poolclass=NullPool)
        try:
            async with async_sessionmaker(engine, expire_on_commit=False)() as session:
                return await action(session)
        finally:
            await engine.dispose()

    return asyncio.run(runner())


def expire(assessment_id: str) -> None:
    async def action(session):
        await session.execute(
            update(Assessment)
            .where(Assessment.id == UUID(assessment_id))
            .values(expires_at=LONG_AGO)
        )
        await session.commit()

    run_in_test_db(action)


def test_list_shows_own_cases_newest_first_with_checklist_counts(live_client):
    client, username, password = live_client
    login(client, username, password)
    first = client.post("/api/v1/assessments", headers=ORIGIN, json=PAYLOAD).json()["data"]
    second = client.post("/api/v1/assessments", headers=ORIGIN, json=PAYLOAD).json()["data"]
    item = second["checklist"][0]["id"]
    client.patch(
        f"/api/v1/assessments/{second['id']}/checklist-items/{item}",
        headers=ORIGIN,
        json={"status": "available"},
    )

    page = client.get("/api/v1/assessments", params={"pageSize": 1}).json()["data"]
    assert page["total"] == 2
    assert page["pageSize"] == 1
    assert [entry["id"] for entry in page["items"]] == [second["id"]]
    assert page["items"][0]["counts"] == {
        "available": 1,
        "missing": 0,
        "needsVerification": 18,
    }
    assert not page["items"][0]["expired"]
    assert page["items"][0]["status"] == "in_progress"
    next_page = client.get("/api/v1/assessments", params={"page": 2, "pageSize": 1})
    assert [entry["id"] for entry in next_page.json()["data"]["items"]] == [first["id"]]


def test_list_rejects_oversized_page_and_hides_other_owners(live_client):
    client, username, password = live_client
    login(client, username, password)
    client.post("/api/v1/assessments", headers=ORIGIN, json=PAYLOAD)
    assert client.get("/api/v1/assessments", params={"pageSize": 101}).status_code == 422
    from src.modules.auth.dependencies import get_current_user
    from src.modules.auth.domain import UserRecord

    client.app.dependency_overrides[get_current_user] = lambda: UserRecord(
        uuid4(), "other", "", True
    )
    assert client.get("/api/v1/assessments").json()["data"] == {
        "items": [],
        "page": 1,
        "pageSize": 20,
        "total": 0,
        "statusCounts": {"all": 0, "inProgress": 0, "ready": 0},
    }


def test_expired_case_is_listed_and_owner_can_still_delete_it(live_client):
    client, username, password = live_client
    login(client, username, password)
    created = client.post("/api/v1/assessments", headers=ORIGIN, json=PAYLOAD).json()["data"]
    expire(created["id"])

    listed = client.get("/api/v1/assessments").json()["data"]["items"]
    assert listed[0]["expired"]
    assert listed[0]["status"] == "expired"
    assert client.get(f"/api/v1/assessments/{created['id']}").status_code == 404
    assert client.delete(f"/api/v1/assessments/{created['id']}", headers=ORIGIN).status_code == 204
    assert client.get("/api/v1/assessments").json()["data"]["total"] == 0


def test_purge_dry_run_counts_and_apply_removes_only_expired_cases(live_client):
    client, username, password = live_client
    login(client, username, password)
    old = client.post("/api/v1/assessments", headers=ORIGIN, json=PAYLOAD).json()["data"]
    client.post("/api/v1/assessments", headers=ORIGIN, json=PAYLOAD)
    expire(old["id"])
    # Mốc năm 2000 chỉ chạm hồ sơ vừa đặt hết hạn, không đụng dữ liệu khác trong DB test
    cutoff = datetime(2000, 1, 2, tzinfo=UTC)

    async def dry_run(session):
        return await AssessmentRepository(session).purge_expired(cutoff, apply=False)

    async def apply(session):
        return await AssessmentRepository(session).purge_expired(cutoff, apply=True)

    assert run_in_test_db(dry_run) == 1
    assert client.get("/api/v1/assessments").json()["data"]["total"] == 2
    assert run_in_test_db(apply) == 1
    remaining = client.get("/api/v1/assessments").json()["data"]["items"]
    assert [entry["id"] for entry in remaining] != [old["id"]]
    assert len(remaining) == 1


def test_status_filter_and_counts_follow_checklist_completion(live_client):
    client, username, password = live_client
    login(client, username, password)
    ready = client.post("/api/v1/assessments", headers=ORIGIN, json=PAYLOAD).json()["data"]
    client.post("/api/v1/assessments", headers=ORIGIN, json=PAYLOAD)
    for item in ready["checklist"]:
        client.patch(
            f"/api/v1/assessments/{ready['id']}/checklist-items/{item['id']}",
            headers=ORIGIN,
            json={"status": "available"},
        )

    page = client.get("/api/v1/assessments", params={"status": "ready"}).json()["data"]
    assert [entry["id"] for entry in page["items"]] == [ready["id"]]
    assert page["items"][0]["status"] == "ready"
    assert page["total"] == 1
    assert page["statusCounts"] == {"all": 2, "inProgress": 1, "ready": 1}
    in_progress = client.get("/api/v1/assessments", params={"status": "in_progress"})
    assert [entry["status"] for entry in in_progress.json()["data"]["items"]] == ["in_progress"]
    assert client.get("/api/v1/assessments", params={"status": "done"}).status_code == 422


def test_current_session_returns_signed_in_user_only(live_client):
    client, username, password = live_client
    assert client.get("/api/v1/auth/sessions/current").status_code == 401
    login(client, username, password)
    assert client.get("/api/v1/auth/sessions/current").json()["data"]["username"] == username
