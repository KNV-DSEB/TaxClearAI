"""Hồ sơ lưu theo bộ câu hỏi cũ (groups-draft-2) vẫn phải mở được sau khi đổi mô hình."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy import select

from src.models.assessment import Assessment
from src.models.auth import User
from tests.integration.test_assessment_flow import live_client, login
from tests.integration.test_assessment_list import run_in_test_db

__all__ = ["live_client"]

LEGACY_ANSWERS = {
    "businessType": "household",
    "registrationStatus": "yes",
    "householdGoal": "stop",
    "goal": "dissolution",
    "establishedYear": None,
    "revenueStatus": "unknown",
    "revenueStartedYear": None,
    "filingStatus": "incomplete",
    "discrepancyStatus": "unknown",
    "recordsStatus": "partial",
    "taxNoticeStatus": "unknown",
    "laborInsuranceStatus": "unknown",
    "assetsInventoryStatus": "unknown",
    "receivablesPayablesStatus": "unknown",
}
LEGACY_SUMMARY = {
    "scope": "a2",
    "knownFacts": [],
    "unknownFacts": [],
    "reviewReasons": [],
    "notice": "Bản tổng hợp cũ.",
}


def insert_legacy_case(username: str) -> str:
    async def action(session):
        owner = await session.scalar(select(User.id).where(User.username == username))
        case_id = uuid4()
        now = datetime.now(UTC)
        session.add(
            Assessment(
                id=case_id,
                owner_id=owner,
                answers=LEGACY_ANSWERS,
                content_version="groups-draft-2",
                summary_snapshot=LEGACY_SUMMARY,
                expires_at=now + timedelta(days=1),
            )
        )
        await session.commit()
        return str(case_id)

    return run_in_test_db(action)


def test_case_saved_with_the_old_questionnaire_still_opens_and_lists(live_client):
    client, username, password = live_client
    login(client, username, password)
    case_id = insert_legacy_case(username)

    opened = client.get(f"/api/v1/assessments/{case_id}")
    assert opened.status_code == 200, opened.text
    data = opened.json()["data"]
    assert data["questionnaireVersion"] == "groups-draft-2"
    assert data["answers"]["registrationStatus"] == "yes"
    assert data["summary"]["scope"] == "a2"

    listed = client.get("/api/v1/assessments").json()["data"]
    assert [item["scope"] for item in listed["items"]] == ["a2"]
