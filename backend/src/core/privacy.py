import re
import unicodedata

from src.modules.chatbot.guardrail import detect_risk_label_at_start

_EMAIL = re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")
_TAX_ID = re.compile(r"(?i)(?:mã số thuế|mst)\s*[:#]?\s*\d{10}(?:\d{3})?|\b\d{13}\b")
_ID_NUMBER = re.compile(r"(?<!\d)\d{12}(?!\d)")
_PHONE = re.compile(r"(?<!\w)(?:\+?84|0)(?:[ .()-]*\d){8,10}(?!\w)")
_LONG_ID = re.compile(r"(?<!\d)\d{9,13}(?!\d)")
_ADDRESS_PII = re.compile(r"(?i)(địa chỉ|nơi ở|trụ sở|địa điểm kinh doanh)\s*[:=]?\s*[^,;.!?]+")

_WORD = r"[^\W\d_]+(?:[-'][^\W\d_]+)?"
_WORD_PATTERN = re.compile(_WORD, re.UNICODE)
_EXPLICIT_NAME_PREFIX = re.compile(
    r"(?i)\b(?:(?:tôi|toi)\s+(?:tên|ten)\s+(?:là|la)|"
    r"(?:tên|ten)\s+(?:tôi|toi)\s+(?:là|la)|(?:tôi|toi)\s+(?:là|la)|"
    r"(?:họ|ho)\s+tên\s*[:=]|(?:chủ|chu)\s+hộ\s*[:=]|"
    r"(?:người|nguoi)\s+(?:đại|dai)\s+(?:diện|dien)\s*[:=])\s*"
)
_HONORIFIC_PREFIX = re.compile(r"(?i)\b(?:ông|ong|bà|ba|anh|chị|chi|cô|co|chú|chu)\b\s*[:=]?\s*")
_HONORIFIC_BEFORE = re.compile(r"(?i)\b(?:ông|ong|bà|ba|anh|chị|chi|cô|co|chú|chu)\s+$")
_COMMON_SURNAMES = (
    "Nguyễn|Nguyen|Trần|Tran|Lê|Le|Phạm|Pham|Hoàng|Hoang|Phan|Vũ|Vu|Võ|Vo|"
    "Đặng|Dang|Bùi|Bui|Đỗ|Do|Hồ|Ho|Ngô|Ngo|Dương|Duong|Lý|Ly|Trương|Truong|"
    "Đinh|Dinh|Cao|Tạ|Ta|Mai|Lưu|Luu|Chu|La|Hà|Ha"
)
_PERSON_NAME = re.compile(
    rf"(?<!\w)(?P<name>(?:{_COMMON_SURNAMES})\s+{_WORD}\s+{_WORD}(?:\s+{_WORD})?)(?!\w)",
    re.IGNORECASE,
)
_EXEMPTIONS = re.compile(
    rf"(?i)\b(?:hộ\s+kinh\s+doanh(?:\s+cá\s+thể)?|doanh\s+nghiệp|cơ\s+quan\s+thuế)\b"
    rf"|\b(?:quận|huyện|phường|xã|tỉnh|thành\s+phố|tp\.?)\s+{_WORD}"
    rf"(?:\s+(?!(?:người|ông|bà|anh|chị|cô|chú|chủ|hộ|doanh|kinh|cơ|mã|đăng|đang|theo|"
    rf"tại|ở|có|là)\b){_WORD}){{0,2}}"
    rf"|\b(?:luật|nghị\s+định|thông\s+tư)\b"
    rf"(?:(?!\b(?:ông|bà|anh|chị|cô|chú|chủ\s+hộ|người\s+đại\s+diện|họ\s+tên|"
    rf"tôi\s+tên\s+là|tên\s+tôi\s+là)\b)[^\n,;.!?]){{0,100}}"
)
_NAME_STOP_WORDS = {
    "va",
    "bi",
    "dang",
    "muon",
    "can",
    "co",
    "la",
    "o",
    "tai",
    "ban",
    "kinh",
    "doanh",
    "giam",
    "doc",
    "chu",
    "thue",
    "no",
    "giau",
    "khai",
    "ke",
    "ne",
    "tron",
    "lach",
}


