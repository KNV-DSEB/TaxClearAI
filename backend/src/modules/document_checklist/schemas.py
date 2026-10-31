from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Segment(StrEnum):
    A1 = "A1"
    A2 = "A2"
    A3 = "A3"
    B1 = "B1"
    B2 = "B2"


class Procedure(StrEnum):
    TERMINATE = "terminate"
    SUSPEND = "suspend"
    CONVERT_TO_NEW_ENTITY = "convert_to_new_entity"


class DeclaredDocumentState(StrEnum):
    AVAILABLE = "available"
    MISSING = "missing"
    NEEDS_VERIFICATION = "needs_verification"


class ChecklistStatus(StrEnum):
    ALREADY_HAVE = "already_have"
    MISSING = "missing"
    NEEDS_VERIFICATION = "needs_verification"


class DocumentDeclaration(BaseModel):
    model_config = ConfigDict(extra="forbid")

    doc_id: str = Field(min_length=1, max_length=40)
    declared_state: DeclaredDocumentState


class ChecklistRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    segment: Segment
    procedure: Procedure
    documents: list[DocumentDeclaration] = Field(default_factory=list, max_length=100)

    @model_validator(mode="after")
    def document_ids_are_unique(self) -> "ChecklistRequest":
        ids = [item.doc_id for item in self.documents]
        if len(ids) != len(set(ids)):
            raise ValueError("documents must not contain duplicate doc_id values")
        return self


class ChecklistItem(BaseModel):
    doc_id: str
    doc_name: str
    status: ChecklistStatus
    template_download_available: bool
    action_guide: str


class ChecklistResponse(BaseModel):
    total_items: int
    readiness_percentage: int = Field(ge=0, le=100)
    checklist: list[ChecklistItem]
