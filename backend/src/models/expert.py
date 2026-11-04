from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, true
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import BaseModel


class Expert(BaseModel):
    __tablename__ = "experts"

    full_name: Mapped[str] = mapped_column(String(150))
    title: Mapped[str] = mapped_column(String(150))
    organization: Mapped[str] = mapped_column(String(200))
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    bio: Mapped[str] = mapped_column(Text)
    specializations: Mapped[str] = mapped_column(String(255))
    partner_type: Mapped[str] = mapped_column(
        String(50), default="tax_consultant", server_default="tax_consultant", index=True
    )
    services_offered: Mapped[str] = mapped_column(String(500), default="", server_default="")
    location: Mapped[str] = mapped_column(String(100))
    experience_years: Mapped[int] = mapped_column(Integer)
    consultation_fee_text: Mapped[str] = mapped_column(String(150))
    is_verified: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default=true(), index=True
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default=true(), index=True
    )


class ConsultationRequest(BaseModel):
    __tablename__ = "consultation_requests"

    expert_id: Mapped[UUID] = mapped_column(
        ForeignKey("experts.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    assessment_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("assessments.id", ondelete="SET NULL"), nullable=True
    )
    contact_name: Mapped[str] = mapped_column(String(150))
    contact_phone: Mapped[str] = mapped_column(String(50))
    contact_email: Mapped[str | None] = mapped_column(String(150), nullable=True)
    business_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    service_needed: Mapped[str | None] = mapped_column(String(100), nullable=True)
    share_data_consent: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default=true()
    )
    data_snapshot: Mapped[str | None] = mapped_column(Text, nullable=True)
    consultation_method: Mapped[str] = mapped_column(
        String(50), default="online", server_default="online"
    )
    notes: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), default="pending", server_default="pending")
