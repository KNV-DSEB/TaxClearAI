"""Chọn đoạn văn bản luật dùng cho chat: kiểm nguồn gốc rồi xếp hạng theo câu hỏi.

Dữ liệu và chính sách nguồn lấy từ PR #15 (trandang2507), thu gọn cho phạm vi B2.
"""

import hashlib
import re
import unicodedata
from collections.abc import Callable
from datetime import UTC, datetime
from urllib.parse import urlparse

from src.modules.assessments.domain import SourceRecord
from src.modules.chat.repository import LegalProvision, LegalSourceRepository

ALLOWED_DOMAINS = frozenset(
    {
        "congbao.chinhphu.vn",
        "vanban.chinhphu.vn",
        "datafiles.chinhphu.vn",
        "vbpl.vn",
        "hue.gov.vn",
    }
)
# Chưa có công cụ đồng bộ lại trong repo, nên nguồn quá hạn sẽ tự ngừng được dùng
MAX_AGE_DAYS = 30
TOP_K = 4
MIN_SCORE = 2
# Cụm xuất hiện gần như mọi đoạn luật, nếu tính điểm sẽ kéo câu hỏi lạc đề về nguồn luật
GENERIC_PHRASES = frozenset(
    {"thutuc", "doanhnghiep", "quydinh", "phapluat", "phaply", "theoquy", "dieuluat"}
)
STOP_WORDS = frozenset(
    [
        "va",
        "la",
        "gi",
        "nao",
        "the",
        "nhu",
        "khong",
        "co",
        "duoc",
        "can",
        "hay",
        "nhung",
        "cac",
        "cua",
        "cho",
        "voi",
        "theo",
        "mot",
        "toi",
        "ban",
        "minh",
        "nay",
        "do",
        "khi",
        "tu",
        "ve",
        "trong",
        "den",
        "se",
        "da",
        "thi",
        "bi",
        "ra",
        "vao",
        "lam",
        "sao",
    ]
)


def syllables(text: str) -> list[str]:
    decomposed = unicodedata.normalize("NFD", text.casefold().replace("đ", "d"))
    plain = "".join(char for char in decomposed if unicodedata.category(char) != "Mn")
    return re.findall(r"[a-z0-9]+", plain)


def query_phrases(question: str) -> set[str]:
    words = syllables(question)
    return {
        first + second
        for first, second in zip(words, words[1:], strict=False)
        if not (first in STOP_WORDS and second in STOP_WORDS)
    } - GENERIC_PHRASES


def is_usable(provision: LegalProvision, now: datetime) -> bool:
    url = urlparse(provision.source_url)
    age_days = (now - provision.fetched_at).total_seconds() / 86400
    digest = hashlib.sha256(provision.text.encode("utf-8")).hexdigest()
    return (
        bool(provision.text.strip())
        and url.scheme == "https"
        and (url.hostname or "") in ALLOWED_DOMAINS
        and 0 <= age_days <= MAX_AGE_DAYS
        and digest == provision.content_sha256
    )


def to_source(provision: LegalProvision) -> SourceRecord:
    location = ", ".join(
        part for part in (provision.article, provision.clause, provision.point) if part
    )
    text = provision.text
    if provision.amended_by:
        text += f"\n(Ghi chú: {provision.amended_by}.)"
    return SourceRecord(
        id=provision.id,
        title=f"{provision.document_title} {provision.document_number} — {location}",
        url=provision.source_url,
        text=text,
        reviewed_at=None,
        kind="legal",
        fetched_at=provision.fetched_at,
        review_status="unreviewed",
    )


class LegalSourceSelector:
    def __init__(
        self,
        repository: LegalSourceRepository | None = None,
        clock: Callable[[], datetime] = lambda: datetime.now(UTC),
    ) -> None:
        self.repository = repository or LegalSourceRepository()
        self.clock = clock
        self.provisions = self.repository.list_provisions()
        # PDF gốc đôi khi tách âm tiết ("gi ải"), nên so khớp trên chuỗi đã bỏ khoảng trắng
        self.index = [
            "".join(syllables(f"{item.document_title} {item.text}")) for item in self.provisions
        ]

    def select(self, question: str) -> list[SourceRecord]:
        phrases = query_phrases(question)
        now = self.clock()
        ranked = []
        for position, (provision, squashed) in enumerate(
            zip(self.provisions, self.index, strict=True)
        ):
            score = sum(phrase in squashed for phrase in phrases)
            if score >= MIN_SCORE and is_usable(provision, now):
                ranked.append((-score, position, provision))
        ranked.sort(key=lambda item: item[:2])
        return [to_source(provision) for _, _, provision in ranked[:TOP_K]]
