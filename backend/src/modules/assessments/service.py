from collections.abc import Callable
from datetime import UTC, date, datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

from src.core.errors import ApplicationError
from src.modules.assessments.content import (
    CHECKLIST_NOTE,
    COMPANY_CONDITIONAL,
    DOCUMENTS,
    DOCUMENTS_A1,
    DOCUMENTS_A2,
    DOCUMENTS_A3,
    DOCUMENTS_B1,
    DOCUMENTS_B2,
    DOCUMENTS_HOUSEHOLD,
    HOUSEHOLD_CONDITIONAL,
    IN_SCOPE,
    NOTICE,
    UNKNOWN_VALUES,
    VERSION,
    get_questionnaire,
    is_visible,
)
from src.modules.assessments.domain import (
    AssessmentRecord,
    AssessmentSummaryRecord,
    SourceRecord,
)
from src.modules.assessments.repository import AssessmentRepository
from src.modules.assessments.schemas import (
    Answers,
    AssessmentListItem,
    AssessmentPage,
    AssessmentView,
    CaseFilter,
    CaseStatus,
    ChecklistCounts,
    ChecklistItemView,
    CreateAssessment,
    ItemStatus,
    Question,
    Questionnaire,
    Scope,
    Summary,
)


def read_questionnaire() -> Questionnaire:
    return get_questionnaire()


def get_approved_chat_sources() -> list[SourceRecord]:
    return [
        SourceRecord(
            id="product-guide",
            title="Hướng dẫn sử dụng Tax Clear",
            url="/huong-dan",
            text=(
                "Bản thử hỗ trợ hộ kinh doanh và doanh nghiệp chuẩn bị khảo sát hồ sơ. "
                "Đăng nhập bằng tài khoản được cấp. Trả lời câu hỏi chẩn đoán; "
                "có thể chọn chưa biết hoặc "
                "để trống năm. Chọn Lưu và xem hồ sơ ở cuối để lưu. "
                "Checklist giúp theo dõi giấy tờ đã có, còn thiếu hoặc cần xác minh. "
                "Có ba trạng thái: "
                "Đã có, Còn thiếu, Cần xác minh. Thay đổi trạng thái, đợi thông báo đã lưu rồi "
                "tải lại để kiểm tra. Sau khi đăng nhập, trang Hồ sơ của tôi liệt kê các hồ sơ "
                "đã lưu để mở lại. Hồ sơ hết hạn truy cập sau 7 ngày; hồ sơ hết hạn vẫn hiện "
                "trong danh sách để bạn xóa. Có thể xóa hồ sơ thử sau bước xác nhận. "
                "Chỉ dùng dữ liệu giả định, không tải chứng từ. "
                "Chat không ghi nhớ hội thoại, không nhận hồ sơ đã lưu, không tính thuế/phạt. "
                "Đây là hướng dẫn sử dụng các chức năng trên web."
            ),
            reviewed_at=date(2026, 10, 30),
            kind="product",
        )
    ]


DOCUMENTS_BY_SCOPE = {
    "a1": DOCUMENTS_A1,
    "a2": DOCUMENTS_A2,
    "a3": DOCUMENTS_A3,
    "b1": DOCUMENTS_B1,
    "b2": DOCUMENTS_B2,
    "household": DOCUMENTS_HOUSEHOLD,
}

Answered = dict[str, Any]


def normalize_answers(data: Answers) -> Answered:
    """Kiểm tra câu bắt buộc và bỏ đáp án của câu không áp dụng, để không lưu dữ liệu thừa."""
    answers = data.model_dump(by_alias=True, mode="json")
    missing = []
    for question in get_questionnaire().questions:
        if not is_visible(question, answers):
            answers[question.id] = None
        elif question.required and answers.get(question.id) in (None, ""):
            missing.append(question.id)
    if missing:
        raise ApplicationError(422, "Vui lòng trả lời đủ các câu hỏi bắt buộc.")
    return answers


def classify(answers: Answered) -> Scope:
    """Bản thử chỉ có danh mục cho giải thể hoặc chấm dứt; thủ tục khác chuyển cho chuyên viên."""
    if answers.get("procedure") != "dissolution":
        return "out_of_scope"
    if answers.get("businessType") == "household":
        return "household"
    return "b1" if answers.get("hasRevenue") == "no" else "b2"


def describe(question: Question, value: object) -> str:
    if question.kind == "choice":
        return next(
            (option.label for option in question.options if option.value == value), str(value)
        )
    if question.kind == "number" and isinstance(value, int):
        return f"{value:,}".replace(",", ".") + (f" {question.unit}" if question.unit else "")
    return str(value)


