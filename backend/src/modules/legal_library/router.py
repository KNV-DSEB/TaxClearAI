from fastapi import APIRouter, Depends

from src.core.rate_limit import enforce_api_rate_limit
from src.modules.legal_library.repository import LegalLibraryRepository
from src.modules.legal_library.schemas import LegalLookupRequest, LegalLookupResponse
from src.modules.legal_library.service import LegalLibraryService

router = APIRouter(prefix="/legal-library", tags=["legal library"])


def get_legal_library_service() -> LegalLibraryService:
    return LegalLibraryService(LegalLibraryRepository())


@router.post(
    "/search",
    response_model=LegalLookupResponse,
    dependencies=[Depends(enforce_api_rate_limit)],
)
async def search_legal_references(
    request: LegalLookupRequest,
    service: LegalLibraryService = Depends(get_legal_library_service),
) -> LegalLookupResponse:
    return service.search(request)
