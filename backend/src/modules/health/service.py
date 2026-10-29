from src.modules.health.repository import HealthRepository
from src.modules.health.schemas import HealthResponse


class HealthService:
    def __init__(self, health_repository: HealthRepository) -> None:
        self._health_repository = health_repository

    async def check(self) -> HealthResponse:
        snapshot = self._health_repository.get_snapshot()
        return HealthResponse(**snapshot)
