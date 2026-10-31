import hashlib
import json
import logging
from datetime import UTC, datetime

import pytest

from src.core.config import Settings
from src.modules.chatbot.llm import MockLLM
from src.modules.chatbot.pipeline import ChatbotPipeline, _source_warnings
from src.modules.chatbot.retriever import KeywordRetriever
from src.modules.chatbot.schemas import ChatRequest, EffectivenessStatus, LawEntry, Segment
from src.modules.chatbot.templates import SAFE_FALLBACK_TEMPLATE


class ApprovedRetriever:
    def retrieve(self, query: str, segment: Segment, top_k: int) -> list[LawEntry]:
        del query, segment, top_k
        return [
            LawEntry(
                id="L900",
                document_number="TEST/2026",
                article="Điều 1",
                clause="Khoản 1",
                van_ban="Test-only source",
                dieu_khoan="Test-only clause",
                noi_dung="Text fixture for unit test only.",
                source_url="https://congbao.chinhphu.vn/test",
                source_domain="congbao.chinhphu.vn",
                fetched_at=datetime.now(UTC),
                content_sha256=hashlib.sha256(b"Text fixture for unit test only.").hexdigest(),
                effectiveness_status="con_hieu_luc",
                ap_dung_cho=[Segment.A1],
            )
        ]


class CapturingLLM(MockLLM):
    def __init__(self) -> None:
        self.seen_message = ""
        self.seen_context: dict[str, bool] = {}

    async def classify_intent(self, message: str, segment: Segment, step: str) -> str:
        self.seen_message = f"{message} {step}"
        return "khong"

    async def generate_answer(self, message, segment, step, context, sources) -> str:
        self.seen_message = f"{message} {step}"
        self.seen_context = context
        return json.dumps(
            {
                "answer": "Theo tài liệu test [L900].",
                "citations": ["L900"],
                "needs_expert": False,
            }
        )


class FakeLLM(MockLLM):
    def __init__(self, classification: str | Exception) -> None:
        self.classification = classification
        self.classify_calls = 0
        self.generate_calls = 0

    async def classify_intent(self, message: str, segment: Segment, step: str) -> str:
        self.classify_calls += 1
        del message, segment, step
        if isinstance(self.classification, Exception):
            raise self.classification
        return self.classification

    async def generate_answer(self, message, segment, step, context, sources) -> str:
        self.generate_calls += 1
        return await super().generate_answer(message, segment, step, context, sources)


def make_request(message: str = "Giải thích hồ sơ?") -> ChatRequest:
    return ChatRequest.model_validate(
        {
            "tin_nhan": message,
            "nhom": "A1",
            "buoc": "Chuẩn bị hồ sơ",
            "co": {"co_lao_dong": True, "dia_chi": True},
        }
    )


@pytest.mark.asyncio
async def test_pipeline_returns_fixed_no_source_without_placeholder_law() -> None:
    pipeline = ChatbotPipeline(
        Settings(_env_file=None, chatbot_mock_mode=True),
        KeywordRetriever(),
        MockLLM(),
    )

    response = await pipeline.answer(make_request("nguyên văn điều luật"))

    assert response.mode == 3
    assert response.needs_expert is True
    assert "Chưa tìm thấy căn cứ pháp lý đủ điều kiện" in response.answer
    assert response.citations == []


@pytest.mark.asyncio
async def test_pipeline_sanitizes_before_llm_and_only_passes_allowlisted_flags() -> None:
    llm = CapturingLLM()
    pipeline = ChatbotPipeline(
        Settings(_env_file=None, chatbot_mock_mode=True), ApprovedRetriever(), llm
    )
    request = make_request(
        "Tôi tên là Nguyễn Văn An, MST 0123456789, email a@example.vn, địa chỉ: 12 Đường ABC"
    )

    response = await pipeline.answer(request)

    assert response.mode == 1
    assert "Nguyễn Văn An" not in llm.seen_message
    assert "0123456789" not in llm.seen_message
    assert "a@example.vn" not in llm.seen_message
    assert "12 Đường ABC" not in llm.seen_message
    assert llm.seen_context == {"co_lao_dong": True}
    assert response.citations == ["L900"]
    assert response.sources[0].document_number == "TEST/2026"
    assert response.sources[0].article == "Điều 1"
    assert response.sources[0].source_url == "https://congbao.chinhphu.vn/test"
    assert response.sources[0].fetched_at is not None
    assert response.data_note is not None
    assert response.sources[0].fetched_at.date().isoformat() in response.data_note
    assert response.ai_disclosure == (
        "Gợi ý do AI hỗ trợ, bạn là người xác nhận; không thay thế tư vấn chuyên môn."
    )
    assert response.scope_note == (
        "Chỉ giải thích tổng quát theo nguồn được cung cấp; trường hợp cụ thể cần chuyên gia."
    )


