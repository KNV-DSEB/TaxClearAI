from fastapi import APIRouter, Depends

from src.modules.health.repository import HealthRepository
from src.modules.health.schemas import HealthResponse
from src.modules.health.service import HealthService

router = APIRouter(prefix="/health", tags=["health"])


def get_health_service() -> HealthService:
    return HealthService(HealthRepository())


# Router ONLY: receive request, delegate to service, return response — see
# AGENTS.md "Architecture Rules". No business logic, no repository calls here.
@router.get("", response_model=HealthResponse)
async def check_health(
    service: HealthService = Depends(get_health_service),
) -> HealthResponse:
    return await service.check()
