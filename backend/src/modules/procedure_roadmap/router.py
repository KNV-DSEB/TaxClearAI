from fastapi import APIRouter, Depends

from src.core.rate_limit import enforce_api_rate_limit
from src.modules.procedure_roadmap.repository import ProcedureRoadmapRepository
from src.modules.procedure_roadmap.schemas import RoadmapRequest, RoadmapResponse
from src.modules.procedure_roadmap.service import ProcedureRoadmapService

router = APIRouter(prefix="/procedures", tags=["procedure roadmaps"])


def get_procedure_roadmap_service() -> ProcedureRoadmapService:
    return ProcedureRoadmapService(ProcedureRoadmapRepository())


@router.post(
    "/roadmap",
    response_model=RoadmapResponse,
    dependencies=[Depends(enforce_api_rate_limit)],
)
async def create_roadmap(
    request: RoadmapRequest,
    service: ProcedureRoadmapService = Depends(get_procedure_roadmap_service),
) -> RoadmapResponse:
    return service.create_roadmap(request)
