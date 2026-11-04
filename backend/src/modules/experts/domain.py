from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class ExpertRecord:
    id: UUID
    full_name: str
    title: str
    organization: str
    avatar_url: str | None
    bio: str
    specializations: str
    location: str
    experience_years: int
    consultation_fee_text: str
    is_verified: bool
    partner_type: str = "tax_consultant"
    services_offered: str = ""


@dataclass(frozen=True)
class ConsultationRecord:
    id: UUID
    expert_id: UUID
    status: str
    created_at: datetime


@dataclass(frozen=True)
class ExpertSeed:
    id: UUID
    full_name: str
    title: str
    organization: str
    bio: str
    specializations: str
    location: str
    experience_years: int
    consultation_fee_text: str
    partner_type: str = "tax_consultant"
    services_offered: str = ""