@pytest.mark.asyncio
async def test_fabricated_deadline_uses_expert_safe_fallback() -> None:
    class HallucinatingLLM(CapturingLLM):
        async def generate_answer(self, message, segment, step, context, sources) -> str:
            del message, segment, step, context
            return json.dumps(
                {
                    "answer": "Thời hạn là 10 ngày [L900].",
                    "citations": ["L900"],
                    "needs_expert": False,
                }
            )

    pipeline = ChatbotPipeline(
        Settings(_env_file=None, chatbot_mock_mode=True), ApprovedRetriever(), HallucinatingLLM()
    )

    response = await pipeline.answer(make_request())

    assert response.answer == SAFE_FALLBACK_TEMPLATE
    assert response.mode == 3
    assert response.needs_expert is True
    assert response.block_reason == "figure_not_in_source"


@pytest.mark.asyncio
async def test_amended_citation_adds_warning_and_escalates() -> None:
    class AmendedRetriever(ApprovedRetriever):
        def retrieve(self, query: str, segment: Segment, top_k: int) -> list[LawEntry]:
            source = super().retrieve(query, segment, top_k)[0]
            return [source.model_copy(update={"amended_by": "2/2026/QH15"})]

    pipeline = ChatbotPipeline(
        Settings(_env_file=None, chatbot_mock_mode=True), AmendedRetriever(), CapturingLLM()
    )

    response = await pipeline.answer(make_request())

    assert response.needs_expert is True
    assert response.mode == 3
    assert "văn bản sửa đổi" in response.answer
    assert response.sources[0].amended_by == "2/2026/QH15"


def test_unknown_effectiveness_source_has_warning() -> None:
    source = (
        ApprovedRetriever()
        .retrieve("", Segment.A1, 1)[0]
        .model_copy(update={"effectiveness_status": EffectivenessStatus.UNKNOWN})
    )

    assert _source_warnings([source]) == ["Cảnh báo: tình trạng hiệu lực của nguồn chưa rõ."]


@pytest.mark.asyncio
async def test_regex_guardrail_stops_before_classifier_call() -> None:
    llm = CapturingLLM()
    pipeline = ChatbotPipeline(
        Settings(_env_file=None, chatbot_mock_mode=True), ApprovedRetriever(), llm
    )

    response = await pipeline.answer(make_request("Làm sao để giấu doanh thu?"))

    assert response.mode == 3
    assert response.needs_expert is True
    assert llm.seen_message == ""


@pytest.mark.parametrize(
    ("message", "expected_label"),
    [
        ("Anh Hùng bị thanh tra thuế", "bi_co_quan_lien_he"),
        ("chị Lan bị truy thu thuế", "bi_co_quan_lien_he"),
        ("Chị Lan muốn giấu doanh thu", "ne_thue"),
        ("ông Nam muốn né thuế", "ne_thue"),
        ("bà Hoa nợ thuế 3 kỳ", "no_ton_dong"),
        ("Tôi tên là Lan giấu doanh thu", "ne_thue"),
        ("chị Lan khai thấp doanh thu", "ne_thue"),
    ],
)
@pytest.mark.asyncio
async def test_pipeline_checks_original_message_before_redaction(
    message: str, expected_label: str
) -> None:
    llm = CapturingLLM()
    pipeline = ChatbotPipeline(
        Settings(_env_file=None, chatbot_mock_mode=True), ApprovedRetriever(), llm
    )
    request = ChatRequest.model_validate(
        {"tin_nhan": message, "nhom": "A2", "buoc": "Đang chuẩn bị"}
    )

    response = await pipeline.answer(request)

    assert response.mode == 3
    assert response.block_reason == expected_label
    assert llm.seen_message == ""


