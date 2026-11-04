from typing import Annotated

from fastapi import APIRouter, Depends, Query

from src.core.schemas import Envelope
from src.modules.legal.dependencies import get_legal_service
from src.modules.legal.schemas import LegalCategory, LegalDocument, LegalDocumentList
from src.modules.legal.service import LegalService

router = APIRouter(prefix="/api/v1/legal", tags=["legal library"])


@router.get("/", response_model=Envelope[LegalDocumentList])
async def list_documents(
    q: Annotated[str | None, Query(max_length=200)] = None,
    category: LegalCategory | None = None,
    service: LegalService = Depends(get_legal_service),
) -> Envelope[LegalDocumentList]:
    return Envelope(data=service.list_documents(q, category))


@router.get("/{slug}", response_model=Envelope[LegalDocument])
async def get_document(
    slug: str,
    service: LegalService = Depends(get_legal_service),
) -> Envelope[LegalDocument]:
    return Envelope(data=service.get_document(slug))