def redact_sensitive_data(text: str) -> str:
    """Mask identity data while preserving ordinary text and risk phrases."""
    text = _EMAIL.sub("[email đã ẩn]", text)
    text = _TAX_ID.sub("[MST đã ẩn]", text)
    text = _ID_NUMBER.sub("[CCCD đã ẩn]", text)
    text = _PHONE.sub("[số điện thoại đã ẩn]", text)
    text = _LONG_ID.sub("[chuỗi số đã ẩn]", text)
    text = _ADDRESS_PII.sub(r"\1: [địa chỉ đã ẩn]", text)
    text = _redact_after_prefix(text, _EXPLICIT_NAME_PREFIX, allow_lowercase=True)
    text = _redact_after_prefix(text, _HONORIFIC_PREFIX, allow_lowercase=False)
    return _redact_fallback_names(text)


def _redact_after_prefix(text: str, pattern: re.Pattern[str], *, allow_lowercase: bool) -> str:
    for match in reversed(list(pattern.finditer(text))):
        start = match.end()
        end = _captured_name_end(text, start, allow_lowercase=allow_lowercase)
        if end is None:
            continue
        protected = [item.span() for item in _EXEMPTIONS.finditer(text)]
        if not _overlaps_protected(start, end, protected):
            text = text[:start] + "[tên riêng đã ẩn]" + text[end:]
    return text


def _captured_name_end(text: str, start: int, *, allow_lowercase: bool) -> int | None:
    cursor = start
    captured_end: int | None = None
    for _ in range(4):
        while cursor < len(text) and text[cursor].isspace():
            cursor += 1
        token_match = _WORD_PATTERN.match(text, cursor)
        if token_match is None:
            break
        token = token_match.group(0)
        normalized_token = _normalize_phrase(token)
        if (
            normalized_token == "dang"
            and token.casefold() == "dang"
            and _has_name_continuation(text, token_match.end())
        ):
            normalized_token = ""
        if (
            normalized_token in _NAME_STOP_WORDS
            or detect_risk_label_at_start(text[cursor:]) is not None
            or (not allow_lowercase and not token[0].isupper())
        ):
            break
        captured_end = token_match.end()
        cursor = captured_end
    return captured_end


def _has_name_continuation(text: str, start: int) -> bool:
    cursor = start
    for _ in range(2):
        while cursor < len(text) and text[cursor].isspace():
            cursor += 1
        token_match = _WORD_PATTERN.match(text, cursor)
        if token_match is None:
            return False
        token = token_match.group(0)
        if (
            _normalize_phrase(token) in _NAME_STOP_WORDS
            or detect_risk_label_at_start(text[cursor:]) is not None
        ):
            return False
        cursor = token_match.end()
    return True


def _redact_fallback_names(text: str) -> str:
    for match in reversed(list(_PERSON_NAME.finditer(text))):
        start = match.start("name")
        end = _captured_name_end(text, start, allow_lowercase=False)
        if end is None or len(_WORD_PATTERN.findall(text[start:end])) < 2:
            continue
        if _HONORIFIC_BEFORE.search(text[max(0, start - 24) : start]):
            continue
        protected = [item.span() for item in _EXEMPTIONS.finditer(text)]
        if not _overlaps_protected(start, end, protected):
            text = text[:start] + "[tên riêng đã ẩn]" + text[end:]
    return text


def _overlaps_protected(start: int, end: int, protected: list[tuple[int, int]]) -> bool:
    return any(
        start < protected_end and end > protected_start
        for protected_start, protected_end in protected
    )


def _normalize_phrase(phrase: str) -> str:
    normalized = unicodedata.normalize("NFD", phrase.lower().replace("đ", "d"))
    return "".join(char for char in normalized if unicodedata.category(char) != "Mn")
