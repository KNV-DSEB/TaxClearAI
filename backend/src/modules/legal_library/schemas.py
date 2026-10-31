from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class LegalProcedure(StrEnum):
    COMPANY_DISSOLUTION = "company_dissolution"
    TAX_ID_TERMINATION = "tax_id_termination"
    HKD_TERMINATION = "hkd_termination"
    HKD_NEW_REGISTRATION = "hkd_new_registration"


class LegalLookupRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    procedure: LegalProcedure | None = None
    query: str | None = Field(default=None, min_length=2, max_length=160)

    @model_validator(mode="after")
    def require_lookup_target(self) -> "LegalLookupRequest":
        if self.procedure is None and self.query is None:
            raise ValueError("procedure or query is required")
        return self


class ApplicableProvision(BaseModel):
    article: str
    clause: str
    point: str | None = None
    regulated_action: str


class LegalReference(BaseModel):
    document_name: str
    document_number: str
    issuing_authority: str
    issued_date: date
    effective_date: date
    effectiveness_status: str
    applicable_provisions: list[ApplicableProvision]
    summary: str
    source_url: str = ""
    has_verbatim_text: bool = False
    last_synced: datetime | None = None
    change_note: str | None = None


class LegalLookupResponse(BaseModel):
    results: list[LegalReference]