@pytest.mark.parametrize(
    "classification",
    ["nhan_khong_duoc_ho_tro", "", RuntimeError("LLM không phản hồi")],
    ids=["unknown-label", "empty-output", "classifier-error"],
)
@pytest.mark.asyncio
async def test_layer_two_classifier_failure_uses_failsafe_without_continuing(
    classification: str | Exception,
) -> None:
    llm = FakeLLM(classification)
    pipeline = ChatbotPipeline(
        Settings(
            _env_file=None,
            chatbot_mock_mode=True,
            chatbot_failsafe="khong_chac_chan",
        ),
        ApprovedRetriever(),
        llm,
    )

    response = await pipeline.answer(make_request("Câu hỏi thủ tục thông thường"))

    assert response.mode == 3
    assert response.needs_expert is True
    assert response.block_reason == "khong_chac_chan"
    assert llm.generate_calls == 0


@pytest.mark.asyncio
async def test_layer_two_can_escalate_a_neutral_question_to_a_risk_label() -> None:
    llm = FakeLLM("ne_thue")
    pipeline = ChatbotPipeline(
        Settings(
            _env_file=None,
            chatbot_mock_mode=True,
            chatbot_guardrail_cache_size=0,
        ),
        ApprovedRetriever(),
        llm,
    )

    response = await pipeline.answer(make_request("Tôi cần chuẩn bị hồ sơ nào?"))

    assert response.block_reason == "ne_thue"
    assert response.needs_expert is True
    assert llm.classify_calls == 1
    assert llm.generate_calls == 0


@pytest.mark.asyncio
async def test_layer_two_cannot_clear_a_risk_already_found_by_regex() -> None:
    llm = FakeLLM("khong")
    pipeline = ChatbotPipeline(
        Settings(_env_file=None, chatbot_mock_mode=True, chatbot_guardrail_cache_size=0),
        ApprovedRetriever(),
        llm,
    )

    response = await pipeline.answer(make_request("Làm sao để giấu doanh thu?"))

    assert response.block_reason == "ne_thue"
    assert llm.classify_calls == 0
    assert llm.generate_calls == 0


@pytest.mark.parametrize(
    ("citations", "answer", "expected_reason"),
    [
        ([], "Câu trả lời chưa có nguồn.", "missing_citation"),
        (["L999"], "Theo nguồn [L999].", "unknown_citation"),
    ],
)
@pytest.mark.asyncio
async def test_pipeline_blocks_answers_without_a_valid_source_citation(
    citations: list[str], answer: str, expected_reason: str
) -> None:
    class RawAnswerLLM(FakeLLM):
        async def generate_answer(self, message, segment, step, context, sources) -> str:
            self.generate_calls += 1
            return json.dumps(
                {"answer": answer, "citations": citations, "needs_expert": True},
                ensure_ascii=False,
            )

    llm = RawAnswerLLM("khong")
    pipeline = ChatbotPipeline(
        Settings(_env_file=None, chatbot_mock_mode=True, chatbot_guardrail_cache_size=0),
        ApprovedRetriever(),
        llm,
    )

    response = await pipeline.answer(make_request("Tôi cần hồ sơ gì?"))

    assert response.block_reason == expected_reason
    assert response.citations == []
    assert response.needs_expert is True


@pytest.mark.parametrize(
    "message",
    [
        "Tôi nên giải thể hay chuyển nhượng?",
        "Làm sao để đỡ bị phạt?",
    ],
)
@pytest.mark.asyncio
async def test_decision_questions_return_fixed_boundary_without_calling_llm(message: str) -> None:
    llm = FakeLLM("khong")
    pipeline = ChatbotPipeline(
        Settings(_env_file=None, chatbot_mock_mode=True, chatbot_guardrail_cache_size=0),
        ApprovedRetriever(),
        llm,
    )

    response = await pipeline.answer(make_request(message))

    assert response.answer == (
        "Hệ thống chỉ mô tả các hướng; quyết định thuộc về bạn, có thể tham khảo chuyên gia."
    )
    assert response.needs_expert is True
    assert response.block_reason == "hoi_quyet_dinh_thay"
    assert llm.classify_calls == 0
    assert llm.generate_calls == 0


