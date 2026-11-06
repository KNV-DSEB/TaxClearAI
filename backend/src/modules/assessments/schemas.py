import re
from datetime import UTC, datetime
from typing import Annotated, Any, Literal
from uuid import UUID

from pydantic import ConfigDict, Field, field_validator

from src.core.schemas import ApiModel

ItemStatus = Literal["available", "missing", "needs_verification"]
Scope = Literal["a1", "a2", "a3", "b1", "b2", "household", "out_of_scope", "needs_confirmation"]


# Ô tự điền không nhận thông tin nhận diện (email, dãy số dài như mã số thuế, số điện thoại)
IDENTIFIER = re.compile(r"[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}|(?:\d[\s.-]*){7,}")
CURRENT_YEAR = datetime.now(UTC).year
Money = Annotated[int, Field(ge=0, le=10**13)]


class Answers(ApiModel):
    """Bộ câu trả lời chuẩn hóa (groups-draft-3). Câu không áp dụng để None."""

    model_config = ConfigDict(str_strip_whitespace=True)

    business_type: Literal["company", "household"]
    procedure: Literal["dissolution", "suspension", "conversion"]
    operating_status: Literal["active", "stopped_not_started", "stopped_preparing", "forced"]
    sector: Literal["trade", "hospitality", "manufacturing", "services", "other"]
    sector_other: str | None = Field(default=None, max_length=80)
    established_year: int | None = Field(default=None, ge=1900, le=CURRENT_YEAR)
    has_revenue: Literal["yes", "no"]
    last_revenue: str | None = Field(default=None, max_length=80)
    has_costs: Literal["yes", "no"]
    records_access: Literal["complete", "partial", "none", "unknown_location"]
    # Hộ kinh doanh
    hh_province: str | None = Field(default=None, max_length=80)
    hh_locations: Literal["one", "many", "none"] | None = None
    hh_conditional: Literal["yes", "no"] | None = None
    hh_tax_obligation: Literal["yes", "no"] | None = None
    hh_invoice_system: Literal["einvoice", "pos", "inaccessible", "none"] | None = None
    hh_employees: Literal["unresolved", "resolved", "none"] | None = None
    hh_revenue_estimate: Money | None = None
    # Doanh nghiệp
    dn_type: Literal["sole", "llc1", "llc2", "jsc", "partnership"] | None = None
    dn_registry: str | None = Field(default=None, max_length=80)
    dn_approver: str | None = Field(default=None, max_length=120)
    dn_decision: Literal["adopted", "none", "drafting", "unknown"] | None = None
    dn_debt_guarantee: Literal["yes", "no"] | None = None
    dn_revenue: Literal["yes", "no"] | None = None
    dn_revenue_amount: Money | None = None
    dn_expenses: Literal["yes", "no"] | None = None
    dn_expense_note: str | None = Field(default=None, max_length=120)
    dn_records: Literal["complete", "partial", "lost", "old_accountant", "unclear"] | None = None
    dn_tax_debt: Literal["yes", "no", "unreconciled"] | None = None

    @field_validator(
        "sector_other",
        "last_revenue",
        "hh_province",
        "dn_registry",
        "dn_approver",
        "dn_expense_note",
    )
    @classmethod
    def reject_identifiers(cls, value: str | None) -> str | None:
        if not value:
            return None
        if IDENTIFIER.search(value):
            raise ValueError(
                "Vui lòng không nhập thông tin nhận diện như email, số điện thoại hay mã số thuế."
            )
        return value


class Option(ApiModel):
    value: str
    label: str


class Question(ApiModel):
    id: str
    label: str
    kind: Literal["year", "choice", "text", "number"] = "choice"
    required: bool = True
    help: str | None = None
    unit: str | None = None
    options: list[Option] = Field(default_factory=list)
    # Chỉ hỏi khi mọi câu trả lời trước đó nằm trong danh sách cho phép; None = luôn hỏi
    show_if: dict[str, list[str]] | None = None


class Questionnaire(ApiModel):
    id: str = "b2"
    version: str
    content_status: Literal["draft", "approved"] = "draft"
    questions: list[Question]


class Summary(ApiModel):
    scope: Scope
    known_facts: list[str]
    unknown_facts: list[str]
    review_reasons: list[str]
    notice: str


class ChecklistItemView(ApiModel):
    id: UUID
    code: str
    label: str
    status: ItemStatus
    review_status: Literal["draft", "approved"]
    note: str | None = None


class AssessmentView(ApiModel):
    id: UUID
    questionnaire_version: str
    content_status: Literal["draft", "approved"]
    answers: dict[str, Any]
    summary: Summary
    checklist: list[ChecklistItemView]
    created_at: datetime
    updated_at: datetime
    expires_at: datetime


class CreateAssessment(ApiModel):
    questionnaire_version: str = Field(max_length=80)
    answers: Answers


class UpdateChecklistItem(ApiModel):
    status: ItemStatus


class ChecklistCounts(ApiModel):
    available: int
    missing: int
    needs_verification: int


CaseStatus = Literal["in_progress", "ready", "expired"]
CaseFilter = Literal["all", "in_progress", "ready"]


class StatusCounts(ApiModel):
    all: int
    in_progress: int
    ready: int


class AssessmentListItem(ApiModel):
    id: UUID
    scope: Scope
    status: CaseStatus
    counts: ChecklistCounts
    created_at: datetime
    updated_at: datetime
    expires_at: datetime
    expired: bool


class AssessmentPage(ApiModel):
    items: list[AssessmentListItem]
    page: int
    page_size: int
    total: int
    status_counts: StatusCounts
