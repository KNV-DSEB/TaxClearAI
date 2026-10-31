from fastapi import APIRouter, Depends

from src.core.rate_limit import enforce_api_rate_limit
from src.modules.process_tracker.repository import ProcessTrackerRepository
from src.modules.process_tracker.schemas import ProcessTrackerRequest, ProcessTrackerResponse
from src.modules.process_tracker.service import ProcessTrackerService

router = APIRouter(prefix="/process-tracker", tags=["process tracker"])


def get_process_tracker_service() -> ProcessTrackerService:
    return ProcessTrackerService(ProcessTrackerRepository())


@router.post(
    "/track",
    response_model=ProcessTrackerResponse,
    dependencies=[Depends(enforce_api_rate_limit)],
)
async def track_process(
    request: ProcessTrackerRequest,
    service: ProcessTrackerService = Depends(get_process_tracker_service),
) -> ProcessTrackerResponse:
    return service.track(request)
