from typing import Literal

from pydantic import Field

from src.core.schemas import ApiModel

LegalCategory = Literal[
    "household",
    "company_dissolution",
    "tax_closure",
    "guidance",
]


class LegalSource(ApiModel):
    label: str
    url: str
    source_type: Literal["official", "reference"]


class LegalStep(ApiModel):
    title: str
    description: str
    authority: str | None = None
    timing: str | None = None


class LegalDocument(ApiModel):
    slug: str
    categories: list[LegalCategory]
    document_type: str
    document_number: str
    document_title: str
    authority: str
    summary: str
    applies_to: list[str]
    overview: str
    legal_basis: list[str] = Field(default_factory=list)
    process_steps: list[LegalStep] = Field(default_factory=list)
    checklist: list[str] = Field(default_factory=list)
    timeline: str
    notes: list[str] = Field(default_factory=list)
    sources: list[LegalSource]


class LegalDocumentList(ApiModel):
    items: list[LegalDocument]
    total: int
