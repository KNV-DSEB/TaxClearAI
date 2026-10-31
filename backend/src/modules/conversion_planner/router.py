from fastapi import APIRouter, Depends

from src.core.rate_limit import enforce_api_rate_limit
from src.modules.conversion_planner.repository import ConversionPlannerRepository
from src.modules.conversion_planner.schemas import ConversionPlanRequest, ConversionPlanResponse
from src.modules.conversion_planner.service import ConversionPlannerService

router = APIRouter(prefix="/conversion-plans", tags=["conversion planner"])


def get_conversion_planner_service() -> ConversionPlannerService:
    return ConversionPlannerService(ConversionPlannerRepository())


@router.post(
    "/parallel",
    response_model=ConversionPlanResponse,
    dependencies=[Depends(enforce_api_rate_limit)],
)
async def create_parallel_plan(
    request: ConversionPlanRequest,
    service: ConversionPlannerService = Depends(get_conversion_planner_service),
) -> ConversionPlanResponse:
    return service.plan(request)
