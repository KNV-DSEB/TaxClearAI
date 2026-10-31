from fastapi import APIRouter, Depends, Query

from src.core.rate_limit import enforce_api_rate_limit
from src.modules.case_brief.schemas import CaseBriefRequest, CaseSegment
from src.modules.expert_directory.repository import ExpertDirectoryRepository
from src.modules.expert_directory.schemas import (
    ExpertProfile,
    ExpertRequestResponse,
    ExpertType,
)
from src.modules.expert_directory.service import ExpertDirectoryService

router = APIRouter(prefix="/experts", tags=["expert directory"])


def get_expert_directory_service() -> ExpertDirectoryService:
    return ExpertDirectoryService(ExpertDirectoryRepository())


@router.get("", response_model=list[ExpertProfile])
async def list_experts(
    segment: CaseSegment | None = Query(default=None),
    region: str | None = Query(default=None, min_length=1, max_length=120),
    expert_type: ExpertType | None = Query(default=None),
    service: ExpertDirectoryService = Depends(get_expert_directory_service),
) -> list[ExpertProfile]:
    return service.list_verified(segment, region, expert_type)


@router.get("/{expert_id}", response_model=ExpertProfile)
async def get_expert(
    expert_id: str,
    service: ExpertDirectoryService = Depends(get_expert_directory_service),
) -> ExpertProfile:
    return service.get_verified(expert_id)


@router.post(
    "/{expert_id}/requests",
    response_model=ExpertRequestResponse,
    dependencies=[Depends(enforce_api_rate_limit)],
)
async def prepare_expert_request(
    expert_id: str,
    case_brief: CaseBriefRequest,
    service: ExpertDirectoryService = Depends(get_expert_directory_service),
) -> ExpertRequestResponse:
    return service.prepare_request(expert_id, case_brief)
