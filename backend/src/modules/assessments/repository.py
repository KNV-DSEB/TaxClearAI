from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import case, delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.assessment import Assessment, ChecklistItem
from src.modules.assessments.domain import AssessmentRecord, AssessmentSummaryRecord
from src.modules.assessments.schemas import (
    Answers,
    ChecklistItemView,
    ItemStatus,
    Summary,
)


def item_view(item: ChecklistItem) -> ChecklistItemView:
    return ChecklistItemView.model_validate(
        {
            "id": item.id,
            "code": item.item_code,
            "label": item.label_snapshot,
            "status": item.status,
            "review_status": item.review_status,
        }
    )


class AssessmentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, owner_id: UUID, record: AssessmentRecord) -> None:
        async with self.session.begin():
            self.session.add(
                Assessment(
                    id=record.id,
                    owner_id=owner_id,
                    answers=record.answers.model_dump(mode="json"),
                    content_version=record.content_version,
                    summary_snapshot=record.summary.model_dump(mode="json"),
                    expires_at=record.expires_at,
                    created_at=record.created_at,
                    updated_at=record.updated_at,
                )
            )
            await self.session.flush()
            self.session.add_all(
                [
                    ChecklistItem(
                        id=item.id,
                        assessment_id=record.id,
                        item_code=item.code,
                        label_snapshot=item.label,
                        review_status=item.review_status,
                        status=item.status,
                    )
                    for item in record.checklist
                ]
            )

    async def get(self, owner_id: UUID, assessment_id: UUID) -> AssessmentRecord | None:
        row = await self.session.scalar(
            select(Assessment).where(
                Assessment.id == assessment_id,
                Assessment.owner_id == owner_id,
                Assessment.expires_at > datetime.now(UTC),
            )
        )
        if row is None:
            return None
        items = await self.session.scalars(
            select(ChecklistItem)
            .where(
                ChecklistItem.assessment_id == assessment_id,
            )
            .order_by(ChecklistItem.created_at, ChecklistItem.id)
            .limit(19)
        )
        return AssessmentRecord(
            id=row.id,
            content_version=row.content_version,
            answers=Answers.model_validate(row.answers),
            summary=Summary.model_validate(row.summary_snapshot),
            checklist=[item_view(item) for item in items],
            created_at=row.created_at,
            updated_at=row.updated_at,
            expires_at=row.expires_at,
        )

    async def update_item(
        self,
        owner_id: UUID,
        assessment_id: UUID,
        item_id: UUID,
        status: ItemStatus,
    ) -> ChecklistItemView | None:
        async with self.session.begin():
            row = await self.session.scalar(
                select(Assessment)
                .where(
                    Assessment.id == assessment_id,
                    Assessment.owner_id == owner_id,
                    Assessment.expires_at > datetime.now(UTC),
                )
                .with_for_update()
            )
            if row is None:
                return None
            item = await self.session.scalar(
                update(ChecklistItem)
                .where(
                    ChecklistItem.id == item_id,
                    ChecklistItem.assessment_id == assessment_id,
                )
                .values(status=status)
                .returning(ChecklistItem)
            )
            if item is None:
                return None
            row.updated_at = datetime.now(UTC)
            return item_view(item)

    async def list_page(
        self, owner_id: UUID, offset: int, limit: int
    ) -> tuple[list[AssessmentSummaryRecord], int]:
        total = await self.session.scalar(
            select(func.count()).select_from(Assessment).where(Assessment.owner_id == owner_id)
        )
        counts = (
            select(
                ChecklistItem.assessment_id,
                func.count(case((ChecklistItem.status == "available", 1))).label("available"),
                func.count(case((ChecklistItem.status == "missing", 1))).label("missing"),
                func.count(case((ChecklistItem.status == "needs_verification", 1))).label(
                    "needs_verification"
                ),
            )
            .group_by(ChecklistItem.assessment_id)
            .subquery()
        )
        rows = await self.session.execute(
            select(
                Assessment,
                func.coalesce(counts.c.available, 0),
                func.coalesce(counts.c.missing, 0),
                func.coalesce(counts.c.needs_verification, 0),
            )
            .outerjoin(counts, counts.c.assessment_id == Assessment.id)
            .where(Assessment.owner_id == owner_id)
            .order_by(Assessment.updated_at.desc(), Assessment.id)
            .offset(offset)
            .limit(limit)
        )
        records = [
            AssessmentSummaryRecord(
                id=row.id,
                scope=Summary.model_validate(row.summary_snapshot).scope,
                available=available,
                missing=missing,
                needs_verification=needs_verification,
                created_at=row.created_at,
                updated_at=row.updated_at,
                expires_at=row.expires_at,
            )
            for row, available, missing, needs_verification in rows.all()
        ]
        await self.session.rollback()
        return records, total or 0

    async def remove(self, owner_id: UUID, assessment_id: UUID) -> bool:
        # Chủ hồ sơ vẫn xóa được hồ sơ đã hết hạn: hết hạn chỉ chặn đọc/sửa, không chặn xóa
        result = await self.session.execute(
            delete(Assessment)
            .where(Assessment.id == assessment_id, Assessment.owner_id == owner_id)
            .returning(Assessment.id)
        )
        removed = result.scalar_one_or_none() is not None
        await self.session.commit()
        return removed

    async def purge_expired(self, now: datetime, apply: bool) -> int:
        expired = Assessment.expires_at <= now
        if not apply:
            count = await self.session.scalar(
                select(func.count()).select_from(Assessment).where(expired)
            )
            await self.session.rollback()
            return count or 0
        result = await self.session.execute(
            delete(Assessment).where(expired).returning(Assessment.id)
        )
        removed = len(result.all())
        await self.session.commit()
        return removed
