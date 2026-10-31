import hashlib
from datetime import UTC, datetime
from urllib.parse import urlparse

from src.core.config import get_settings
from src.modules.chatbot.schemas import EffectivenessStatus, LawEntry


def is_usable_source(source: LawEntry, *, now: datetime | None = None) -> bool:
    """Return whether a source satisfies every provenance and freshness requirement."""
    text = source.noi_dung.strip()
    if not text or _is_placeholder(text):
        return False
    settings = get_settings()
    domain = source.source_domain.strip().lower().rstrip(".")
    if domain not in settings.allowed_law_domains:
        return False
    parsed_url = urlparse(source.source_url)
    if parsed_url.scheme != "https" or (parsed_url.hostname or "").lower() != domain:
        return False
    # Unknown status can be surfaced with an expert warning by the response pipeline.
    # Expired and not-yet-effective documents must never support an answer.
    if source.effectiveness_status in {
        EffectivenessStatus.EXPIRED,
        EffectivenessStatus.NOT_YET_EFFECTIVE,
    }:
        return False
    if source.fetched_at is None:
        return False
    current = now or datetime.now(UTC)
    fetched = source.fetched_at
    if fetched.tzinfo is None:
        fetched = fetched.replace(tzinfo=UTC)
    age_days = (current - fetched).total_seconds() / 86400
    if age_days < 0 or age_days > settings.law_max_age_days:
        return False
    digest = hashlib.sha256(source.noi_dung.encode("utf-8")).hexdigest()
    return source.content_sha256 == digest


def _is_placeholder(text: str) -> bool:
    normalized = text.casefold()
    return any(
        marker in normalized for marker in ("placeholder", "chưa có nội dung nguyên văn", "[chưa")
    )
