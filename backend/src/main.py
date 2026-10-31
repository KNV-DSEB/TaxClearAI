from fastapi import FastAPI

from src.core.config import get_settings
from src.core.exceptions import register_exception_handlers
from src.core.logging import configure_logging
from src.core.middleware import register_middleware
from src.modules.assessments.router import router as assessments_router
from src.modules.auth.router import router as auth_router
from src.modules.chat.legal_sources import LegalSourceSelector
from src.modules.chat.provider import GeminiProvider
from src.modules.chat.router import router as chat_router
from src.modules.chat.service import ChatService
from src.modules.health.router import router as health_router


def create_app() -> FastAPI:
    configure_logging()
    application = FastAPI(title="Tax Clear AI", version="0.1.0")
    settings = get_settings()
    application.state.chat_service = ChatService(
        GeminiProvider(settings.gemini_api_key, settings.gemini_model),
        legal_selector=LegalSourceSelector().select,
    )
    register_middleware(application)
    register_exception_handlers(application)
    application.include_router(health_router)
    application.include_router(auth_router)
    application.include_router(assessments_router)
    application.include_router(chat_router)
    return application


app = create_app()
