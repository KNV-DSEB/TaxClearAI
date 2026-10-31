from fastapi import FastAPI

from src.core.config import get_settings
from src.core.exceptions import register_exception_handlers
from src.core.logging import configure_logging
from src.core.middleware import register_middleware
from src.modules.health.router import router as health_router

configure_logging()

app = FastAPI(title=get_settings().app_title)

register_middleware(app)
register_exception_handlers(app)

app.include_router(health_router)
