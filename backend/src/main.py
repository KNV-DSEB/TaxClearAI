from fastapi import FastAPI

from src.core.config import get_settings
from src.core.exceptions import register_exception_handlers
from src.core.logging import configure_logging
from src.core.middleware import register_middleware
from src.modules.case_brief.router import router as case_brief_router
from src.modules.chatbot.router import router as chatbot_router
from src.modules.conversion_planner.router import router as conversion_planner_router
from src.modules.document_checklist.router import router as document_checklist_router
from src.modules.expert_directory.router import router as expert_directory_router
from src.modules.health.router import router as health_router
from src.modules.legal_library.router import router as legal_library_router
from src.modules.legal_survey.router import router as legal_survey_router
from src.modules.procedure_roadmap.router import router as procedure_roadmap_router
from src.modules.process_tracker.router import router as process_tracker_router

configure_logging()

app = FastAPI(title=get_settings().app_title)

register_middleware(app)
register_exception_handlers(app)

app.include_router(health_router)
app.include_router(document_checklist_router)
app.include_router(legal_survey_router)
app.include_router(legal_library_router)
app.include_router(procedure_roadmap_router)
app.include_router(process_tracker_router)
app.include_router(case_brief_router)
app.include_router(conversion_planner_router)
app.include_router(chatbot_router)
app.include_router(expert_directory_router)
