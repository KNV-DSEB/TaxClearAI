import re
from uuid import UUID

from src.core.errors import ApplicationError
from src.models.community import CommunityQuestion, CommunityTopic
from src.modules.community.repository import CommunityRepository
from src.modules.community.schemas import (
    CommunityQuestionItem,
    CommunityQuestionPage,
    CreateQuestionRequest,
    TopicView,
)


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _topic_view(topic: CommunityTopic) -> TopicView:
    return TopicView(id=topic.id, slug=topic.slug, name=topic.name, order_index=topic.order_index)


def _question_view(
    question: CommunityQuestion, topic: CommunityTopic
) -> CommunityQuestionItem:
    return CommunityQuestionItem(
        id=question.id,
        topic=_topic_view(topic),
        author_name=question.author_name,
        title=question.title,
        question_content=question.question_content,
        answer_content=question.answer_content,
        answered_by=question.answered_by,
        answered_at=question.answered_at,
        created_at=question.created_at,
    )


class CommunityService:
    def __init__(self, repository: CommunityRepository) -> None:
        self.repository = repository

    async def list_topics(self) -> list[TopicView]:
        return [_topic_view(topic) for topic in await self.repository.list_topics()]

    async def list_questions(
        self, keyword: str | None, topic_slug: str | None, page: int, page_size: int
    ) -> CommunityQuestionPage:
        cleaned_keyword = _clean_text(keyword) if keyword else None
        rows, total = await self.repository.list_questions(
            cleaned_keyword or None, topic_slug, (page - 1) * page_size, page_size
        )
        return CommunityQuestionPage(
            items=[_question_view(question, topic) for question, topic in rows],
            page=page,
            page_size=page_size,
            total=total,
        )

    async def get_question(self, question_id: UUID) -> CommunityQuestionItem:
        row = await self.repository.get_question(question_id)
        if row is None:
            raise ApplicationError(404, "Không tìm thấy câu hỏi hoặc câu hỏi chưa được công bố.")
        question, topic = row
        return _question_view(question, topic)

    async def create_question(
        self, request: CreateQuestionRequest, author_id: UUID | None = None
    ) -> CommunityQuestionItem:
        topic = await self.repository.get_topic(request.topic_slug)
        if topic is None:
            raise ApplicationError(404, "Không tìm thấy chủ đề đang hoạt động.")
        author_name = _clean_text(request.author_name) if request.author_name else "Người dùng ẩn danh"
        question, topic = await self.repository.create_question(
            topic,
            author_name,
            author_id,
            _clean_text(request.title),
            _clean_text(request.question_content),
        )
        return _question_view(question, topic)
