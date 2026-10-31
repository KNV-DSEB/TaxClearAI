import re

import pytest
from fastapi.testclient import TestClient


def test_create_hkd_termination_roadmap_returns_required_json(client: TestClient) -> None:
    response = client.post(
        "/procedures/roadmap",
        json={"segment": "A2", "target_action": "terminate"},
    )

    assert response.status_code == 200
    roadmap = response.json()
    assert set(roadmap) == {"segment", "roadmap_title", "steps", "needs_expert"}
    assert roadmap["segment"] == "A2"
    assert roadmap["steps"][0]["step_order"] == 1
    assert set(roadmap["steps"][0]) == {
        "step_order",
        "phase",
        "action",
        "agency",
        "law_reference",
        "expected_duration",
        "can_self_do",
    }
    assert any(step["phase"] == "TAX_SUBMISSION" for step in roadmap["steps"])
    assert any(step["phase"] == "REGISTRATION_RESULT" for step in roadmap["steps"])


def test_create_company_dissolution_roadmap_uses_current_registry_deadlines(
    client: TestClient,
) -> None:
    response = client.post(
        "/procedures/roadmap",
        json={"segment": "B2", "target_action": "terminate"},
    )

    assert response.status_code == 200
    steps = response.json()["steps"]
    assert any("05 ngày làm việc" in step["expected_duration"] for step in steps)
    assert any("02 ngày làm việc" in step["expected_duration"] for step in steps)
    assert any("296/2026/NĐ-CP" in step["law_reference"] for step in steps)


def test_create_roadmap_rejects_unknown_segment(client: TestClient) -> None:
    response = client.post(
        "/procedures/roadmap",
        json={"segment": "C1", "target_action": "terminate"},
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    ("segment", "target_action"),
    [
        (segment, target_action)
        for segment in ("A1", "A2", "A3", "B1", "B2")
        for target_action in ("terminate", "convert_to_new_entity", "suspend")
    ],
)
def test_roadmap_endpoint_accepts_each_segment_and_target(
    client: TestClient, segment: str, target_action: str
) -> None:
    response = client.post(
        "/procedures/roadmap",
        json={"segment": segment, "target_action": target_action},
    )

    assert response.status_code == 200
    steps = response.json()["steps"]
    assert [step["step_order"] for step in steps] == list(range(1, len(steps) + 1))


@pytest.mark.parametrize("segment", ["A1", "A2", "A3", "B1", "B2"])
def test_suspension_checklist_is_nonempty(client: TestClient, segment: str) -> None:
    response = client.post(
        "/documents/checklist",
        json={"segment": segment, "procedure": "suspend"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total_items"] > 0
    assert len(body["checklist"]) > 0


@pytest.mark.parametrize("segment", ["A1", "A2", "A3", "B1", "B2"])
def test_suspension_roadmap_has_contiguous_steps(client: TestClient, segment: str) -> None:
    response = client.post(
        "/procedures/roadmap",
        json={"segment": segment, "target_action": "suspend"},
    )

    assert response.status_code == 200
    body = response.json()
    assert "Quy trình tạm ngừng kinh doanh" in body["roadmap_title"]
    assert body["steps"]
    assert [step["step_order"] for step in body["steps"]] == list(range(1, len(body["steps"]) + 1))


def test_conversion_planner_rejects_suspension_as_unsupported(client: TestClient) -> None:
    response = client.post(
        "/conversion-plans/parallel",
        json={"current_model": "HKD", "desired_model": "COMPANY_LLC", "target_action": "suspend"},
    )

    assert response.status_code == 422
    assert "không thuộc phạm vi" in response.json()["detail"]


@pytest.mark.parametrize("segment", ["B1", "B2"])
def test_compare_procedures_returns_qualitative_comparison(
    client: TestClient, segment: str
) -> None:
    response = client.post(
        "/procedures/compare",
        json={"segment": segment, "has_dispute": True},
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["rows"]) == 5
    assert "không khuyến nghị chọn hướng nào" in body["recommendation_boundary"]
    assert all(
        row["legal_basis"] == "Chưa xác định căn cứ trong nguồn đã đồng bộ" for row in body["rows"]
    )
    assert all(
        re.search(r"\d[\d.,]*\s*(đồng|vnđ|vnd|triệu|nghìn|tỷ|%)", str(row), re.I) is None
        for row in body["rows"]
    )


def test_compare_procedures_rejects_household_segment(client: TestClient) -> None:
    response = client.post("/procedures/compare", json={"segment": "A2"})

    assert response.status_code == 422
