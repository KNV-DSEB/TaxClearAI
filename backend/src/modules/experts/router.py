from uuid import UUID

from fastapi import APIRouter, Depends, Query

from src.core.schemas import Envelope
from src.modules.auth.dependencies import get_current_user, get_optional_user
from src.modules.auth.domain import UserRecord
from src.modules.experts.dependencies import get_expert_service
from src.modules.experts.schemas import (
    ConsultationResponse,
    CreateConsultationRequest,
    ExpertPage,
    ExpertView,
    RecommendedExpertView,
)
from src.modules.experts.service import ExpertService

router = APIRouter(prefix="/api/v1/experts", tags=["experts"])


@router.get("/", response_model=Envelope[ExpertPage])
async def list_experts(
    q: str | None = Query(default=None, max_length=200),
    specialization: str | None = Query(default=None, max_length=255),
    location: str | None = Query(default=None, max_length=100),
    partner_type: str | None = Query(
        default=None,
        alias="partnerType",
        pattern=r"^(accounting_firm|accountant|tax_consultant)$",
    ),
    page: int = Query(default=1, ge=1, le=1000),
    page_size: int = Query(default=20, ge=1, le=100, alias="pageSize"),
    service: ExpertService = Depends(get_expert_service),
) -> Envelope[ExpertPage]:
    result = await service.list_experts(q, specialization, location, partner_type, page, page_size)
    return Envelope(data=result)


@router.get("/{expert_id}", response_model=Envelope[ExpertView])
async def get_expert(
    expert_id: UUID,
    service: ExpertService = Depends(get_expert_service),
) -> Envelope[ExpertView]:
    return Envelope(data=await service.get_expert(expert_id))


@router.get(
    "/recommendations/{assessment_id}",
    response_model=Envelope[list[RecommendedExpertView]],
)
async def recommend_experts_for_assessment(
    assessment_id: UUID,
    user: UserRecord = Depends(get_current_user),
    service: ExpertService = Depends(get_expert_service),
) -> Envelope[list[RecommendedExpertView]]:
    result = await service.recommend_experts_for_assessment(assessment_id, user.id)
    return Envelope(data=result)


@router.post("/consultations", status_code=201, response_model=Envelope[ConsultationResponse])
async def create_consultation_request(
    data: CreateConsultationRequest,
    user: UserRecord | None = Depends(get_optional_user),
    service: ExpertService = Depends(get_expert_service),
) -> Envelope[ConsultationResponse]:
    user_id = user.id if user else None
    result = await service.create_consultation_request(data, user_id)
    return Envelope(data=result)
