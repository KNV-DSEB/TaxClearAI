from datetime import UTC, date, datetime, timedelta
from typing import Literal
from uuid import UUID, uuid4

from src.core.errors import ApplicationError
from src.modules.assessments.content import (
    CHECKLIST_NOTE,
    DOCUMENTS,
    NOTICE,
    VERSION,
    get_questionnaire,
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
    Questionnaire,
    Summary,
)


def read_questionnaire() -> Questionnaire:
    return get_questionnaire()


def get_approved_chat_sources() -> list[SourceRecord]:
    return [
        SourceRecord(
            id="product-guide",
            title="Hướng dẫn sử dụng Tax Clear AI",
            url="/huong-dan",
            text=(
                "Bản thử dành cho doanh nghiệp từng hoạt động muốn chuẩn bị khảo sát giải thể. "
                "Đăng nhập bằng tài khoản được cấp. Trả lời 11 câu; có thể chọn chưa biết hoặc "
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


def build_summary(data: Answers) -> Summary:
    scope: Literal["b2", "out_of_scope", "needs_confirmation"] = "b2"
    if data.business_type == "household" or data.goal == "other" or data.revenue_status == "no":
        scope = "out_of_scope"
    elif "unknown" in (data.business_type, data.goal, data.revenue_status):
        scope = "needs_confirmation"
    questions = {question.id: question for question in get_questionnaire().questions}
    known, unknown = [], []
    for key, value in data.model_dump(by_alias=True).items():
        question = questions[key]
        if value is None or value == "unknown":
            unknown.append(question.label)
        else:
            label = next(
                (option.label for option in question.options if option.value == value), value
            )
            known.append(f"{question.label} — {label}")
    reasons = []
    if data.filing_status != "complete":
        reasons.append("Tình trạng kê khai cần được chuyên viên xác minh.")
    if data.tax_notice_status != "no":
        reasons.append("Cần xác minh thông báo hoặc nghĩa vụ thuế với chuyên viên.")
    return Summary(
        scope=scope, known_facts=known, unknown_facts=unknown, review_reasons=reasons, notice=NOTICE
    )


def prepare_checklist(data: Answers, assessment_id: UUID) -> list[ChecklistItemView]:
    if build_summary(data).scope != "b2":
        return []
    return [
        ChecklistItemView(
            id=uuid4(),
            code=code,
            label=label,
            status="needs_verification",
            review_status="draft",
            note=CHECKLIST_NOTE,
        )
        for code, label in DOCUMENTS
    ]


def with_note(item: ChecklistItemView) -> ChecklistItemView:
    return item.model_copy(update={"note": CHECKLIST_NOTE})


def case_status(record: AssessmentSummaryRecord, now: datetime) -> CaseStatus:
    """Đủ giấy tờ để làm việc với chuyên viên, không phải hoàn tất thủ tục pháp lý."""
    if record.expires_at <= now:
        return "expired"
    if (
        record.scope == "b2"
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
        now = datetime.now(UTC)
        record = AssessmentRecord(
            id=uuid4(),
            content_version=VERSION,
            answers=request.answers,
            summary=build_summary(request.answers),
            checklist=[],
            created_at=now,
            updated_at=now,
            expires_at=now + timedelta(days=7),
        )
        record.checklist = prepare_checklist(request.answers, record.id)
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