# Mỗi dấu hiệu chỉ nêu việc cần xác minh với chuyên viên, không kết luận pháp lý
RISK_FLAGS: list[tuple[Callable[[Answered], bool], str]] = [
    (
        lambda a: a.get("operatingStatus") == "forced",
        "Cơ sở bị yêu cầu hoặc buộc chấm dứt: nên trao đổi với chuyên gia sớm để xác định "
        "thời hạn và nghĩa vụ.",
    ),
    (
        lambda a: a.get("dnDebtGuarantee") == "no",
        "Doanh nghiệp chưa bảo đảm thanh toán toàn bộ nợ và nghĩa vụ tài sản: cần chuyên gia "
        "xem xét trước khi chọn hướng xử lý.",
    ),
    (
        lambda a: (
            a.get("dnTaxDebt") in {"yes", "unreconciled"} or a.get("hhTaxObligation") == "yes"
        ),
        "Còn nghĩa vụ thuế, tiền phạt hoặc tiền chậm nộp chưa xác nhận: cần đối chiếu với cơ quan "
        "thuế qua chuyên viên.",
    ),
    (
        lambda a: a.get("hhEmployees") == "unresolved",
        "Còn người lao động chưa giải quyết xong quyền lợi: cần chuyên viên hướng dẫn.",
    ),
    (
        lambda a: (
            a.get("recordsAccess") in {"none", "unknown_location"}
            or a.get("dnRecords") in {"lost", "old_accountant", "unclear"}
            or a.get("hhInvoiceSystem") == "inaccessible"
        ),
        "Hồ sơ, sổ sách hoặc dữ liệu khó truy xuất: cần chuyên viên đánh giá cách khôi phục "
        "hoặc xác minh.",
    ),
]
SCOPE_REASONS: dict[str, str] = {
    "out_of_scope": (
        "Bản thử chỉ chuẩn bị hồ sơ giải thể hoặc chấm dứt hoạt động; nhu cầu tạm ngừng hoặc "
        "chuyển đổi cần trao đổi với chuyên viên."
    ),
    "household": (
        "Ưu tiên xác nhận quy trình chấm dứt hoạt động hộ kinh doanh và nghĩa vụ thuế trước khi "
        "đăng ký hộ mới."
    ),
    "b1": (
        "Cần xác minh tình trạng doanh thu, hóa đơn và nghĩa vụ còn lại trước khi chọn thủ tục."
    ),
    "b2": (
        "Doanh nghiệp đã phát sinh doanh thu: cần rà soát quyết toán thuế, hóa đơn và nghĩa vụ "
        "còn lại trước khi chọn thủ tục."
    ),
}


def build_summary(answers: Answered) -> Summary:
    scope = classify(answers)
    known, unknown = [], []
    for question in get_questionnaire().questions:
        if not is_visible(question, answers):
            continue
        value = answers.get(question.id)
        if value in (None, "") or value in UNKNOWN_VALUES:
            unknown.append(question.label)
        else:
            known.append(f"{question.label} — {describe(question, value)}")
    reasons = [SCOPE_REASONS[scope]] if scope in SCOPE_REASONS else []
    reasons += [text for applies, text in RISK_FLAGS if applies(answers)]
    return Summary(
        scope=scope,
        known_facts=known,
        unknown_facts=unknown,
        review_reasons=reasons,
        notice=NOTICE,
    )


def conditional_documents(answers: Answered, scope: Scope) -> list[tuple[str, str]]:
    """Mục thêm vào danh mục khi chính câu trả lời cho thấy có liên quan."""
    picks: list[str] = []
    table: dict[str, str] = {}
    if scope == "household":
        table = HOUSEHOLD_CONDITIONAL
        if answers.get("hhTaxObligation") == "yes":
            picks.append("missing_tax_returns")
        if answers.get("hhConditional") == "yes":
            picks.append("licenses")
        if answers.get("hhEmployees") == "unresolved":
            picks.append("labor_rights")
        if answers.get("hhInvoiceSystem") in {"einvoice", "pos", "inaccessible"}:
            picks.append("invoice_data")
        if answers.get("hhLocations") == "many":
            picks.append("locations")
    elif scope in {"b1", "b2"}:
        table = COMPANY_CONDITIONAL
        if answers.get("dnDebtGuarantee") == "no":
            picks.append("debt_plan")
        if answers.get("dnTaxDebt") in {"yes", "unreconciled"}:
            picks.append("tax_debt_confirmation")
        if answers.get("dnRecords") in {"lost", "old_accountant"}:
            picks.append("record_recovery")
    return [(code, table[code]) for code in picks]


