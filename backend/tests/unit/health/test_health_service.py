import pytest

from src.modules.health.repository import HealthRepository
from src.modules.health.service import HealthService


@pytest.mark.asyncio
async def test_check_returns_status_ok() -> None:
    service = HealthService(HealthRepository())
    result = await service.check()
    assert result.status == "ok"


@pytest.mark.asyncio
async def test_check_returns_non_negative_uptime() -> None:
    service = HealthService(HealthRepository())
    result = await service.check()
    assert result.uptime_seconds >= 0
