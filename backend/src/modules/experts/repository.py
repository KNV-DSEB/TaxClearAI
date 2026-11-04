from uuid import UUID, uuid4

from sqlalchemy import case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement

from src.models.expert import ConsultationRequest, Expert
from src.modules.experts.domain import ConsultationRecord, ExpertRecord, ExpertSeed


def _expert_record(row: Expert) -> ExpertRecord:
    return ExpertRecord(
        id=row.id,
        full_name=row.full_name,
        title=row.title,
        organization=row.organization,
        avatar_url=row.avatar_url,
        bio=row.bio,
        specializations=row.specializations,
        partner_type=row.partner_type,
        services_offered=row.services_offered,
        location=row.location,
        experience_years=row.experience_years,
        consultation_fee_text=row.consultation_fee_text,
        is_verified=row.is_verified,
    )


class ExpertRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_experts(
        self,
        keyword: str | None,
        specialization: str | None,
        location: str | None,
        partner_type: str | None,
        offset: int,
        limit: int,
    ) -> tuple[list[ExpertRecord], int]:
        statement = select(Expert).where(Expert.is_active.is_(True))
        count_statement = select(func.count()).select_from(Expert).where(Expert.is_active.is_(True))
        if keyword:
            pattern = f"%{keyword}%"
            criterion = or_(
                Expert.full_name.ilike(pattern),
                Expert.title.ilike(pattern),
                Expert.organization.ilike(pattern),
                Expert.bio.ilike(pattern),
                Expert.specializations.ilike(pattern),
            )
            statement = statement.where(criterion)
            count_statement = count_statement.where(criterion)
        if specialization:
            criterion = Expert.specializations.ilike(f"%{specialization}%")
            statement = statement.where(criterion)
            count_statement = count_statement.where(criterion)
        if location:
            criterion = Expert.location.ilike(location)
            statement = statement.where(criterion)
            count_statement = count_statement.where(criterion)
        if partner_type:
            statement = statement.where(Expert.partner_type == partner_type)
            count_statement = count_statement.where(Expert.partner_type == partner_type)
        rows = await self.session.scalars(
            statement.order_by(Expert.is_verified.desc(), Expert.full_name)
            .offset(offset)
            .limit(limit)
        )
        total = await self.session.scalar(count_statement)
        return [_expert_record(row) for row in rows], total or 0

    async def get_expert(self, expert_id: UUID) -> ExpertRecord | None:
        row = await self.session.scalar(
            select(Expert).where(Expert.id == expert_id, Expert.is_active.is_(True))
        )
        return _expert_record(row) if row else None

    async def list_recommended_experts(
        self, specializations: list[str], limit: int
    ) -> list[tuple[ExpertRecord, int]]:
        if not specializations:
            return []
        matches = [
            case(
                (
                    or_(
                        Expert.specializations.ilike(f"%{specialization}%"),
                        Expert.services_offered.ilike(f"%{specialization}%"),
                    ),
                    1,
                ),
                else_=0,
            )
            for specialization in specializations
        ]
        match_count: ColumnElement[int] = matches[0]
        for match in matches[1:]:
            match_count = match_count + match
        rows = await self.session.execute(
            select(Expert, match_count.label("match_count"))
            .where(Expert.is_active.is_(True), match_count > 0)
            .order_by(match_count.desc(), Expert.is_verified.desc(), Expert.full_name)
            .limit(limit)
        )
        return [(_expert_record(row), score) for row, score in rows.all()]

    async def list_senior_generalist_experts(self, limit: int = 2) -> list[ExpertRecord]:
        rows = await self.session.scalars(
            select(Expert)
            .where(Expert.is_active.is_(True))
            .order_by(
                Expert.experience_years.desc(),
                Expert.is_verified.desc(),
                Expert.full_name,
            )
            .limit(limit)
        )
        return [_expert_record(row) for row in rows]

    async def create_consultation_request(
        self,
        expert_id: UUID,
        user_id: UUID | None,
        assessment_id: UUID | None,
        contact_name: str,
        contact_phone: str,
        contact_email: str | None,
        business_type: str | None,
        consultation_method: str,
        notes: str,
        service_needed: str | None,
        share_data_consent: bool,
        data_snapshot: str | None,
    ) -> ConsultationRecord:
        request = ConsultationRequest(
            id=uuid4(),
            expert_id=expert_id,
            user_id=user_id,
            assessment_id=assessment_id,
            contact_name=contact_name,
            contact_phone=contact_phone,
            contact_email=contact_email,
            business_type=business_type,
            service_needed=service_needed,
            share_data_consent=share_data_consent,
            data_snapshot=data_snapshot,
            consultation_method=consultation_method,
            notes=notes,
            status="pending",
        )
        self.session.add(request)
        await self.session.commit()
        await self.session.refresh(request)
        return ConsultationRecord(
            id=request.id,
            expert_id=request.expert_id,
            status=request.status,
            created_at=request.created_at,
        )

    async def seed_experts(self, records: list[ExpertSeed]) -> None:
        existing_rows = await self.session.scalars(select(Expert))
        existing_by_id = {row.id: row for row in existing_rows}
        for record in records:
            row = existing_by_id.get(record.id)
            if row is None:
                row = Expert(id=record.id)
                self.session.add(row)
                existing_by_id[record.id] = row
            row.full_name = record.full_name
            row.title = record.title
            row.organization = record.organization
            row.avatar_url = None
            row.bio = record.bio
            row.specializations = record.specializations
            row.partner_type = record.partner_type
            row.services_offered = record.services_offered
            row.location = record.location
            row.experience_years = record.experience_years
            row.consultation_fee_text = record.consultation_fee_text
            row.is_verified = False
            row.is_active = True
        await self.session.commit()
