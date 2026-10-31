from fastapi import APIRouter, Depends

from src.core.config import get_settings
from src.core.rate_limit import enforce_api_rate_limit
from src.modules.legal_survey.ai_classifier import create_situation_classifier
from src.modules.legal_survey.repository import LegalSurveyRepository
from src.modules.legal_survey.schemas import (
    ChatContextResponse,
    ClassificationResponse,
    SurveyAnswers,
    SurveyQuestion,
)
from src.modules.legal_survey.service import LegalSurveyService

router = APIRouter(prefix="/survey", tags=["legal survey"])


def get_legal_survey_service() -> LegalSurveyService:
    settings = get_settings()
    return LegalSurveyService(
        LegalSurveyRepository(),
        create_situation_classifier(settings),
        survey_ai_enabled=settings.survey_ai_enabled,
    )


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
    return await service.classify(answers)


@router.post("/chat-context", response_model=ChatContextResponse)
async def build_chat_context(
    classification: ClassificationResponse,
    service: LegalSurveyService = Depends(get_legal_survey_service),
) -> ChatContextResponse:
    return service.chat_context(classification)
