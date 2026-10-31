from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import and_, case, delete, func, not_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.assessment import Assessment, ChecklistItem
from src.modules.assessments.domain import AssessmentRecord, AssessmentSummaryRecord
from src.modules.assessments.schemas import (
    Answers,
    CaseFilter,
    ChecklistItemView,
    ItemStatus,
    StatusCounts,
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
        self, owner_id: UUID, offset: int, limit: int, case_filter: CaseFilter, now: datetime
    ) -> tuple[list[AssessmentSummaryRecord], int, StatusCounts]:
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
        available = func.coalesce(counts.c.available, 0)
        missing = func.coalesce(counts.c.missing, 0)
        needs_verification = func.coalesce(counts.c.needs_verification, 0)
        active = Assessment.expires_at > now
        # Cùng định nghĩa với service.case_status(): hồ sơ B2 đủ giấy tờ khi mọi mục là "Đã có"
        ready = and_(
            active,
            Assessment.summary_snapshot["scope"].astext == "b2",
            available > 0,
            missing == 0,
            needs_verification == 0,
        )
        base = (
            select(Assessment, available, missing, needs_verification)
            .outerjoin(counts, counts.c.assessment_id == Assessment.id)
            .where(Assessment.owner_id == owner_id)
        )
        tally = (
            await self.session.execute(
                select(
                    func.count(),
                    func.count().filter(and_(active, not_(ready))),
                    func.count().filter(ready),
                )
                .select_from(Assessment)
                .outerjoin(counts, counts.c.assessment_id == Assessment.id)
                .where(Assessment.owner_id == owner_id)
            )
        ).one()
        filtered = base
        if case_filter == "ready":
            filtered = base.where(ready)
        elif case_filter == "in_progress":
            filtered = base.where(active, not_(ready))
        rows = await self.session.execute(
            filtered.order_by(Assessment.updated_at.desc(), Assessment.id)
            .offset(offset)
            .limit(limit)
        )
        records = [
            AssessmentSummaryRecord(
                id=row.id,
                scope=Summary.model_validate(row.summary_snapshot).scope,
                available=row_available,
                missing=row_missing,
                needs_verification=row_needs_verification,
                created_at=row.created_at,
                updated_at=row.updated_at,
                expires_at=row.expires_at,
            )
            for row, row_available, row_missing, row_needs_verification in rows.all()
        ]
        await self.session.rollback()
        status_counts = StatusCounts(all=tally[0], in_progress=tally[1], ready=tally[2])
        total = {"all": tally[0], "in_progress": tally[1], "ready": tally[2]}[case_filter]
        return records, total, status_counts

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
