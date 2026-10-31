import pytest


def test_generate_case_brief(client) -> None:
    response = client.post(
        "/case-brief/generate",
        json={
            "diagnosis": {
                "segment": "A3",
                "entity_type": "HKD",
                "procedure": "Chấm dứt hoạt động hộ kinh doanh",
                "target_action": "terminate",
                "risk_flags": ["bank_account_mismatch"],
                "blockers": ["Doanh thu kê khai lệch sao kê"],
                "notes": [],
            },
            "user_questions": [],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["case_classification"].startswith("A3")
    assert payload["estimated_cost"]["currency"] == "VND"
    assert payload["estimated_cost"]["minimum"] == 5_000_000
    assert payload["estimated_cost"]["maximum"] is None
    assert payload["estimated_cost"]["service_fee"] == {
        "minimum": 5_000_000,
        "maximum": None,
        "note": payload["estimated_cost"]["service_fee"]["note"],
    }
    assert payload["estimated_cost"]["sources"] == ["Ban cố vấn dự án (báo giá tham khảo)"]
    assert len(payload["scope_of_work"]["expert_to_do"]) >= 4
    assert "không gửi bản gốc" in payload["privacy_note"]


@pytest.mark.parametrize(
    ("segment", "service_minimum", "service_maximum", "requires_survey"),
    [
        ("A2", 5_000_000, None, False),
        ("B1", 11_500_000, 19_500_000, False),
        ("B2", None, None, True),
    ],
)
def test_estimated_cost_returns_advisor_reference_and_separate_state_payments(
    client,
    segment: str,
    service_minimum: int | None,
    service_maximum: int | None,
    requires_survey: bool,
) -> None:
    response = client.post(
        "/case-brief/generate",
        json={
            "diagnosis": {
                "segment": segment,
                "entity_type": "Doanh nghiệp" if segment.startswith("B") else "HKD",
                "procedure": "Chấm dứt hoạt động",
                "target_action": "terminate",
            }
        },
    )

    assert response.status_code == 200
    cost = response.json()["estimated_cost"]
    assert cost["service_fee"]["minimum"] == service_minimum
    assert cost["service_fee"]["maximum"] == service_maximum
    assert cost["minimum"] == service_minimum
    assert cost["maximum"] == service_maximum
    assert cost["quote_requires_survey"] is requires_survey
    assert cost["sources"] == ["Ban cố vấn dự án (báo giá tham khảo)"]
    assert "không ước tính" in cost["state_payments_note"] or segment == "B1"
    if segment == "B1":
        assert "30.000.000–80.000.000" in cost["state_payments_note"]
        assert "không phải số tiền phải nộp của hồ sơ người dùng" in cost["state_payments_note"]
    if segment == "B2":
        assert "hàng tỷ đồng" in cost["state_payments_note"]
        assert "khảo sát hồ sơ thực tế" in cost["service_fee"]["note"]


def test_generate_case_brief_rejects_uploaded_document_field(client) -> None:
    response = client.post(
        "/case-brief/generate",
        json={
            "diagnosis": {
                "segment": "A1",
                "entity_type": "HKD",
                "procedure": "Chấm dứt",
                "target_action": "terminate",
            },
            "uploaded_document": "sensitive contents",
        },
    )

    assert response.status_code == 422
