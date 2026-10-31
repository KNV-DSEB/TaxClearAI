from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class CaseSegment(StrEnum):
    A1 = "A1"
    A2 = "A2"
    A3 = "A3"
    B1 = "B1"
    B2 = "B2"


class CaseDiagnosis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    segment: CaseSegment
    entity_type: str = Field(min_length=1, max_length=80)
    procedure: str = Field(min_length=1, max_length=200)
    target_action: str = Field(min_length=1, max_length=120)
    risk_flags: list[str] = Field(default_factory=list, max_length=30)
    blockers: list[str] = Field(default_factory=list, max_length=30)
    notes: list[str] = Field(default_factory=list, max_length=30)


class CaseBriefRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    diagnosis: CaseDiagnosis
    user_questions: list[str] = Field(default_factory=list, max_length=20)


class ServiceFee(BaseModel):
    minimum: int | None
    maximum: int | None
    note: str


class EstimatedCost(BaseModel):
    currency: str = "VND"
    minimum: int | None
    maximum: int | None
    reference_basis: str
    complexity_note: str
    sources: list[str]
    service_fee: ServiceFee
    state_payments_note: str
    quote_requires_survey: bool = False


class CaseBriefResponse(BaseModel):
    case_classification: str
    target_group: str
    main_blockers: list[str]
    scope_of_work: dict[str, list[str]]
    expert_interview_questions: list[str]
    estimated_cost: EstimatedCost
    privacy_note: str
