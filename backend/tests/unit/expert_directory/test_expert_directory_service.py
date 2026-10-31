import json
from pathlib import Path

import pytest
from fastapi import HTTPException

from src.modules.case_brief.schemas import CaseBriefRequest
from src.modules.expert_directory.repository import ExpertDirectoryRepository
from src.modules.expert_directory.schemas import ExpertType
from src.modules.expert_directory.service import ExpertDirectoryService


def _service() -> ExpertDirectoryService:
    return ExpertDirectoryService(ExpertDirectoryRepository())


def test_filters_experts_by_segment_region_and_type() -> None:
    service = _service()

    by_segment = service.list_verified(segment="A1")
    by_region = service.list_verified(region="miền bắc")
    by_type = service.list_verified(expert_type=ExpertType.DAI_LY_THUE)

    assert by_segment
    assert all("A1" in expert.segments for expert in by_segment)
    assert by_region
    assert all(any("miền bắc" in region.casefold() for region in e.regions) for e in by_region)
    assert by_type
    assert all(expert.expert_type == ExpertType.DAI_LY_THUE for expert in by_type)


def test_unverified_experts_are_not_listed_or_returned_by_id() -> None:
    service = _service()

    experts = service.list_verified()
    with pytest.raises(HTTPException) as error:
        service.get_verified("demo-accountant-unverified-05")

    assert error.value.status_code == 404
    assert all(expert.verified for expert in experts)
    assert "demo-accountant-unverified-05" not in {expert.id for expert in experts}


def test_only_experts_from_the_json_data_file_are_returned() -> None:
    data_path = (
        Path(__file__)
        .parents[3]
        .joinpath("src", "modules", "expert_directory", "data", "experts.json")
    )
    source_ids = {item["id"] for item in json.loads(data_path.read_text(encoding="utf-8"))}

    returned_ids = {expert.id for expert in _service().list_verified()}

    assert returned_ids
    assert returned_ids <= source_ids


def test_demo_profiles_cover_every_segment_and_have_valid_service_prices() -> None:
    repository = ExpertDirectoryRepository()
    profiles = repository.list_experts()
    verified_profiles = _service().list_verified()
    supported_segments = {segment for expert in verified_profiles for segment in expert.segments}

    assert {"A1", "A2", "A3", "B1", "B2"} <= supported_segments
    assert all(expert.illustrative for expert in profiles)
    for expert in profiles:
        for service in expert.services:
            assert service.price_min is None or service.price_min >= 0
            assert service.price_max is None or service.price_max >= 0
            if service.price_min is not None and service.price_max is not None:
                assert service.price_min <= service.price_max
            assert service.scope.strip()
            assert service.exclusions
            assert all(exclusion.strip() for exclusion in service.exclusions)


def test_request_redacts_identifiers_before_return_and_logging(monkeypatch) -> None:
    logged: dict[str, object] = {}

    def capture_log(event: str, **fields: object) -> None:
        logged["event"] = event
        logged.update(fields)

    monkeypatch.setattr("src.modules.expert_directory.service.logger.info", capture_log)
    request = CaseBriefRequest.model_validate(
        {
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
            "user_questions": ["Liên hệ An qua an@example.test"],
        }
    )
    repository = ExpertDirectoryRepository()
    before = len(repository.list_experts())

    response = ExpertDirectoryService(repository).prepare_request("demo-lawyer-01", request)
    payload = response.model_dump(mode="json", by_alias=True)
    log_text = json.dumps(logged, ensure_ascii=False)
    brief_text = json.dumps(payload["case_brief"], ensure_ascii=False)

    assert "Nguyễn Văn An" not in brief_text + log_text
    assert "0123456789" not in brief_text + log_text
    assert "0912345678" not in brief_text + log_text
    assert "an@example.test" not in brief_text + log_text
    assert isinstance(logged["case_brief"], str)
    assert len(logged["case_brief"]) <= 500
    assert "[email đã ẩn]" in brief_text
    assert response.request_status == "prepared_not_sent"
    assert response.illustrative is True
    assert len(repository.list_experts()) == before
