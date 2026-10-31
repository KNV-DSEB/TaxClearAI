import hashlib
import json
from datetime import UTC, datetime

from src.modules.chatbot.schemas import LawEntry, LLMAnswer, Segment
from src.modules.chatbot.validator import parse_answer, validate_answer


def source() -> LawEntry:
    return LawEntry(
        id="L001",
        van_ban="Test source",
        dieu_khoan="Điều 1, Khoản 1",
        document_number="TEST/2026",
        article="Điều 1",
        clause="Khoản 1",
        noi_dung="Nội dung nguyên văn dùng trong fixture kiểm thử.",
        source_url="https://congbao.chinhphu.vn/test",
        source_domain="congbao.chinhphu.vn",
        fetched_at=datetime.now(UTC),
        content_sha256=hashlib.sha256(
            "Nội dung nguyên văn dùng trong fixture kiểm thử.".encode()
        ).hexdigest(),
        effectiveness_status="con_hieu_luc",
        ap_dung_cho=[Segment.A1],
    )


def test_parses_json_code_fence() -> None:
    parsed = parse_answer(
        '```json\n{"answer":"Căn cứ [L001]","citations":["L001"],"needs_expert":false}\n```'
    )
    assert parsed is not None
    assert parsed.citations == ["L001"]


def test_validator_accepts_cited_answer() -> None:
    parsed = parse_answer(
        '{"answer":"Theo đoạn trích [L001].","citations":["L001"],"needs_expert":false}'
    )
    assert parsed is not None
    assert validate_answer(parsed, [source()]) is None


def test_validator_rejects_money_unknown_citation_and_commanding_tone() -> None:
    money = parse_answer(
        '{"answer":"Bạn nộp 5 triệu đồng [L001]","citations":["L001"],"needs_expert":false}'
    )
    unknown = parse_answer(
        '{"answer":"Theo nguồn [L999]","citations":["L999"],"needs_expert":false}'
    )
    command = parse_answer(
        '{"answer":"Bạn phải làm ngay [L001]","citations":["L001"],"needs_expert":false}'
    )
    assert money and validate_answer(money, [source()]) == "money_amount"
    assert unknown and validate_answer(unknown, [source()]) == "unknown_citation"
    assert command and validate_answer(command, [source()]) == "commanding_tone"


def test_validator_requires_citations_for_non_expert_answer() -> None:
    parsed = parse_answer('{"answer":"Trả lời không nguồn","citations":[],"needs_expert":false}')
    assert parsed and validate_answer(parsed, [source()]) == "missing_citation"


def test_validator_requires_citation_even_when_answer_escalates_to_expert() -> None:
    parsed = parse_answer(
        '{"answer":"Tình huống cần chuyên gia rà soát.","citations":[],"needs_expert":true}'
    )

    assert parsed and validate_answer(parsed, [source()]) == "missing_citation"


def test_validator_rejects_expired_source_without_review_flags() -> None:
    parsed = parse_answer(
        '{"answer":"Theo nguồn [L001].","citations":["L001"],"needs_expert":false}'
    )
    expired_source = source().model_copy(update={"effectiveness_status": "het_hieu_luc"})

    assert parsed is not None
    assert validate_answer(parsed, [expired_source]) == "unverified_source"


def test_validator_rejects_approximate_money_without_digits() -> None:
    parsed = parse_answer(
        '{"answer":"Khoảng vài triệu đồng [L001]","citations":["L001"],"needs_expert":false}'
    )
    assert parsed and validate_answer(parsed, [source()]) == "money_amount"


def test_validator_rejects_compound_spelled_money_amount() -> None:
    parsed = parse_answer(
        '{"answer":"Khoản này khoảng một trăm triệu đồng [L001]",'
        '"citations":["L001"],"needs_expert":false}'
    )
    assert parsed and validate_answer(parsed, [source()]) == "money_amount"


def test_validator_rejects_percentage_in_penalty_principle_answer() -> None:
    parsed = parse_answer(
        '{"answer":"Mức áp dụng là 12 phần trăm [L001]","citations":["L001"],"needs_expert":true}'
    )

    assert parsed and validate_answer(parsed, [source()]) == "money_amount"


def evidence_source() -> LawEntry:
    text = "Điều 3. Khoản 2. “Người nộp thuế” gửi hồ sơ trong thời hạn 5 ngày làm việc."
    return source().model_copy(
        update={"noi_dung": text, "content_sha256": hashlib.sha256(text.encode()).hexdigest()}
    )


def answer(text: str) -> LLMAnswer:
    parsed = parse_answer(
        json.dumps(
            {"answer": text, "citations": ["L001"], "needs_expert": False}, ensure_ascii=False
        )
    )
    assert parsed is not None
    return parsed


def test_answer_with_supported_quote_duration_and_provision_passes() -> None:
    candidate = answer("Theo Điều 3, Khoản 2, “Người nộp thuế” gửi trong 5 ngày làm việc [L001].")

    assert validate_answer(candidate, [evidence_source()]) is None


def test_answer_with_fabricated_quote_is_rejected() -> None:
    assert validate_answer(answer("“Cơ quan phải hoàn trả ngay” [L001]."), [evidence_source()]) == (
        "quote_not_in_source"
    )


def test_answer_with_fabricated_deadline_is_rejected() -> None:
    assert validate_answer(
        answer("Hồ sơ nộp trong 10 ngày làm việc [L001]."), [evidence_source()]
    ) == ("figure_not_in_source")


def test_answer_with_fabricated_article_is_rejected() -> None:
    assert validate_answer(answer("Căn cứ Điều 4, Khoản 2 [L001]."), [evidence_source()]) == (
        "figure_not_in_source"
    )
