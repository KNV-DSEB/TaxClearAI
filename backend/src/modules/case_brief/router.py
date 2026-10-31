from fastapi import APIRouter, Depends

from src.core.rate_limit import enforce_api_rate_limit
from src.modules.case_brief.repository import CaseBriefRepository
from src.modules.case_brief.schemas import CaseBriefRequest, CaseBriefResponse
from src.modules.case_brief.service import CaseBriefService

router = APIRouter(prefix="/case-brief", tags=["case brief"])


def get_case_brief_service() -> CaseBriefService:
    return CaseBriefService(CaseBriefRepository())


@router.post(
    "/generate",
    response_model=CaseBriefResponse,
    dependencies=[Depends(enforce_api_rate_limit)],
)
async def generate_case_brief(
    request: CaseBriefRequest,
    service: CaseBriefService = Depends(get_case_brief_service),
) -> CaseBriefResponse:
    return service.generate(request)
