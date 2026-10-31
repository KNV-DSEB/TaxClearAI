import json

from fastapi import HTTPException, status

from src.core.logging import logger
from src.modules.case_brief.schemas import CaseBriefRequest, CaseDiagnosis, CaseSegment
from src.modules.case_brief.service import CaseBriefService
from src.modules.expert_directory.repository import ExpertDirectoryRepository
from src.modules.expert_directory.schemas import (
    ExpertProfile,
    ExpertRequestResponse,
    ExpertType,
)


class ExpertDirectoryService:
    def __init__(self, repository: ExpertDirectoryRepository) -> None:
        self._repository = repository

    def list_verified(
        self,
        segment: CaseSegment | None = None,
        region: str | None = None,
        expert_type: ExpertType | None = None,
    ) -> list[ExpertProfile]:
        experts = [expert for expert in self._repository.list_experts() if expert.verified]
        if segment:
            experts = [expert for expert in experts if segment in expert.segments]
        if region:
            region_filter = region.strip().casefold()
            experts = [
                expert
                for expert in experts
                if any(region_filter in item.casefold() for item in expert.regions)
            ]
        if expert_type:
            experts = [expert for expert in experts if expert.expert_type == expert_type]
        return experts

    def get_verified(self, expert_id: str) -> ExpertProfile:
        expert = next(
            (
                item
                for item in self._repository.list_experts()
                if item.id == expert_id and item.verified
            ),
            None,
        )
        if expert is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy chuyên gia đã xác thực.",
            )
        return expert

    def prepare_request(
        self, expert_id: str, case_brief: CaseBriefRequest
    ) -> ExpertRequestResponse:
        expert = self.get_verified(expert_id)
        if case_brief.diagnosis.segment not in expert.segments:
            raise HTTPException(
                status_code=422,
                detail="Chuyên gia này chưa được khai báo hỗ trợ nhóm hồ sơ đã chọn.",
            )
        sanitized = self._redact_case_brief(case_brief)
        logger.info(
            "expert_directory_request_prepared",
            expert_id=expert.id,
            case_brief=json.dumps(sanitized.model_dump(mode="json"), ensure_ascii=False)[:500],
        )
        return ExpertRequestResponse(
            expert_id=expert.id,
            case_brief=sanitized,
            request_status="prepared_not_sent",
            message=(
                "Yêu cầu đã được lọc định danh. Hệ thống chưa gửi hoặc lưu yêu cầu; "
                "hãy chuyển bản này qua kênh bảo mật sau khi kiểm tra."
            ),
            illustrative=expert.illustrative,
        )

    @staticmethod
    def _redact_case_brief(case_brief: CaseBriefRequest) -> CaseBriefRequest:
        diagnosis = case_brief.diagnosis
        return CaseBriefRequest(
            diagnosis=CaseDiagnosis(
                segment=diagnosis.segment,
                entity_type=CaseBriefService._sanitize(diagnosis.entity_type),
                procedure=CaseBriefService._sanitize(diagnosis.procedure),
                target_action=CaseBriefService._sanitize(diagnosis.target_action),
                risk_flags=[CaseBriefService._sanitize(item) for item in diagnosis.risk_flags],
                blockers=[CaseBriefService._sanitize(item) for item in diagnosis.blockers],
                notes=[CaseBriefService._sanitize(item) for item in diagnosis.notes],
            ),
            user_questions=[CaseBriefService._sanitize(item) for item in case_brief.user_questions],
        )
