from dataclasses import dataclass
from datetime import date, datetime
from typing import Literal
from uuid import UUID

from src.modules.assessments.schemas import Answers, ChecklistItemView, Summary


@dataclass
class AssessmentRecord:
    id: UUID
    content_version: str
    answers: Answers
    summary: Summary
    checklist: list[ChecklistItemView]
    created_at: datetime
    updated_at: datetime
    expires_at: datetime


@dataclass(frozen=True)
class SourceRecord:
    id: str
    title: str
    url: str
    text: str
    reviewed_at: date
    kind: Literal["product", "legal"]
