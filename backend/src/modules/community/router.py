from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response

from src.core.schemas import Envelope
from src.modules.auth.dependencies import get_optional_user
from src.modules.auth.domain import UserRecord
from src.modules.community.dependencies import get_community_service
from src.modules.community.schemas import (
    CommunityQuestionItem,
    CommunityQuestionPage,
    CreateQuestionRequest,
    TopicView,
)
from src.modules.community.service import CommunityService

router = APIRouter(prefix="/api/v1/community", tags=["community"])


@router.get("/topics", response_model=Envelope[list[TopicView]])
async def list_topics(
    service: CommunityService = Depends(get_community_service),
) -> Envelope[list[TopicView]]:
    return Envelope(data=await service.list_topics())


@router.get("/questions", response_model=Envelope[CommunityQuestionPage])
async def list_questions(
    q: str | None = Query(default=None, max_length=200),
    topic: str | None = Query(default=None, max_length=120),
    page: int = Query(default=1, ge=1, le=1000),
    page_size: int = Query(default=20, ge=1, le=100, alias="pageSize"),
    service: CommunityService = Depends(get_community_service),
) -> Envelope[CommunityQuestionPage]:
    return Envelope(data=await service.list_questions(q, topic, page, page_size))


@router.get("/questions/{question_id}", response_model=Envelope[CommunityQuestionItem])
async def read_question(
    question_id: UUID,
    service: CommunityService = Depends(get_community_service),
) -> Envelope[CommunityQuestionItem]:
    return Envelope(data=await service.get_question(question_id))


@router.post("/questions", status_code=201, response_model=Envelope[CommunityQuestionItem])
async def create_question(
    data: CreateQuestionRequest,
    response: Response,
    user: UserRecord | None = Depends(get_optional_user),
    service: CommunityService = Depends(get_community_service),
) -> Envelope[CommunityQuestionItem]:
    author_id = user.id if user else None
    result = await service.create_question(data, author_id)
    response.headers["Location"] = f"/api/v1/community/questions/{result.id}"
    return Envelope(data=result)
