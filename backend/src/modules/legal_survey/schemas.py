from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from src.core.ai_disclosure import AI_DISCLOSURE


class EntityType(StrEnum):
    HKD = "HKD"
    DN = "DN"


class RegistrationStatus(StrEnum):
    REGISTERED = "registered"
    NOT_REGISTERED = "not_registered"
    UNKNOWN = "unknown"


class TaxIdStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    UNKNOWN = "unknown"


class OperatingStatus(StrEnum):
    CURRENTLY_ACTIVE = "currently_active"
    NEVER_HAD_REVENUE = "never_had_revenue"
    ABANDONED_AFTER_OPERATION = "abandoned_after_operation"
    UNKNOWN = "unknown"


class DeclarationStatus(StrEnum):
    FILED_ALL = "filed_all"
    FILED_SOME = "filed_some"
    NOT_FILED = "not_filed"
    UNKNOWN = "unknown"


class YesNoUnknown(StrEnum):
    YES = "yes"
    NO = "no"
    UNKNOWN = "unknown"


class BusinessStartPeriod(StrEnum):
    BEFORE_2012 = "before_2012"
    FROM_2012_TO_2019 = "2012_2019"
    FROM_2020_TO_2024 = "2020_2024"
    FROM_2025_ONWARD = "2025_onward"
    UNKNOWN = "unknown"


class IdleDuration(StrEnum):
    UNDER_1Y = "under_1y"
    FROM_1_TO_3Y = "1_to_3y"
    OVER_3Y = "over_3y"
    UNKNOWN = "unknown"


class InvoiceStatus(StrEnum):
    NONE = "none"
    RESOLVED = "resolved"
    UNRESOLVED = "unresolved"
    UNKNOWN = "unknown"


class BankStatus(StrEnum):
    MATCHES = "matches"
    MISMATCH = "mismatch"
    NOT_REVIEWED = "not_reviewed"


class Obligation(StrEnum):
    NONE = "none"
    UNKNOWN = "unknown"
    UNPAID_TAX = "unpaid_tax"
    UNRESOLVED_INVOICES = "unresolved_invoices"
    UNPAID_LABOUR = "unpaid_labour"
    UNPAID_SOCIAL_SECURITY = "unpaid_social_security"
    OTHER = "other"


class TargetAction(StrEnum):
    TERMINATE = "terminate"
    SUSPEND = "suspend"
    CONVERT_TO_NEW_ENTITY = "convert_to_new_entity"


class SurveyAnswers(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    entity_type: EntityType
    registration_status: RegistrationStatus
    tax_id_status: TaxIdStatus
    operating_status: OperatingStatus
    declaration_status: DeclarationStatus
    declaration_matches_reality: YesNoUnknown
    invoice_status: InvoiceStatus
    bank_status: BankStatus
    unpaid_obligations: list[Obligation] | None = Field(
        description=(
            "Null means unknown; an empty list means the user confirmed there are "
            "no unpaid obligations."
        )
    )
    tax_audit_notice: YesNoUnknown
    target_action: TargetAction
    business_start_period: BusinessStartPeriod = BusinessStartPeriod.UNKNOWN
    idle_duration: IdleDuration = IdleDuration.UNKNOWN
    has_assets_or_inventory: YesNoUnknown = YesNoUnknown.UNKNOWN
    has_employees: YesNoUnknown = YesNoUnknown.UNKNOWN
    free_text: str | None = Field(default=None, max_length=1000)

    @model_validator(mode="after")
    def obligations_are_unique(self) -> "SurveyAnswers":
        if self.unpaid_obligations is not None and len(set(self.unpaid_obligations)) != len(
            self.unpaid_obligations
        ):
            raise ValueError("unpaid_obligations must not contain duplicates")
        if (
            self.unpaid_obligations
            and Obligation.NONE in self.unpaid_obligations
            and len(self.unpaid_obligations) > 1
        ):
            raise ValueError("none cannot be combined with another obligation")
        if (
            self.unpaid_obligations
            and Obligation.UNKNOWN in self.unpaid_obligations
            and len(self.unpaid_obligations) > 1
        ):
            raise ValueError("unknown cannot be combined with another obligation")
        return self


class RiskFlag(StrEnum):
    HAS_TAX_AUDIT_NOTICE = "has_tax_audit_notice"
    BANK_ACCOUNT_MISMATCH = "bank_account_mismatch"
    UNRESOLVED_INVOICES = "unresolved_invoices"
    UNPAID_SOCIAL_SECURITY = "unpaid_social_security"
    LONG_INACTIVE = "long_inactive"
    PRE_2012_ENTITY = "pre_2012_entity"
    ASSETS_WITHOUT_REVENUE = "assets_without_revenue"


class Segment(StrEnum):
    A1 = "A1"
    A2 = "A2"
    A3 = "A3"
    B1 = "B1"
    B2 = "B2"


class SurveyAIStatus(StrEnum):
    OK = "ok"
    UNAVAILABLE = "unavailable"
    REJECTED = "rejected"
    DISABLED = "disabled"


class SurveyAIAgreement(StrEnum):
    AGREE = "agree"
    DISAGREE = "disagree"
    AI_NOT_USED = "ai_not_used"


class SituationSuggestion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    suggested_segment: Segment
    confidence: float = Field(ge=0.0, le=1.0)
    reasons: list[str] = Field(max_length=5)
    risk_signals: list[RiskFlag] = Field(default_factory=list)
    missing_info: list[str] = Field(default_factory=list, max_length=15)

    @field_validator("reasons")
    @classmethod
    def validate_reason_lengths(cls, values: list[str]) -> list[str]:
        if any(not value.strip() or len(value) > 200 for value in values):
            raise ValueError("reasons must be non-empty and at most 200 characters")
        return values

    @field_validator("missing_info")
    @classmethod
    def validate_missing_info_lengths(cls, values: list[str]) -> list[str]:
        if any(not value.strip() or len(value) > 80 for value in values):
            raise ValueError("missing_info must contain question ids")
        return values


class SummaryProfile(BaseModel):
    entity_type: EntityType
    has_registration: bool
    has_declaration: bool
    has_discrepancy: bool
    has_debt: bool
    target_action: TargetAction


class ClassificationResponse(BaseModel):
    determined_segment: Segment
    confidence_score: float = Field(ge=0.0, le=1.0)
    risk_flags: list[RiskFlag]
    summary_profile: SummaryProfile
    rules_segment: Segment
    ai_suggestion: SituationSuggestion | None = None
    ai_status: SurveyAIStatus = SurveyAIStatus.DISABLED
    agreement: SurveyAIAgreement = SurveyAIAgreement.AI_NOT_USED
    needs_user_confirmation: bool = False
    candidates: list[Segment] = Field(default_factory=list)
    needs_expert: bool = False
    ai_disclosure: str = AI_DISCLOSURE

    @model_validator(mode="before")
    @classmethod
    def fill_legacy_response_fields(cls, value: object) -> object:
        if not isinstance(value, dict):
            return value
        data = dict(value)
        data.setdefault("rules_segment", data.get("determined_segment"))
        data.setdefault(
            "candidates",
            [data["determined_segment"]] if data.get("determined_segment") else [],
        )
        return data


class ChatContextResponse(BaseModel):
    context_flags: dict[str, bool]


class SurveyOption(BaseModel):
    value: str
    label: str


class SurveyQuestion(BaseModel):
    id: str
    prompt: str
    selection_type: str
    options: list[SurveyOption]
    show_if: dict[str, list[str]] | None = None
