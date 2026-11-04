from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.modules.assessments.repository import AssessmentRepository
from src.modules.experts.repository import ExpertRepository
from src.modules.experts.service import ExpertService


def get_expert_service(
    session: AsyncSession = Depends(get_db, use_cache=False),
) -> ExpertService:
    return ExpertService(ExpertRepository(session), AssessmentRepository(session))