@pytest.mark.asyncio
async def test_procedure_question_is_not_blocked_as_decision_advice() -> None:
    llm = FakeLLM("khong")
    pipeline = ChatbotPipeline(
        Settings(_env_file=None, chatbot_mock_mode=True, chatbot_guardrail_cache_size=0),
        ApprovedRetriever(),
        llm,
    )

    response = await pipeline.answer(make_request("Hồ sơ giải thể gồm những gì?"))

    assert response.block_reason is None
    assert response.needs_expert is False
    assert llm.classify_calls == 1
    assert llm.generate_calls == 1


@pytest.mark.asyncio
async def test_pipeline_skips_answer_generation_when_no_source_meets_threshold() -> None:
    llm = FakeLLM("khong")
    pipeline = ChatbotPipeline(
        Settings(
            _env_file=None,
            chatbot_mock_mode=True,
            chatbot_guardrail_cache_size=0,
            chatbot_min_retrieval_score=1,
        ),
        KeywordRetriever(entries=ApprovedRetriever().retrieve("", Segment.A1, 6)),
        llm,
    )

    response = await pipeline.answer(make_request("vũ trụ bóng tối xa xôi"))

    assert response.mode == 3
    assert response.block_reason == "no_relevant_source"
    assert llm.classify_calls == 0
    assert llm.generate_calls == 0


@pytest.mark.asyncio
async def test_money_question_uses_fixed_self_lookup_template() -> None:
    pipeline = ChatbotPipeline(
        Settings(_env_file=None, chatbot_mock_mode=True), ApprovedRetriever(), CapturingLLM()
    )

    response = await pipeline.answer(make_request("Tôi phải nộp bao nhiêu tiền?"))

    assert response.mode == 2
    assert response.needs_expert is False
    assert "không tính hoặc ước lượng" in response.answer
    assert "cổng Thuế điện tử" in response.answer
    assert "POST /cases/brief" not in response.answer
    assert not any(character.isdigit() for character in response.answer)


@pytest.mark.asyncio
async def test_service_fee_question_points_only_to_case_brief() -> None:
    pipeline = ChatbotPipeline(
        Settings(_env_file=None, chatbot_mock_mode=True), ApprovedRetriever(), CapturingLLM()
    )

    response = await pipeline.answer(make_request("Phí dịch vụ tư vấn là bao nhiêu?"))

    assert response.block_reason == "hoi_so_tien"
    assert "POST /cases/brief" in response.answer
    assert "tiền nộp ngân sách" in response.answer


@pytest.mark.asyncio
async def test_survey_context_stops_chat_before_classifier_retrieval_or_generation() -> None:
    llm = FakeLLM("khong")
    retriever = ApprovedRetriever()
    pipeline = ChatbotPipeline(Settings(_env_file=None, chatbot_mock_mode=True), retriever, llm)
    request = ChatRequest.model_validate(
        {"tin_nhan": "Tôi cần chuẩn bị gì?", "nhom": "A2", "co": {"co_thong_bao_thue": True}}
    )

    response = await pipeline.answer(request)

    assert response.mode == 3
    assert response.block_reason == "bi_co_quan_lien_he"
    assert llm.classify_calls == 0
    assert llm.generate_calls == 0


@pytest.mark.asyncio
async def test_neutral_question_without_survey_flags_continues_normally() -> None:
    llm = FakeLLM("khong")
    pipeline = ChatbotPipeline(
        Settings(_env_file=None, chatbot_mock_mode=True), ApprovedRetriever(), llm
    )

    response = await pipeline.answer(
        ChatRequest.model_validate({"tin_nhan": "Tôi cần chuẩn bị gì?", "nhom": "A2"})
    )

    assert response.mode == 1
    assert llm.classify_calls == 1
    assert llm.generate_calls == 1