def prepare_checklist(answers: Answered, assessment_id: UUID) -> list[ChecklistItemView]:
    scope = classify(answers)
    documents = DOCUMENTS_BY_SCOPE.get(scope, []) + conditional_documents(answers, scope)
    return [
        ChecklistItemView(
            id=uuid4(),
            code=code,
            label=label,
            status="needs_verification",
            review_status="draft",
            note=CHECKLIST_NOTE,
        )
        for code, label in documents
    ]


def with_note(item: ChecklistItemView) -> ChecklistItemView:
    return item.model_copy(update={"note": CHECKLIST_NOTE})


def case_status(record: AssessmentSummaryRecord, now: datetime) -> CaseStatus:
    """Đủ giấy tờ để làm việc với chuyên viên, không phải hoàn tất thủ tục pháp lý."""
    if record.expires_at <= now:
        return "expired"
    if (
        record.scope in IN_SCOPE
        and record.available > 0
        and record.missing == 0
        and record.needs_verification == 0
    ):
        return "ready"
    return "in_progress"


def to_list_item(record: AssessmentSummaryRecord, now: datetime) -> AssessmentListItem:
    return AssessmentListItem(
        id=record.id,
        scope=record.scope,
        status=case_status(record, now),
        counts=ChecklistCounts(
            available=record.available,
            missing=record.missing,
            needs_verification=record.needs_verification,
        ),
        created_at=record.created_at,
        updated_at=record.updated_at,
        expires_at=record.expires_at,
        expired=record.expires_at <= now,
    )


def to_view(record: AssessmentRecord) -> AssessmentView:
    order = {code: index for index, (code, _) in enumerate(DOCUMENTS)}
    return AssessmentView(
        id=record.id,
        questionnaire_version=record.content_version,
        content_status="draft",
        answers=record.answers,
        summary=record.summary,
        checklist=sorted(
            (with_note(item) for item in record.checklist),
            key=lambda item: order.get(item.code, len(order)),
        ),
        created_at=record.created_at,
        updated_at=record.updated_at,
        expires_at=record.expires_at,
    )


class AssessmentService:
    def __init__(self, repository: AssessmentRepository) -> None:
        self.repository = repository

    async def create(self, owner_id: UUID, request: CreateAssessment) -> AssessmentView:
        if request.questionnaire_version != VERSION:
            raise ApplicationError(409, "Bộ câu hỏi đã thay đổi. Vui lòng mở lại khảo sát.")
        answers = normalize_answers(request.answers)
        now = datetime.now(UTC)
        record = AssessmentRecord(
            id=uuid4(),
            content_version=VERSION,
            answers=answers,
            summary=build_summary(answers),
            checklist=[],
            created_at=now,
            updated_at=now,
            expires_at=now + timedelta(days=7),
        )
        record.checklist = prepare_checklist(answers, record.id)
        await self.repository.create(owner_id, record)
        return to_view(record)

    async def get(self, owner_id: UUID, assessment_id: UUID) -> AssessmentView:
        record = await self.repository.get(owner_id, assessment_id)
        if record is None:
            raise ApplicationError(404, "Không tìm thấy hồ sơ hoặc hồ sơ đã hết hạn.")
        return to_view(record)

    async def update_item(
        self,
        owner_id: UUID,
        assessment_id: UUID,
        item_id: UUID,
        status: ItemStatus,
    ) -> ChecklistItemView:
        item = await self.repository.update_item(owner_id, assessment_id, item_id, status)
        if item is None:
            raise ApplicationError(404, "Không tìm thấy mục hồ sơ.")
        return with_note(item)

    async def list_page(
        self, owner_id: UUID, page: int, page_size: int, case_filter: CaseFilter = "all"
    ) -> AssessmentPage:
        now = datetime.now(UTC)
        records, total, status_counts = await self.repository.list_page(
            owner_id, (page - 1) * page_size, page_size, case_filter, now
        )
        return AssessmentPage(
            status_counts=status_counts,
            items=[to_list_item(record, now) for record in records],
            page=page,
            page_size=page_size,
            total=total,
        )

    async def purge_expired(self, apply: bool) -> int:
        return await self.repository.purge_expired(datetime.now(UTC), apply)

    async def remove(self, owner_id: UUID, assessment_id: UUID) -> None:
        if not await self.repository.remove(owner_id, assessment_id):
            raise ApplicationError(404, "Không tìm thấy hồ sơ.")
