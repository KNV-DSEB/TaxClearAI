from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from src.modules.chatbot.law_source import LawTextRecord
from src.modules.legal_library.repository import LegalLibraryRepository
from src.modules.legal_library.schemas import LegalLookupRequest
from src.modules.legal_library.service import LegalLibraryService


@pytest.fixture
def service() -> LegalLibraryService:
    return LegalLibraryService(LegalLibraryRepository())


@pytest.mark.parametrize(
    ("procedure", "expected_document"),
    [
        ("company_dissolution", "59/2020/QH14"),
        ("tax_id_termination", "90/2026/TT-BTC"),
        ("hkd_termination", "168/2025/NĐ-CP"),
        ("hkd_new_registration", "168/2025/NĐ-CP"),
    ],
)
def test_search_returns_current_references_for_each_procedure(
    service: LegalLibraryService, procedure: str, expected_document: str
) -> None:
    result = service.search(LegalLookupRequest(procedure=procedure))

    assert result.results
    assert any(item.document_number == expected_document for item in result.results)
    assert all(item.issuing_authority for item in result.results)
    assert all(item.effectiveness_status == "khong_ro" for item in result.results)
    assert all(
        item.applicable_provisions or item.document_number in {"117/2025/NĐ-CP", "310/2025/NĐ-CP"}
        for item in result.results
    )


def test_tax_lookup_uses_current_law_and_does_not_return_superseded_tax_forms(
    service: LegalLibraryService,
) -> None:
    result = service.search(LegalLookupRequest(procedure="tax_id_termination"))
    numbers = {item.document_number for item in result.results}

    assert "108/2025/QH15" in numbers
    assert "252/2026/NĐ-CP" in numbers
    assert "90/2026/TT-BTC" in numbers
    assert "38/2019/QH14" not in numbers
    assert "86/2024/TT-BTC" not in numbers


def test_hkd_termination_references_tax_precondition_and_commune_registry_sequence(
    service: LegalLibraryService,
) -> None:
    result = service.search(LegalLookupRequest(procedure="hkd_termination"))
    hkd_rule = next(item for item in result.results if item.document_number == "168/2025/NĐ-CP")
    tax_rule = next(item for item in result.results if item.document_number == "90/2026/TT-BTC")

    assert any(
        item.article == "Điều 104" and item.point == "Điểm a"
        for item in hkd_rule.applicable_provisions
    )
    assert any("cấp xã" in item.regulated_action for item in hkd_rule.applicable_provisions)
    assert any(
        item.article == "Điều 27" and "Khoản 4" in item.clause
        for item in tax_rule.applicable_provisions
    )


def test_query_can_search_without_procedure_filter(service: LegalLibraryService) -> None:
    result = service.search(LegalLookupRequest(query="hộ kinh doanh"))

    assert result.results
    assert all(
        "hộ kinh doanh" in item.summary.casefold()
        or "hộ kinh doanh" in item.document_name.casefold()
        or "hộ kinh doanh"
        in " ".join(
            provision.regulated_action for provision in item.applicable_provisions
        ).casefold()
        or item.document_number in {"168/2025/NĐ-CP", "90/2026/TT-BTC"}
        for item in result.results
    )


def test_requires_procedure_or_query() -> None:
    with pytest.raises(ValidationError):
        LegalLookupRequest()


def test_new_references_expose_shared_law_sync_fields(
    service: LegalLibraryService,
) -> None:
    result = service.search(LegalLookupRequest(query="kinh tế tư nhân"))
    resolution = next(item for item in result.results if item.document_number == "198/2025/QH15")

    assert resolution.has_verbatim_text is False
    assert resolution.source_url.startswith("https://congbao.chinhphu.vn/")
    assert resolution.last_synced is None
    assert resolution.effectiveness_status == "khong_ro"
    assert resolution.change_note


def test_reference_sync_fields_come_from_shared_law_store(monkeypatch: pytest.MonkeyPatch) -> None:
    record = LawTextRecord.model_validate(
        {
            "document_number": "198/2025/QH15",
            "article": "Điều 10",
            "clause": "Khoản 7",
            "noi_dung": "Nội dung nguyên văn từ văn bản.",
            "source_url": "https://congbao.chinhphu.vn/van-ban/test.htm",
            "source_domain": "congbao.chinhphu.vn",
            "fetched_at": "2026-10-30T12:00:00+00:00",
            "content_sha256": "a" * 64,
            "effectiveness_status": "con_hieu_luc",
        }
    )
    monkeypatch.setattr(
        "src.modules.legal_library.service.read_law_text_records",
        lambda: ({record.key: record}, []),
    )
    result = LegalLibraryService(LegalLibraryRepository()).search(
        LegalLookupRequest(query="kinh tế tư nhân")
    )
    resolution = next(item for item in result.results if item.document_number == "198/2025/QH15")

    assert resolution.has_verbatim_text is True
    assert resolution.source_url == record.source_url
    assert resolution.last_synced == datetime(2026, 10, 30, 12, tzinfo=UTC)
    assert resolution.effectiveness_status == "con_hieu_luc"


@pytest.mark.parametrize(
    ("number", "issued", "effective"),
    [
        ("117/2025/NĐ-CP", "2025-06-09", "2025-07-01"),
        ("310/2025/NĐ-CP", "2025-12-02", "2026-01-16"),
        ("198/2025/QH15", "2025-05-17", "2025-05-17"),
    ],
)
def test_new_references_publish_official_dates_and_links(
    service: LegalLibraryService, number: str, issued: str, effective: str
) -> None:
    references = LegalLibraryRepository().get_references(None, None)
    reference = next(item for item in references if item.document_number == number)

    assert reference.issued_date.isoformat() == issued
    assert reference.effective_date.isoformat() == effective
    assert reference.source_url.startswith("https://congbao.chinhphu.vn/")
