from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Literal
from uuid import UUID

from src.modules.assessments.schemas import ChecklistItemView, Scope, Summary


@dataclass
class AssessmentRecord:
    id: UUID
    content_version: str
    answers: dict[str, Any]
    summary: Summary
    checklist: list[ChecklistItemView]
    created_at: datetime
    updated_at: datetime
    expires_at: datetime


@dataclass(frozen=True)
class AssessmentSummaryRecord:
    id: UUID
    scope: Scope
    available: int
    missing: int
    needs_verification: int
    created_at: datetime
    updated_at: datetime
    expires_at: datetime


@dataclass(frozen=True)
class SourceRecord:
    id: str
    title: str
    url: str
    text: str
    reviewed_at: date | None
    kind: Literal["product", "legal"]
    fetched_at: datetime | None = None
    review_status: Literal["reviewed", "unreviewed"] = "reviewed"
