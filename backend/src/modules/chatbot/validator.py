import json
import re
import unicodedata

from pydantic import ValidationError

from src.modules.chatbot.guardrail import normalize_text
from src.modules.chatbot.schemas import LawEntry, LLMAnswer
from src.modules.chatbot.source_policy import is_usable_source

_JSON_FENCE = re.compile(r"^\s*```(?:json)?\s*(.*?)\s*```\s*$", re.DOTALL | re.IGNORECASE)
_MONEY = re.compile(r"(?i)(\d[\d.,]*\s*(đồng|vnđ|vnd|triệu|nghìn|ngàn|tỷ|%|phần\s+trăm))")
_MONEY_WORDS = re.compile(
    r"(?i)\b(một|hai|ba|bốn|năm|sáu|bảy|tám|chín|mười)"
    r"(?:\s+(?:mươi|mốt|lăm|trăm|linh|lẻ)){0,3}\s+(triệu|nghìn|ngàn|tỷ|đồng)\b"
)
_APPROXIMATE_MONEY = re.compile(r"(?i)\b(vài|mấy|nửa|hơn|khoảng)\s+(triệu|nghìn|ngàn|tỷ)\b")
_COMMANDING = re.compile(r"\b(ban phai|ban nen lam cach|hay lam|cach tot nhat de tranh)\b")
_EVASION = re.compile(r"\b(ne thue|tron thue|giau doanh thu|che giau doanh thu)\b")
_QUOTED_TEXT = re.compile(r'[“"]([^”"]+)[”"]')
_DURATION = re.compile(r"\b(\d+(?:[.,]\d+)?)\s*(ngay\s+lam\s+viec|ngay|thang|nam)\b")
_LEGAL_REFERENCE = re.compile(r"\b(dieu|khoan)\s+(\d+)\b")


def parse_answer(raw: str) -> LLMAnswer | None:
    """Parse strict answer JSON, optionally wrapped in a JSON code fence."""
    match = _JSON_FENCE.match(raw)
    candidate = match.group(1) if match else raw.strip()
    try:
        return LLMAnswer.model_validate(json.loads(candidate))
    except (json.JSONDecodeError, ValidationError, ValueError):
        return None


def validate_answer(answer: LLMAnswer, sources: list[LawEntry]) -> str | None:
    """Return a rejection reason when generated content violates output policy."""
    if not answer.citations:
        return "missing_citation"
    eligible_sources = {source.id: source for source in sources if is_usable_source(source)}
    source_ids = set(eligible_sources)
    if any(citation not in source_ids for citation in answer.citations):
        known_ids = {source.id for source in sources}
        return (
            "unverified_source"
            if any(citation in known_ids for citation in answer.citations)
            else "unknown_citation"
        )
    if any(f"[{citation}]" not in answer.answer for citation in answer.citations):
        return "citation_not_in_answer"
    normalized = normalize_text(answer.answer)
    if (
        _MONEY.search(answer.answer)
        or _MONEY_WORDS.search(answer.answer)
        or _APPROXIMATE_MONEY.search(answer.answer)
    ):
        return "money_amount"
    if _COMMANDING.search(normalized):
        return "commanding_tone"
    if _EVASION.search(normalized):
        return "evasion_instruction"
    cited_sources = [eligible_sources[citation] for citation in answer.citations]
    source_texts = [_normalize_evidence(source.noi_dung) for source in cited_sources]
    for quoted in _QUOTED_TEXT.findall(answer.answer):
        normalized_quote = _normalize_evidence(quoted)
        if not normalized_quote or not any(normalized_quote in text for text in source_texts):
            return "quote_not_in_source"
    for number, unit in _DURATION.findall(normalized):
        clean_unit = re.sub(r"\s+", " ", unit)
        c_num = _canonical_number(number)
        pattern = rf"(?<![a-z0-9])0*{re.escape(c_num)}\s+{re.escape(clean_unit)}(?![a-z0-9])"
        if not any(re.search(pattern, text) for text in source_texts):
            return "figure_not_in_source"
    for kind, number in _LEGAL_REFERENCE.findall(normalized):
        clean_kind = re.sub(r"\s+", " ", kind)
        c_num = _canonical_number(number)
        pattern = rf"(?<![a-z0-9]){re.escape(clean_kind)}\s+0*{re.escape(c_num)}(?![a-z0-9])"
        if not any(re.search(pattern, text) for text in source_texts):
            return "figure_not_in_source"
    return None


def _normalize_evidence(text: str) -> str:
    folded = unicodedata.normalize("NFD", text.casefold().replace("đ", "d"))
    without_marks = "".join(char for char in folded if unicodedata.category(char) != "Mn")
    without_marks = (
        without_marks.replace("“", '"').replace("”", '"').replace("„", '"').replace("’", "'")
    )
    return re.sub(r"\s+", " ", without_marks).strip()


def _canonical_number(value: str) -> str:
    number = value.replace(",", ".")
    if "." in number:
        whole, fraction = number.split(".", maxsplit=1)
        return f"{int(whole)}.{fraction}"
    return str(int(number))


def _contains_phrase(source: str, phrase: str) -> bool:
    return re.search(rf"(?<![a-z0-9]){re.escape(phrase)}(?![a-z0-9])", source) is not None


def validate_situation_reasons(
    reasons: list[str], *, enum_evidence: set[str], free_text: str | None
) -> str | None:
    """Reject suggestion rationales that are unsafe or not grounded in user input."""
    normalized_free_text = normalize_text(free_text or "")
    for reason in reasons:
        normalized = normalize_text(reason)
        if (
            _MONEY.search(reason)
            or _MONEY_WORDS.search(reason)
            or _APPROXIMATE_MONEY.search(reason)
        ):
            return "money_amount"
        if _COMMANDING.search(normalized):
            return "commanding_tone"
        if _EVASION.search(normalized):
            return "evasion_instruction"
        if reason not in enum_evidence and (
            not normalized_free_text or normalized not in normalized_free_text
        ):
            return "ungrounded_reason"
    return None
