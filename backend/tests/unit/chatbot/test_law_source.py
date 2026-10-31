import hashlib
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from src.core.config import get_settings
from src.modules.chatbot import sync_law_text
from src.modules.chatbot.schemas import EffectivenessStatus, LawEntry, Segment
from src.modules.chatbot.source_policy import is_usable_source
from src.modules.chatbot.sync_law_text import _TextExtractor, extract_provision


@pytest.fixture(autouse=True)
def source_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LAW_SOURCE_ALLOWLIST", "congbao.chinhphu.vn")
    monkeypatch.setenv("LAW_MAX_AGE_DAYS", "30")
    get_settings.cache_clear()


def source(**updates: object) -> LawEntry:
    content = "Điều 1. Nội dung nguyên văn được trích từ nguồn chính thức."
    row: dict[str, object] = {
        "document_number": "1/2026/QH15",
        "article": "Điều 1",
        "clause": "Khoản 1",
        "noi_dung": content,
        "source_url": "https://congbao.chinhphu.vn/van-ban/test.htm",
        "source_domain": "congbao.chinhphu.vn",
        "fetched_at": datetime.now(UTC),
        "content_sha256": hashlib.sha256(content.encode()).hexdigest(),
        "effectiveness_status": EffectivenessStatus.CURRENT,
        "ap_dung_cho": [Segment.A1],
    }
    row.update(updates)
    return LawEntry.model_validate(row)


@pytest.mark.parametrize(
    "changes",
    [
        {"source_domain": "example.com"},
        {"effectiveness_status": EffectivenessStatus.EXPIRED},
        {"fetched_at": datetime.now(UTC) - timedelta(days=31)},
        {"content_sha256": "0" * 64},
        {"noi_dung": "[PLACEHOLDER]"},
        {"noi_dung": "  "},
    ],
)
def test_source_fails_closed_for_invalid_provenance(changes: dict[str, object]) -> None:
    assert not is_usable_source(source(**changes))


def test_valid_recent_official_source_is_usable() -> None:
    assert is_usable_source(source())


def test_extracts_requested_clause_and_rejects_ambiguous_structure() -> None:
    fixture = Path(__file__).parents[2] / "fixtures" / "law" / "simple.html"
    parser = _TextExtractor()
    parser.feed(fixture.read_text(encoding="utf-8"))
    text = parser.text()
    assert extract_provision(text, "Điều 1", "Khoản 1", None) == "1. Nguyên văn khoản một."
    ambiguous = text + " Điều 1. Lặp điều. 1. Nội dung."
    assert extract_provision(ambiguous, "Điều 1", "Khoản 1", None) is None


def test_sync_extracts_fixture_and_reports_expired_status(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    manifest = [
        {
            "document_number": "1/2026/QH15",
            "source_url": "https://congbao.chinhphu.vn/van-ban/test.htm",
            "provisions": [
                {"article": "Điều 1", "clause": "Khoản 1"},
                {"article": "Điều 1", "clause": "Khoản 3"},
            ],
        }
    ]
    (data_dir / "law_sources.json").write_text(
        json.dumps(manifest, ensure_ascii=False), encoding="utf-8"
    )
    (data_dir / "law_text.json").write_text("[]", encoding="utf-8")
    monkeypatch.setattr(sync_law_text, "DATA_DIR", data_dir)
    monkeypatch.setattr(sync_law_text, "read_law_text_records", lambda: ({}, []))
    fixture = Path(__file__).parents[2] / "fixtures" / "law" / "simple.html"
    page = fixture.read_text(encoding="utf-8") + "<p>Hết hiệu lực.</p>"
    monkeypatch.setattr(sync_law_text, "_fetch", lambda _url: page)

    report = sync_law_text.synchronize()

    assert report["successful"] == 1
    assert len(report["skipped"]) == 1
    assert report["expired_documents"] == ["1/2026/QH15"]
    stored = json.loads((data_dir / "law_text.json").read_text(encoding="utf-8"))
    extracted = next(row for row in stored if row["clause"] == "Khoản 1")
    assert extracted["noi_dung"] == "1. Nguyên văn khoản một."
    assert extracted["effectiveness_status"] == "het_hieu_luc"
    assert (
        extracted["content_sha256"]
        == hashlib.sha256(extracted["noi_dung"].encode("utf-8")).hexdigest()
    )


def test_sync_skips_ambiguous_changed_page_and_keeps_old_record(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    url = "https://congbao.chinhphu.vn/van-ban/test.htm"
    old_fetched_at = "2026-10-30T12:00:00+00:00"
    manifest = [
        {
            "document_number": "1/2026/QH15",
            "source_url": url,
            "provisions": [{"article": "Điều 1", "clause": "Khoản 1"}],
        }
    ]
    old_record = {
        "document_number": "1/2026/QH15",
        "article": "Điều 1",
        "clause": "Khoản 1",
        "noi_dung": "Nội dung cũ nguyên văn.",
        "source_url": url,
        "source_domain": "congbao.chinhphu.vn",
        "fetched_at": old_fetched_at,
        "content_sha256": hashlib.sha256("Nội dung cũ nguyên văn.".encode()).hexdigest(),
        "effectiveness_status": "con_hieu_luc",
    }
    (data_dir / "law_sources.json").write_text(
        json.dumps(manifest, ensure_ascii=False), encoding="utf-8"
    )
    (data_dir / "law_text.json").write_text(
        json.dumps([old_record], ensure_ascii=False), encoding="utf-8"
    )
    monkeypatch.setattr(sync_law_text, "DATA_DIR", data_dir)
    monkeypatch.setattr(sync_law_text, "read_law_text_records", lambda: ({}, []))
    fixture = Path(__file__).parents[2] / "fixtures" / "law" / "simple.html"
    page = fixture.read_text(encoding="utf-8") + "<p>Điều 1. Bản lặp.</p>"
    monkeypatch.setattr(sync_law_text, "_fetch", lambda _url: page)

    report = sync_law_text.synchronize()

    assert report["successful"] == 0
    assert len(report["skipped"]) == 1
    stored = json.loads((data_dir / "law_text.json").read_text(encoding="utf-8"))
    assert stored[0]["fetched_at"] == old_fetched_at
    assert stored[0]["noi_dung"] == old_record["noi_dung"]


def test_extracts_text_from_official_pdf_attachment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import pypdf

    monkeypatch.setenv("LAW_SOURCE_ALLOWLIST", "congbao.chinhphu.vn,datafiles.chinhphu.vn")
    get_settings.cache_clear()
    fixture = Path(__file__).parents[2] / "fixtures" / "law" / "pdf_source.html"
    page = fixture.read_text(encoding="utf-8-sig")
    fetched: list[str] = []
    monkeypatch.setattr(
        sync_law_text,
        "_fetch_bytes",
        lambda url: fetched.append(url) or b"fixture PDF bytes",
    )

    class FakePage:
        @staticmethod
        def extract_text() -> str:
            return "Điều 27. Nội dung từ tài liệu PDF."

    class FakePdfReader:
        def __init__(self, _payload: bytes) -> None:
            self.pages = [FakePage()]

    monkeypatch.setattr(pypdf, "PdfReader", FakePdfReader)

    extracted = sync_law_text._extract_official_document_text(
        page, "https://congbao.chinhphu.vn/van-ban/test.htm"
    )

    assert fetched == ["https://datafiles.chinhphu.vn/cpp/files/vbpq/2026/7/90-btc.signed.pdf"]
    assert extracted == "Điều 27. Nội dung từ tài liệu PDF."
