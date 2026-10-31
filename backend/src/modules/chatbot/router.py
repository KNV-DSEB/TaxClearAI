from fastapi import APIRouter, Depends

from src.core.config import get_settings
from src.core.rate_limit import enforce_chatbot_rate_limit
from src.modules.chatbot.pipeline import ChatbotPipeline
from src.modules.chatbot.retriever import KeywordRetriever
from src.modules.chatbot.schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/chatbot", tags=["chatbot"])


def get_chatbot_pipeline() -> ChatbotPipeline:
    settings = get_settings()
    return ChatbotPipeline(
        settings,
        KeywordRetriever(
            min_score=settings.chatbot_min_retrieval_score,
        ),
    )


@router.post(
    "/ask",
    response_model=ChatResponse,
    dependencies=[Depends(enforce_chatbot_rate_limit)],
)
async def ask_chatbot(
    request: ChatRequest,
    pipeline: ChatbotPipeline = Depends(get_chatbot_pipeline),
) -> ChatResponse:
    return await pipeline.answer(request)
