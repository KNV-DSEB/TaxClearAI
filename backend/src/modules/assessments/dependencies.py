from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.modules.assessments.repository import AssessmentRepository
from src.modules.assessments.service import AssessmentService


def get_assessment_service(
    session: AsyncSession = Depends(get_db, use_cache=False),
) -> AssessmentService:
    return AssessmentService(AssessmentRepository(session))
