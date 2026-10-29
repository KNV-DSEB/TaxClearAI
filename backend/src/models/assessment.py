from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import BaseModel


class Assessment(BaseModel):
    __tablename__ = "assessments"
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    answers: Mapped[dict[str, Any]] = mapped_column(JSONB)
    content_version: Mapped[str] = mapped_column(String(80))
    summary_snapshot: Mapped[dict[str, Any]] = mapped_column(JSONB)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)


class ChecklistItem(BaseModel):
    __tablename__ = "checklist_items"
    __table_args__ = (
        UniqueConstraint("assessment_id", "item_code"),
        CheckConstraint(
            "status IN ('available','missing','needs_verification')",
            name="checklist_items_status_check",
        ),
        CheckConstraint(
            "review_status IN ('draft','approved')", name="checklist_items_review_status_check"
        ),
    )
    assessment_id: Mapped[UUID] = mapped_column(
        ForeignKey("assessments.id", ondelete="CASCADE"), index=True
    )
    item_code: Mapped[str] = mapped_column(String(80))
    label_snapshot: Mapped[str] = mapped_column(String(300))
    review_status: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(30))
