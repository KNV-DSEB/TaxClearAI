import hashlib
import json
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from src.modules.chat.legal_sources import LegalSourceSelector, is_usable
from src.modules.chat.repository import DATA_FILE, LegalProvision, LegalSourceRepository
from src.modules.chat.schemas import GeneratedAnswer
from src.modules.chat.service import ChatService

FETCHED = datetime(2026, 10, 31, 10, 0, tzinfo=UTC)
TEXT = "1. Hồ sơ giải thể doanh nghiệp bao gồm giấy tờ sau đây: a) Thông báo về giải thể."


def provision(**changes) -> LegalProvision:
    values = {
        "id": "L1",
        "document_number": "59/2020/QH14",
        "document_title": "Luật Doanh nghiệp",
        "article": "Điều 210",
        "clause": "Khoản 1",
        "point": "",
        "text": TEXT,
        "source_url": "https://congbao.chinhphu.vn/van-ban/luat-59.htm",
        "fetched_at": FETCHED,
        "content_sha256": hashlib.sha256(TEXT.encode()).hexdigest(),
        "amended_by": None,
    }
    return LegalProvision(**(values | changes))


def write_sources(tmp_path, *items: LegalProvision):
    path = tmp_path / "sources.json"
    path.write_text(
        json.dumps(
            {
                "origin": "test",
                "reviewStatus": "unreviewed",
                "provisions": [item.model_dump(mode="json", by_alias=True) for item in items],
            }
        ),
        encoding="utf-8",
    )
    return LegalSourceRepository(path)


@pytest.mark.parametrize(
    ("changes", "now"),
    [
        ({"content_sha256": "0" * 64}, FETCHED),
        ({"source_url": "http://congbao.chinhphu.vn/van-ban/luat-59.htm"}, FETCHED),
        ({"source_url": "https://example.com/luat-59.htm"}, FETCHED),
        ({}, FETCHED + timedelta(days=31)),
        ({}, FETCHED - timedelta(days=1)),
    ],
)
def test_source_rejected_when_hash_domain_scheme_or_freshness_fails(changes, now):
    assert not is_usable(provision(**changes), now)


def test_bundled_b2_sources_keep_original_text_hashes():
    provisions = LegalSourceRepository(DATA_FILE).list_provisions()
    assert len(provisions) == 25
    assert all(is_usable(item, item.fetched_at) for item in provisions)


def test_selector_matches_split_pdf_syllables_and_skips_off_topic_questions(tmp_path):
    split = "Doanh nghi ệp ch ỉ được gi ải th ể khi b ảo đảm thanh toán hết các khoản nợ."
    repository = write_sources(
        tmp_path,
        provision(),
        provision(
            id="L2",
            article="Điều 207",
            clause="Khoản 2",
            text=split,
            content_sha256=hashlib.sha256(split.encode()).hexdigest(),
        ),
    )
    selector = LegalSourceSelector(repository, clock=lambda: FETCHED)
    chosen = selector.select("Khi nào doanh nghiệp được giải thể và thanh toán khoản nợ?")
    assert [source.id for source in chosen] == ["L2"]
    assert chosen[0].kind == "legal"
    assert chosen[0].review_status == "unreviewed"
    assert chosen[0].title == "Luật Doanh nghiệp 59/2020/QH14 — Điều 207, Khoản 2"
    assert selector.select("Thủ tục nhập khẩu ô tô thế nào?") == []


def test_selector_stops_using_stale_sources(tmp_path):
    selector = LegalSourceSelector(
        write_sources(tmp_path, provision()), clock=lambda: FETCHED + timedelta(days=31)
    )
    assert selector.select("Hồ sơ giải thể gồm giấy tờ gì?") == []


def test_unreadable_source_file_degrades_to_no_sources(tmp_path):
    path = tmp_path / "broken.json"
    path.write_text("{not json", encoding="utf-8")
    assert LegalSourceRepository(path).list_provisions() == []


class FakeProvider:
    def __init__(self):
        self.sources = []

    async def generate(self, message, sources):
        self.sources = sources
        return GeneratedAnswer(
            reply="Theo Luật Doanh nghiệp, Điều 210 khoản 1, hồ sơ gồm thông báo giải thể.",
            source_ids=[sources[0].id],
        )


async def test_legal_question_is_answered_from_official_text_marked_unreviewed(tmp_path):
    selector = LegalSourceSelector(write_sources(tmp_path, provision()), clock=lambda: FETCHED)
    provider = FakeProvider()
    result = await ChatService(provider, legal_selector=selector.select).answer(
        uuid4(), "Hồ sơ giải thể doanh nghiệp gồm những giấy tờ gì?"
    )
    assert result.disposition == "answered"
    assert [source.kind for source in provider.sources] == ["legal"]
    citation = result.citations[0]
    assert citation.kind == "legal"
    assert citation.review_status == "unreviewed"
    assert citation.reviewed_at is None
    assert citation.fetched_at == FETCHED
    assert citation.url.startswith("https://congbao.chinhphu.vn/")
