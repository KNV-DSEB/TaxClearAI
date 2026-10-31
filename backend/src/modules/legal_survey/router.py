from fastapi import APIRouter, Depends

from src.core.rate_limit import enforce_api_rate_limit
from src.modules.legal_survey.repository import LegalSurveyRepository
from src.modules.legal_survey.schemas import (
    ClassificationResponse,
    SurveyAnswers,
    SurveyQuestion,
)
from src.modules.legal_survey.service import LegalSurveyService

router = APIRouter(prefix="/survey", tags=["legal survey"])


def get_legal_survey_service() -> LegalSurveyService:
    return LegalSurveyService(LegalSurveyRepository())


@router.get("/questions", response_model=list[SurveyQuestion])
async def get_questions(
    service: LegalSurveyService = Depends(get_legal_survey_service),
) -> list[SurveyQuestion]:
    return service.get_questions()


@router.post(
    "/classify",
    response_model=ClassificationResponse,
    dependencies=[Depends(enforce_api_rate_limit)],
)
async def classify(
    answers: SurveyAnswers,
    service: LegalSurveyService = Depends(get_legal_survey_service),
) -> ClassificationResponse:
    return service.classify(answers)
