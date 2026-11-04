from uuid import UUID, uuid4

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.community import CommunityQuestion, CommunityTopic


class CommunityRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_topics(self) -> list[CommunityTopic]:
        result = await self.session.scalars(
            select(CommunityTopic)
            .where(CommunityTopic.is_active.is_(True))
            .order_by(CommunityTopic.order_index, CommunityTopic.name)
        )
        return list(result)

    async def get_topic(self, slug: str) -> CommunityTopic | None:
        return await self.session.scalar(
            select(CommunityTopic).where(
                CommunityTopic.slug == slug, CommunityTopic.is_active.is_(True)
            )
        )

    async def get_question(
        self, question_id: UUID
    ) -> tuple[CommunityQuestion, CommunityTopic] | None:
        statement = (
            select(CommunityQuestion, CommunityTopic)
            .join(CommunityTopic, CommunityQuestion.topic_id == CommunityTopic.id)
            .where(
                CommunityQuestion.id == question_id,
                CommunityQuestion.is_published.is_(True),
                CommunityTopic.is_active.is_(True),
            )
        )
        row = await self.session.execute(statement)
        return row.first()

    async def list_questions(
        self, keyword: str | None, topic_slug: str | None, offset: int, limit: int
    ) -> tuple[list[tuple[CommunityQuestion, CommunityTopic]], int]:
        statement = (
            select(CommunityQuestion, CommunityTopic)
            .join(CommunityTopic, CommunityQuestion.topic_id == CommunityTopic.id)
            .where(
                CommunityQuestion.is_published.is_(True), CommunityTopic.is_active.is_(True)
            )
        )
        count_statement = (
            select(func.count())
            .select_from(CommunityQuestion)
            .join(CommunityTopic, CommunityQuestion.topic_id == CommunityTopic.id)
            .where(CommunityQuestion.is_published.is_(True), CommunityTopic.is_active.is_(True))
        )
        if keyword:
            pattern = f"%{keyword}%"
            criterion = or_(
                CommunityQuestion.title.ilike(pattern),
                CommunityQuestion.question_content.ilike(pattern),
            )
            statement = statement.where(criterion)
            count_statement = count_statement.where(criterion)
        if topic_slug:
            statement = statement.where(CommunityTopic.slug == topic_slug)
            count_statement = count_statement.where(CommunityTopic.slug == topic_slug)
        rows = await self.session.execute(
            statement.order_by(CommunityQuestion.created_at.desc(), CommunityQuestion.id)
            .offset(offset)
            .limit(limit)
        )
        total = await self.session.scalar(count_statement)
        return list(rows.all()), total or 0

    async def create_question(
        self,
        topic: CommunityTopic,
        author_name: str,
        author_id: UUID | None,
        title: str,
        question_content: str,
    ) -> tuple[CommunityQuestion, CommunityTopic]:
        question = CommunityQuestion(
            id=uuid4(),
            topic_id=topic.id,
            author_name=author_name,
            author_id=author_id,
            title=title,
            question_content=question_content,
            is_published=True,
        )
        self.session.add(question)
        await self.session.commit()
        await self.session.refresh(question)
        return question, topic
