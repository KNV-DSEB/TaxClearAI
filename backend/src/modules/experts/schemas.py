from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import Field, field_validator

from src.core.schemas import ApiModel


class ExpertView(ApiModel):
    id: UUID
    full_name: str
    title: str
    organization: str
    avatar_url: str | None
    bio: str
    specializations: list[str]
    partner_type: Literal["accounting_firm", "accountant", "tax_consultant"]
    services_offered: list[str]
    location: str
    experience_years: int
    consultation_fee_text: str
    is_verified: bool


class RecommendedExpertView(ApiModel):
    expert: ExpertView
    match_reason: str


class ExpertPage(ApiModel):
    items: list[ExpertView]
    page: int
    page_size: int
    total: int


class CreateConsultationRequest(ApiModel):
    expert_id: UUID
    assessment_id: UUID | None = None
    contact_name: str = Field(min_length=1, max_length=150)
    contact_phone: str = Field(min_length=8, max_length=50, pattern=r"^[0-9+().\s-]+$")
    contact_email: str | None = Field(
        default=None,
        max_length=150,
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
    )
    business_type: str | None = Field(default=None, max_length=100)
    service_needed: Literal[
        "Dọn dẹp và hoàn thiện sổ sách kế toán",
        "Lập báo cáo tài chính và quyết toán thuế giải thể",
        "Đóng mã số thuế và giải thể trọn gói",
        "Kiểm tra và giải trình chênh lệch số liệu thuế",
        "Khác",
    ] | None = None
    share_data_consent: bool = True
    consultation_method: Literal["online", "phone", "in_person"] = "online"
    notes: str = Field(min_length=1, max_length=5000)

    @field_validator("contact_phone")
    @classmethod
    def validate_contact_phone(cls, value: str) -> str:
        if sum(character.isdigit() for character in value) < 8:
            raise ValueError("Số điện thoại cần có ít nhất 8 chữ số.")
        return value


class ConsultationResponse(ApiModel):
    id: UUID
    expert_id: UUID
    status: str
    created_at: datetime
