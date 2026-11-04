from src.modules.legal.repository import LegalRepository
from src.modules.legal.service import LegalService


def get_legal_service() -> LegalService:
    return LegalService(LegalRepository())
