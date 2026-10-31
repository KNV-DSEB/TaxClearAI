from fastapi import APIRouter, Depends

from src.core.rate_limit import enforce_api_rate_limit
from src.modules.document_checklist.repository import DocumentChecklistRepository
from src.modules.document_checklist.schemas import ChecklistRequest, ChecklistResponse
from src.modules.document_checklist.service import DocumentChecklistService

router = APIRouter(prefix="/documents", tags=["document checklist"])


def get_document_checklist_service() -> DocumentChecklistService:
    return DocumentChecklistService(DocumentChecklistRepository())


@router.post(
    "/checklist",
    response_model=ChecklistResponse,
    dependencies=[Depends(enforce_api_rate_limit)],
)
async def review_checklist(
    request: ChecklistRequest,
    service: DocumentChecklistService = Depends(get_document_checklist_service),
) -> ChecklistResponse:
    return service.review(request)
