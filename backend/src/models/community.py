from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import BaseModel


class CommunityTopic(BaseModel):
    __tablename__ = "community_topics"

    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class CommunityQuestion(BaseModel):
    __tablename__ = "community_questions"

    topic_id: Mapped[UUID] = mapped_column(ForeignKey("community_topics.id"), index=True)
    author_name: Mapped[str] = mapped_column(String(120))
    author_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(200))
    question_content: Mapped[str] = mapped_column(Text)
    answer_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    answered_by: Mapped[str | None] = mapped_column(String(120), nullable=True)
    answered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
