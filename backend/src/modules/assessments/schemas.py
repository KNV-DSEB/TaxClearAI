from datetime import UTC, datetime
from typing import Literal, Self
from uuid import UUID

from pydantic import Field, model_validator

from src.core.schemas import ApiModel

TriState = Literal["yes", "no", "unknown"]
ItemStatus = Literal["available", "missing", "needs_verification"]


class Answers(ApiModel):
    business_type: Literal["company", "household", "unknown"]
    goal: Literal["dissolution", "other", "unknown"]
    established_year: int | None = Field(ge=1900, le=datetime.now(UTC).year)
    revenue_status: TriState
    revenue_started_year: int | None = Field(ge=1900, le=datetime.now(UTC).year)
    filing_status: Literal["complete", "incomplete", "never", "unknown"]
    records_status: Literal["complete", "partial", "missing", "unknown"]
    tax_notice_status: TriState
    labor_insurance_status: Literal["none", "obligations", "unknown"]
    assets_inventory_status: TriState
    receivables_payables_status: TriState

    @model_validator(mode="after")
    def validate_years(self) -> Self:
        if self.revenue_started_year is None:
            return self
        if self.revenue_status == "no":
            raise ValueError("Năm phát sinh không phù hợp câu trả lời.")
        if self.established_year and self.revenue_started_year < self.established_year:
            raise ValueError("Năm phát sinh không được trước năm thành lập.")
        return self


class Option(ApiModel):
    value: str
    label: str


class Question(ApiModel):
    id: str
    label: str
    kind: Literal["year", "choice"] = "choice"
    required: bool = True
    options: list[Option] = Field(default_factory=list)


class Questionnaire(ApiModel):
    id: str = "b2"
    version: str
    content_status: Literal["draft", "approved"] = "draft"
    questions: list[Question]


class Summary(ApiModel):
    scope: Literal["b2", "out_of_scope", "needs_confirmation"]
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
    answers: Answers
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


class AssessmentListItem(ApiModel):
    id: UUID
    scope: Literal["b2", "out_of_scope", "needs_confirmation"]
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
