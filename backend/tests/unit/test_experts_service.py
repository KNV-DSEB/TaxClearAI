import asyncio
import json
from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

from src.modules.assessments.schemas import Summary
from src.modules.experts.domain import ExpertRecord
from src.modules.experts.schemas import CreateConsultationRequest
from src.modules.experts.service import ExpertService
from tests.fixtures import company


def expert(full_name: str, years: int, specializations: str) -> ExpertRecord:
    return ExpertRecord(
        id=uuid4(),
        full_name=full_name,
        title="Chuyên gia",
        organization="Đơn vị tư vấn",
        avatar_url=None,
        bio="Hồ sơ thử nghiệm",
        specializations=specializations,
        location="Toàn quốc",
        experience_years=years,
        consultation_fee_text="Liên hệ",
        is_verified=False,
    )


def answers(**changes: object) -> dict[str, object]:
    return company(**changes)


class FakeAssessmentRepository:
    def __init__(self, assessment: SimpleNamespace) -> None:
        self.assessment = assessment

    async def get(self, owner_id, assessment_id):
        return self.assessment


class FakeExpertRepository:
    def __init__(self, senior_records: list[ExpertRecord]) -> None:
        self.senior_records = senior_records
        self.recommended_calls = 0

    async def list_recommended_experts(self, tags: list[str], limit: int):
        self.recommended_calls += 1
        return []

    async def list_senior_generalist_experts(self, limit: int = 2):
        return self.senior_records[:limit]


class ConsultationExpertRepository(FakeExpertRepository):
    def __init__(self, expert_record: ExpertRecord) -> None:
        super().__init__([])
        self.expert_record = expert_record
        self.request_data = None

    async def get_expert(self, expert_id):
        return self.expert_record if expert_id == self.expert_record.id else None

    async def create_consultation_request(self, **kwargs):
        self.request_data = kwargs
        return SimpleNamespace(
            id=uuid4(),
            expert_id=kwargs["expert_id"],
            status="pending",
            created_at=datetime.now(UTC),
        )

    async def list_experts(self, *args):
        self.list_args = args
        return [self.expert_record], 1


class FakeAssessmentLookup:
    def __init__(self, assessment):
        self.assessment = assessment

    async def get(self, owner_id, assessment_id):
        return self.assessment


def make_assessment(scope: str, assessment_answers: dict[str, object]) -> SimpleNamespace:
    return SimpleNamespace(
        answers=assessment_answers,
        summary=Summary(
            scope=scope,
            known_facts=[],
            unknown_facts=[],
            review_reasons=[],
            notice="Bản thử.",
        ),
    )


def test_needs_confirmation_recommends_senior_generalists_even_when_goal_has_tags():
    seniors = [
        expert("Chuyên gia 15 năm", 15, "Thuế, Pháp lý doanh nghiệp"),
        expert("Chuyên gia 12 năm", 12, "Kế toán, Giải thể doanh nghiệp"),
    ]
    expert_repository = FakeExpertRepository(seniors)
    service = ExpertService(
        expert_repository,
        FakeAssessmentRepository(make_assessment("needs_confirmation", answers())),
    )

    result = asyncio.run(service.recommend_experts_for_assessment(uuid4(), uuid4()))

    assert [item.expert.experience_years for item in result] == [15, 12]
    assert all(item.expert.experience_years >= 10 for item in result)
    assert all(str(item.expert.experience_years) in item.match_reason for item in result)
    assert all(item.expert.specializations[0] in item.match_reason for item in result)
    assert expert_repository.recommended_calls == 0


def test_no_specialty_matches_falls_back_to_senior_experts():
    seniors = [expert("Chuyên gia 15 năm", 15, "Thuế, Pháp lý doanh nghiệp")]
    expert_repository = FakeExpertRepository(seniors)
    service = ExpertService(
        expert_repository,
        FakeAssessmentRepository(
            make_assessment(
                "b2",
                answers(hasRevenue="yes", dnTaxDebt="no", dnRecords="complete"),
            )
        ),
    )

    result = asyncio.run(service.recommend_experts_for_assessment(uuid4(), uuid4()))

    assert len(result) == 1
    assert result[0].expert.full_name == "Chuyên gia 15 năm"
    assert expert_repository.recommended_calls == 1


def test_list_experts_passes_partner_type_filter_to_repository():
    record = expert("Đối tác kế toán", 11, "Sổ sách kế toán")
    repository = ConsultationExpertRepository(record)
    service = ExpertService(repository, FakeAssessmentRepository(None))

    result = asyncio.run(service.list_experts(None, None, None, "accountant", 1, 20))

    assert result.items[0].partner_type == "tax_consultant"
    assert repository.list_args[3] == "accountant"


def test_consultation_request_stores_service_and_consented_assessment_snapshot():
    record = expert("Đối tác kế toán", 11, "Sổ sách kế toán")
    assessment = make_assessment("b2", answers())
    assessment.answers = answers()
    assessment.checklist = []
    repository = ConsultationExpertRepository(record)
    service = ExpertService(repository, FakeAssessmentLookup(assessment))
    request = CreateConsultationRequest(
        expert_id=record.id,
        assessment_id=uuid4(),
        contact_name="  Nguyễn An  ",
        contact_phone="0912345678",
        notes="  Rà soát sổ sách  ",
        service_needed="Dọn dẹp và hoàn thiện sổ sách kế toán",
        share_data_consent=True,
        sample_acknowledged=True,
    )

    asyncio.run(service.create_consultation_request(request, uuid4()))

    assert repository.request_data["service_needed"] == "Dọn dẹp và hoàn thiện sổ sách kế toán"
    assert repository.request_data["share_data_consent"] is True
    snapshot = json.loads(repository.request_data["data_snapshot"])
    assert snapshot["scope"] == "b2"
    assert snapshot["answers"]["businessType"] == "company"
    assert snapshot["checklist"] == []
