import re
import time
import unicodedata
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Protocol
from uuid import UUID

from src.core.errors import ApplicationError
from src.modules.assessments.domain import SourceRecord
from src.modules.assessments.service import get_approved_chat_sources
from src.modules.chat.schemas import ChatReply, Citation, GeneratedAnswer

SENSITIVE = re.compile(r"[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}|(?:\d[\s.-]*){7,}")
YEARS = re.compile(r"\b(?:19|20)\d{2}\b")
MONEY = re.compile(r"\d[\d.,\s]*(?:đồng|vnd|vnđ|triệu|tỷ|%)", re.IGNORECASE)


def phrases(*terms: str) -> re.Pattern[str]:
    # So khớp nguyên cụm từ: "phat" không được khớp "phát sinh" hay "phát hành"
    return re.compile(r"\b(?:" + "|".join(terms) + r")\b")


# Chỉ chặn khi người dùng đưa giá trị, không chặn câu hỏi về chính khái niệm đó
PRIVATE_VALUE = phrases(
    r"(?:cccd|can cuoc|cmnd|ma so thue|mst|so tai khoan)(?:\s+cua\s+\w+)?\s*(?:la|:)\s*[\w-]*\d\w*",
    "mat khau",
    "api key",
)
RISK_TERMS = phrases(
    "bao nhieu tien",
    "so tien thue",
    "tien thue",
    "so thue phai nop",
    "truy thu",
    "tien phat",
    "bi phat",
    "muc phat",
    "khoan phat",
    "xu phat",
    "nop phat",
    "phat bao nhieu",
    "phat cham nop",
    "ne thue",
    "tron thue",
    "lach thue",
)
LEGAL_TERMS = phrases(
    "quy dinh",
    "phap ly",
    "phap luat",
    "dieu luat",
    "luat",
    "nghi dinh",
    "thong tu",
    "thu tuc",
    "giai the",
    "ke khai",
    "co quan thue",
    "ma so thue",
    "mon bai",
    "nghia vu",
    "thanh ly",
)
PRODUCT_TERMS = phrases(
    "checklist", "trang thai", "luu", "mo lai", "khao sat", "dang nhap", "cach dung"
)


def normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text.casefold().replace("đ", "d"))
    return "".join(char for char in decomposed if unicodedata.category(char) != "Mn")


class AnswerProvider(Protocol):
    async def generate(self, message: str, sources: list[SourceRecord]) -> GeneratedAnswer: ...


class ChatService:
    def __init__(
        self,
        provider: AnswerProvider,
        source_loader: Callable[[], list[SourceRecord]] = get_approved_chat_sources,
        legal_selector: Callable[[str], list[SourceRecord]] = lambda _: [],
    ) -> None:
        self.provider = provider
        self.source_loader = source_loader
        self.legal_selector = legal_selector
        self.buckets: dict[UUID, tuple[int, int]] = {}
        self.day = datetime.now(UTC).date()
        self.daily_calls = 0

    def check_rate(self, owner: UUID) -> None:
        minute = int(time.monotonic() // 60)
        self.buckets = {key: value for key, value in self.buckets.items() if value[0] == minute}
        _, count = self.buckets.get(owner, (minute, 0))
        if count >= 3 or len(self.buckets) > 10000:
            raise ApplicationError(429, "Bạn đã hỏi nhiều câu liên tiếp. Vui lòng chờ một phút.")
        self.buckets[owner] = (minute, count + 1)

    def reserve_quota(self) -> None:
        today = datetime.now(UTC).date()
        if today != self.day:
            self.day, self.daily_calls = today, 0
        if self.daily_calls >= 20:
            raise ApplicationError(
                429, "Bản thử đã hết lượt trợ lý hôm nay. Vui lòng quay lại sau."
            )
        self.daily_calls += 1

    def insufficient(self, provider_used: bool = False) -> ChatReply:
        return ChatReply(
            reply="Tôi chưa tìm thấy nguồn phù hợp cho câu hỏi này. "
            "Bạn có thể hỏi cách dùng checklist hoặc trao đổi với chuyên viên.",
            disposition="insufficient_sources",
            provider_used=provider_used,
        )

    async def answer(self, owner: UUID, message: str) -> ChatReply:
        self.check_rate(owner)
        text = normalize(message)
        if SENSITIVE.search(YEARS.sub(" ", message)) or PRIVATE_VALUE.search(text):
            return ChatReply(
                reply="Câu hỏi có dấu hiệu chứa thông tin riêng tư. Vui lòng bỏ thông tin "
                "nhận diện và chỉ hỏi bằng tình huống giả định.",
                disposition="blocked_input",
            )
        if RISK_TERMS.search(text):
            return ChatReply(
                reply="Tôi không tính thuế, tiền phạt hoặc kết luận cho hồ sơ cụ thể. "
                "Bạn cần chuyên viên thuế xem xét thông tin đã được xác minh.",
                disposition="expert_review",
            )
        legal = bool(LEGAL_TERMS.search(text))
        product = bool(PRODUCT_TERMS.search(text))
        if legal:
            sources = self.legal_selector(message)
        else:
            sources = [source for source in self.source_loader() if source.kind == "product"]
        if not sources or (not legal and not product):
            return self.insufficient()
        self.reserve_quota()
        generated = await self.provider.generate(message, sources)
        allowed = {source.id: source for source in sources}
        if MONEY.search(generated.reply) or any(key not in allowed for key in generated.source_ids):
            return self.insufficient(provider_used=True)
        citations = [
            Citation(
                source_id=source.id,
                title=source.title,
                url=source.url,
                reviewed_at=source.reviewed_at,
                kind=source.kind,
                fetched_at=source.fetched_at,
                review_status=source.review_status,
            )
            for source in sources
            if source.id in generated.source_ids
        ]
        return ChatReply(
            reply=generated.reply, disposition="answered", citations=citations, provider_used=True
        )
