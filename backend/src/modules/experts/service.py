import json
import re
from uuid import UUID

from src.core.errors import ApplicationError
from src.modules.assessments.repository import AssessmentRepository
from src.modules.experts.domain import ExpertRecord
from src.modules.experts.repository import ExpertRepository
from src.modules.experts.schemas import (
    ConsultationResponse,
    CreateConsultationRequest,
    ExpertPage,
    ExpertView,
    RecommendedExpertView,
)


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _expert_view(record: ExpertRecord) -> ExpertView:
    return ExpertView(
        id=record.id,
        full_name=record.full_name,
        title=record.title,
        organization=record.organization,
        avatar_url=record.avatar_url,
        bio=record.bio,
        specializations=[
            item.strip() for item in record.specializations.split(",") if item.strip()
        ],
        partner_type=record.partner_type,
        services_offered=[
            item.strip() for item in record.services_offered.split(",") if item.strip()
        ],
        location=record.location,
        experience_years=record.experience_years,
        consultation_fee_text=record.consultation_fee_text,
        is_verified=record.is_verified,
    )


class ExpertService:
    def __init__(
        self, repository: ExpertRepository, assessment_repository: AssessmentRepository
    ) -> None:
        self.repository = repository
        self.assessment_repository = assessment_repository

    async def recommend_experts_for_assessment(
        self, assessment_id: UUID, user_id: UUID | None
    ) -> list[RecommendedExpertView]:
        if user_id is None:
            raise ApplicationError(401, "Vui lòng đăng nhập để xem gợi ý chuyên gia.")
        assessment = await self.assessment_repository.get(user_id, assessment_id)
        if assessment is None:
            raise ApplicationError(404, "Không tìm thấy hồ sơ hoặc hồ sơ đã hết hạn.")

        answers = assessment.answers
        matching_groups: list[tuple[list[str], str]] = []
        if (
            answers.get("taxNoticeStatus") == "yes"
            or answers.get("filingStatus") in ("incomplete", "never")
            or answers.get("dnTaxDebt") in ("yes", "unreconciled")
            or answers.get("hhTaxObligation") == "yes"
        ):
            matching_groups.append(
                (
                    ["Quyết toán thuế", "Đóng mã số thuế", "Thuế tồn đọng"],
                    "Hồ sơ của bạn có phát sinh vướng mắc về kê khai hoặc nghĩa vụ thuế "
                    "cần chuyên viên rà soát.",
                )
            )
        if "dissolution" in (answers.get("goal"), answers.get("procedure")):
            matching_groups.append(
                (
                    ["Giải thể DN", "Thanh lý tài sản"],
                    "Chuyên gia chuyên sâu về trình tự và thủ tục đóng mã số thuế, "
                    "giải thể doanh nghiệp.",
                )
            )
        if answers.get("businessType") == "household":
            matching_groups.append(
                (
                    ["Hộ kinh doanh"],
                    "Chuyên gia có kinh nghiệm xử lý thủ tục chấm dứt và chuyển đổi hộ kinh doanh.",
                )
            )
        if assessment.summary.scope in {"b2", "a3"}:
            matching_groups.append(
                (
                    ["Sổ sách kế toán", "Dọn dẹp sổ sách", "Hộ kinh doanh", "Báo cáo tài chính"],
                    "Hồ sơ có tồn đọng hoặc chênh lệch số liệu, phù hợp với đơn vị kế toán có thể "
                    "rà soát chứng từ và sổ sách.",
                )
            )
        if (
            answers.get("laborInsuranceStatus") == "obligations"
            or answers.get("hhEmployees") == "unresolved"
        ):
            matching_groups.append(
                (
                    ["Bảo hiểm xã hội", "Lao động"],
                    "Cần rà soát hoàn tất nghĩa vụ bảo hiểm và lao động trước khi giải thể.",
                )
            )
        if answers.get("goal") == "other" or answers.get("procedure") in (
            "suspension",
            "conversion",
        ):
            matching_groups.append(
                (
                    ["Chuyển đổi loại hình", "Tạm ngừng kinh doanh"],
                    "Chuyên gia phù hợp với nhu cầu chuyển đổi loại hình hoặc "
                    "tạm ngừng kinh doanh.",
                )
            )

        tags = list(dict.fromkeys(tag for group, _ in matching_groups for tag in group))
        records = (
            []
            if assessment.summary.scope == "needs_confirmation"
            else await self.repository.list_recommended_experts(tags, limit=6)
        )
        if assessment.summary.scope in {"b2", "a3"}:
            records.sort(
                key=lambda item: (
                    item[0].partner_type not in {"accounting_firm", "accountant"},
                    -item[1],
                    not item[0].is_verified,
                )
            )
            records = records[:3]
        recommendations = []
        if not records:
            senior_records = await self.repository.list_senior_generalist_experts(limit=2)
            for record in senior_records:
                expert = _expert_view(record)
                specializations = ", ".join(expert.specializations[:3])
                recommendations.append(
                    RecommendedExpertView(
                        expert=expert,
                        match_reason=(
                            f"Chuy\u00ean gia {expert.experience_years} n\u0103m kinh nghi\u1ec7m "
                            "\u0111a l\u0129nh v\u1ef1c "
                            f"({specializations}), ph\u00f9 h\u1ee3p "
                            "\u0111\u1ec3 r\u00e0 so\u00e1t "
                            "t\u1ed5ng th\u1ec3 v\u00e0 tra c\u1ee9u t\u00ecnh tr\u1ea1ng "
                            "m\u00e3 s\u1ed1 thu\u1ebf theo h\u1ed3 s\u01a1."
                        ),
                    )
                )
            return recommendations

        for record, _ in records:
            expert = _expert_view(record)
            expert_specializations = [
                item.casefold() for item in (*expert.specializations, *expert.services_offered)
            ]
            reasons = [
                reason
                for group, reason in matching_groups
                if reason
                and any(
                    tag.casefold() in specialization
                    for tag in group
                    for specialization in expert_specializations
                )
            ]
            recommendations.append(
                RecommendedExpertView(expert=expert, match_reason=" ".join(reasons))
            )
        return recommendations

    async def list_experts(
        self,
        keyword: str | None,
        specialization: str | None,
        location: str | None,
        partner_type: str | None,
        page: int,
        page_size: int,
    ) -> ExpertPage:
        records, total = await self.repository.list_experts(
            _clean_text(keyword) if keyword else None,
            _clean_text(specialization) if specialization else None,
            _clean_text(location) if location else None,
            partner_type,
            (page - 1) * page_size,
            page_size,
        )
        return ExpertPage(
            items=[_expert_view(record) for record in records],
            page=page,
            page_size=page_size,
            total=total,
        )

    async def get_expert(self, expert_id: UUID) -> ExpertView:
        record = await self.repository.get_expert(expert_id)
        if record is None:
            raise ApplicationError(404, "Không tìm thấy chuyên gia đang hoạt động.")
        return _expert_view(record)

    async def create_consultation_request(
        self, request: CreateConsultationRequest, user_id: UUID | None
    ) -> ConsultationResponse:
        if await self.repository.get_expert(request.expert_id) is None:
            raise ApplicationError(404, "Không tìm thấy chuyên gia đang hoạt động.")
        if request.assessment_id is not None:
            if user_id is None:
                raise ApplicationError(401, "Vui lòng đăng nhập để liên kết hồ sơ tư vấn.")
            assessment = await self.assessment_repository.get(user_id, request.assessment_id)
            if assessment is None:
                raise ApplicationError(404, "Không tìm thấy hồ sơ tư vấn.")
        else:
            assessment = None

        contact_name = _clean_text(request.contact_name)
        contact_phone = _clean_text(request.contact_phone)
        notes = _clean_text(request.notes)
        if not contact_name or not contact_phone or not notes:
            raise ApplicationError(422, "Vui lòng nhập tên, số điện thoại và nội dung cần tư vấn.")
        data_snapshot = None
        if request.share_data_consent and assessment is not None:
            data_snapshot = json.dumps(
                {
                    "scope": assessment.summary.scope,
                    "answers": dict(assessment.answers),
                    "summary": assessment.summary.model_dump(mode="json"),
                    "checklist": [item.model_dump(mode="json") for item in assessment.checklist],
                },
                ensure_ascii=False,
                separators=(",", ":"),
            )
        record = await self.repository.create_consultation_request(
            expert_id=request.expert_id,
            user_id=user_id,
            assessment_id=request.assessment_id,
            contact_name=contact_name,
            contact_phone=contact_phone,
            contact_email=_clean_text(request.contact_email) if request.contact_email else None,
            business_type=_clean_text(request.business_type) if request.business_type else None,
            consultation_method=request.consultation_method,
            notes=notes,
            service_needed=_clean_text(request.service_needed) if request.service_needed else None,
            share_data_consent=request.share_data_consent,
            data_snapshot=data_snapshot,
        )
        return ConsultationResponse(
            id=record.id,
            expert_id=record.expert_id,
            status=record.status,
            created_at=record.created_at,
        )
