from datetime import datetime
from uuid import UUID

from pydantic import Field

from src.core.schemas import ApiModel


class TopicView(ApiModel):
    id: UUID
    slug: str
    name: str
    order_index: int


class CommunityQuestionItem(ApiModel):
    id: UUID
    topic: TopicView
    author_name: str
    title: str
    question_content: str
    answer_content: str | None
    answered_by: str | None
    answered_at: datetime | None
    created_at: datetime


class CommunityQuestionPage(ApiModel):
    items: list[CommunityQuestionItem]
    page: int
    page_size: int
    total: int


class CreateQuestionRequest(ApiModel):
    topic_slug: str = Field(min_length=1, max_length=120)
    author_name: str | None = Field(default=None, max_length=120)
    title: str = Field(min_length=5, max_length=200)
    question_content: str = Field(min_length=10, max_length=10000)