@pytest.mark.asyncio
async def test_penalty_principle_question_retrieves_and_always_recommends_expert() -> None:
    llm = CapturingLLM()
    pipeline = ChatbotPipeline(
        Settings(_env_file=None, chatbot_mock_mode=True), ApprovedRetriever(), llm
    )

    response = await pipeline.answer(make_request("Có bị phạt không nếu chưa kê khai?"))

    assert response.block_reason is None
    assert response.needs_expert is True
    assert response.mode == 3
    assert response.citations == ["L900"]
    assert "có thể kết nối chuyên gia" in response.answer


@pytest.mark.asyncio
async def test_penalty_principle_without_source_uses_expert_no_source_response() -> None:
    pipeline = ChatbotPipeline(
        Settings(_env_file=None, chatbot_mock_mode=True), KeywordRetriever(), CapturingLLM()
    )

    response = await pipeline.answer(make_request("Có bị phạt không nếu chưa kê khai?"))

    assert response.mode == 3
    assert response.needs_expert is True
    assert response.block_reason == "no_relevant_source"
    assert "Chưa tìm thấy căn cứ pháp lý đủ điều kiện" in response.answer


@pytest.mark.asyncio
async def test_pipeline_accepts_empty_current_step() -> None:
    llm = CapturingLLM()
    pipeline = ChatbotPipeline(
        Settings(_env_file=None, chatbot_mock_mode=True), ApprovedRetriever(), llm
    )
    request = ChatRequest.model_validate({"tin_nhan": "Giải thích hồ sơ", "nhom": "A1"})

    response = await pipeline.answer(request)

    assert response.mode == 1
    assert llm.seen_message.endswith(" ")


@pytest.mark.asyncio
async def test_log_record_uses_redacted_message(caplog) -> None:
    pipeline = ChatbotPipeline(
        Settings(_env_file=None, chatbot_mock_mode=True), KeywordRetriever(), MockLLM()
    )
    request = make_request(
        "Tôi tên là Nguyễn Văn An, MST: 0123456789, email a@example.vn, số 0912345678 " + "x" * 300
    )
    caplog.set_level(logging.INFO)

    await pipeline.answer(request)

    assert "Nguyễn Văn An" not in caplog.text
    assert "0123456789" not in caplog.text
    assert "a@example.vn" not in caplog.text
    assert "0912345678" not in caplog.text
    log_records = [
        json.loads(record.getMessage())
        for record in caplog.records
        if record.getMessage().startswith("{")
    ]
    chatbot_records = [record for record in log_records if "message_redacted" in record]
    assert chatbot_records
    assert all(len(record["message_redacted"]) <= 200 for record in chatbot_records)


@pytest.mark.asyncio
async def test_missing_provenance_returns_fixed_no_source_without_answer_generation() -> None:
    llm = FakeLLM(classification="khong")
    pipeline = ChatbotPipeline(
        Settings(
            _env_file=None,
            chatbot_mock_mode=True,
            chatbot_guardrail_cache_size=0,
        ),
        KeywordRetriever(),
        llm,
    )
    request = ChatRequest.model_validate(
        {
            "tin_nhan": "Giải thể doanh nghiệp cần những bước nào?",
            "nhom": "B1",
            "buoc": "",
        }
    )

    response = await pipeline.answer(request)

    assert response.mode == 3
    assert response.block_reason == "no_relevant_source"
    assert llm.generate_calls == 0


@pytest.mark.parametrize(
    ("message", "reason"),
    [
        ("Phạt bao nhiêu nếu giải thể?", "hoi_so_tien"),
        ("Làm sao để né thuế?", "ne_thue"),
        ("Tôi đã nhận thông báo giải trình của cơ quan thuế", "bi_co_quan_lien_he"),
    ],
)
@pytest.mark.asyncio
async def test_guardrails_remain_active(message: str, reason: str) -> None:
    pipeline = ChatbotPipeline(
        Settings(
            _env_file=None,
            chatbot_mock_mode=True,
            chatbot_guardrail_cache_size=0,
        ),
        KeywordRetriever(),
        MockLLM(),
    )

    response = await pipeline.answer(make_request(message))

    assert response.block_reason == reason
