import json
from pathlib import Path

from fastapi.testclient import TestClient


def test_expert_list_filters_by_segment_region_and_type(client) -> None:
    response = client.get("/experts", params={"segment": "A1", "region": "Miền Bắc"})

    assert response.status_code == 200
    experts = response.json()
    assert experts
    assert all(expert["verified"] is True for expert in experts)
    assert all("A1" in expert["segments"] for expert in experts)
    assert all(
        any("miền bắc" in region.casefold() for region in expert["regions"]) for expert in experts
    )
    assert all(expert["du_lieu_minh_hoa"] is True for expert in experts)

    typed = client.get("/experts", params={"expert_type": "dai_ly_thue"})
    assert typed.status_code == 200
    assert typed.json()
    assert all(expert["expert_type"] == "dai_ly_thue" for expert in typed.json())


def test_expert_detail_includes_scope_prices_and_no_unverified_expert(client) -> None:
    response = client.get("/experts/demo-lawyer-01")

    assert response.status_code == 200
    expert = response.json()
    assert expert["du_lieu_minh_hoa"] is True
    assert expert["services"][0]["price_min"] == 5000000
    assert expert["services"][0]["price_max"] is None
    assert expert["services"][0]["price_unit"] == "VND/hồ sơ"
    assert expert["services"][0]["exclusions"] == ["Tiền thuế, tiền phạt và lệ phí nộp nhà nước"]
    assert expert["platform_fee_note"] == "MVP: nền tảng chưa xử lý thanh toán hoặc thu phí."
    assert expert["platform_fee_model"] == {"type": "none", "value": None}

    hidden = client.get("/experts/demo-accountant-unverified-05")
    assert hidden.status_code == 404


def test_every_segment_has_illustrative_verified_expert(client: TestClient) -> None:
    for segment in ("A1", "A2", "A3", "B1", "B2"):
        response = client.get("/experts", params={"segment": segment})

        assert response.status_code == 200
        experts = response.json()
        assert experts
        assert all(expert["verified"] is True for expert in experts)
        assert all(expert["du_lieu_minh_hoa"] is True for expert in experts)


def test_expert_listing_never_includes_ids_outside_data_file(client) -> None:
    data_path = (
        Path(__file__)
        .parents[2]
        .joinpath("src", "modules", "expert_directory", "data", "experts.json")
    )
    source_ids = {item["id"] for item in json.loads(data_path.read_text(encoding="utf-8"))}

    response = client.get("/experts")

    assert response.status_code == 200
    assert {expert["id"] for expert in response.json()} <= source_ids


def test_expert_request_returns_redacted_case_brief_without_sending(client) -> None:
    response = client.post(
        "/experts/demo-lawyer-01/requests",
        json={
            "diagnosis": {
                "segment": "A3",
                "entity_type": "HKD",
                "procedure": "Chấm dứt hoạt động",
                "target_action": "terminate",
                "risk_flags": [],
                "blockers": [
                    "Chủ hộ: Nguyễn Văn An, MST: 0123456789, số gọi 0912345678, "
                    "email an@example.test"
                ],
                "notes": [],
            },
            "user_questions": ["Liên hệ an@example.test"],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    brief_text = json.dumps(payload["case_brief"], ensure_ascii=False)
    assert "Nguyễn Văn An" not in brief_text
    assert "0123456789" not in brief_text
    assert "0912345678" not in brief_text
    assert "an@example.test" not in brief_text
    assert "[email đã ẩn]" in brief_text
    assert payload["request_status"] == "prepared_not_sent"
    assert payload["du_lieu_minh_hoa"] is True


def test_expert_request_uses_shared_redaction_without_masking_terms_or_locations(
    client: TestClient,
) -> None:
    response = client.post(
        "/experts/demo-lawyer-01/requests",
        json={
            "diagnosis": {
                "segment": "A3",
                "entity_type": "Hộ Kinh Doanh",
                "procedure": "Chấm dứt hoạt động",
                "target_action": "terminate",
                "risk_flags": [],
                "notes": ["Hộ kinh doanh tạp hóa tại Quận Ba Đình"],
                "blockers": ["Nguyễn Văn An SĐT 0912345678 chưa kê khai 3 kỳ"],
            },
            "user_questions": ["Tôi là Trần Thị Bé, MST 0312345678, có bị phạt không?"],
        },
    )

    assert response.status_code == 200
    brief = response.json()["case_brief"]
    serialized = json.dumps(brief, ensure_ascii=False)
    diagnosis = brief["diagnosis"]
    assert diagnosis["entity_type"] == "Hộ Kinh Doanh"
    assert "Quận Ba Đình" in diagnosis["notes"][0]
    assert "Nguyễn Văn An" not in serialized
    assert "Trần Thị Bé" not in serialized
    assert "0912345678" not in serialized
    assert "0312345678" not in serialized
    assert "[tên riêng đã ẩn]" in serialized
    assert "[số điện thoại đã ẩn]" in serialized
    assert "[MST đã ẩn]" in serialized


def test_expert_request_rejects_segment_outside_expert_profile(client) -> None:
    response = client.post(
        "/experts/demo-lawyer-01/requests",
        json={
            "diagnosis": {
                "segment": "B2",
                "entity_type": "DN",
                "procedure": "Rà soát hồ sơ",
                "target_action": "terminate",
            }
        },
    )

    assert response.status_code == 422
