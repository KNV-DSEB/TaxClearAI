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
MONEY = re.compile(r"\d[\d.,\s]*(?:đồng|vnd|vnđ|triệu|tỷ|%)", re.IGNORECASE)
PRIVATE_TERMS = ("cccd", "can cuoc", "ma so thue", "so tai khoan", "mat khau", "api key")
RISK_TERMS = ("bao nhieu tien", "tien thue", "so thue", "truy thu", "phat", "ne thue", "tron thue")
LEGAL_TERMS = ("quy dinh", "phap ly", "dieu luat", "thu tuc", "giai the", "ke khai", "co quan thue")
PRODUCT_TERMS = ("checklist", "trang thai", "luu", "mo lai", "khao sat", "dang nhap", "cach dung")


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
    ) -> None:
        self.provider = provider
        self.source_loader = source_loader
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
            reply="Chưa có đủ nguồn pháp lý được cố vấn duyệt cho câu hỏi này. "
            "Bạn nên trao đổi với chuyên viên. Tôi có thể giải thích cách dùng checklist trên web.",
            disposition="insufficient_sources",
            provider_used=provider_used,
        )

    async def answer(self, owner: UUID, message: str) -> ChatReply:
        self.check_rate(owner)
        text = normalize(message)
        if SENSITIVE.search(message) or any(term in text for term in PRIVATE_TERMS):
            return ChatReply(
                reply="Câu hỏi có dấu hiệu chứa thông tin riêng tư. Vui lòng bỏ thông tin "
                "nhận diện và chỉ hỏi bằng tình huống giả định.",
                disposition="blocked_input",
            )
        if any(term in text for term in RISK_TERMS):
            return ChatReply(
                reply="Tôi không tính thuế, tiền phạt hoặc kết luận cho hồ sơ cụ thể. "
                "Bạn cần chuyên viên thuế xem xét thông tin đã được xác minh.",
                disposition="expert_review",
            )
        legal = any(term in text for term in LEGAL_TERMS)
        product = any(term in text for term in PRODUCT_TERMS)
        sources = [
            source
            for source in self.source_loader()
            if source.kind == ("legal" if legal else "product")
        ]
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
            )
            for source in sources
            if source.id in generated.source_ids
        ]
        return ChatReply(
            reply=generated.reply, disposition="answered", citations=citations, provider_used=True
        )
