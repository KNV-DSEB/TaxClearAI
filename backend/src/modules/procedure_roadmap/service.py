from src.modules.document_checklist.repository import DocumentChecklistRepository
from src.modules.document_checklist.schemas import Procedure
from src.modules.document_checklist.schemas import Segment as ChecklistSegment
from src.modules.procedure_roadmap.repository import ProcedureRoadmapRepository
from src.modules.procedure_roadmap.schemas import (
    ProcedureCompareRequest,
    ProcedureCompareResponse,
    ProcedureComparisonRow,
    RoadmapRequest,
    RoadmapResponse,
    Segment,
    TargetAction,
)


class ProcedureRoadmapService:
    def __init__(
        self,
        roadmap_repository: ProcedureRoadmapRepository,
        checklist_repository: DocumentChecklistRepository | None = None,
    ) -> None:
        self._roadmap_repository = roadmap_repository
        self._checklist_repository = checklist_repository or DocumentChecklistRepository()

    def create_roadmap(self, request: RoadmapRequest) -> RoadmapResponse:
        is_household = request.segment in {Segment.A1, Segment.A2, Segment.A3}
        if request.target_action == TargetAction.SUSPEND:
            subject = "Hộ kinh doanh" if is_household else "Doanh nghiệp"
            title = f"Quy trình tạm ngừng kinh doanh {subject}"
        elif is_household:
            title = (
                "Quy trình chấm dứt hoạt động Hộ kinh doanh"
                if request.target_action == TargetAction.TERMINATE
                else "Quy trình chấm dứt hộ cũ và đăng ký hộ kinh doanh mới"
            )
        elif request.target_action == TargetAction.TERMINATE:
            title = "Quy trình giải thể doanh nghiệp"
        else:
            title = "Quy trình chuyển đổi loại hình doanh nghiệp"

        steps = self._roadmap_repository.get_steps(request.segment, request.target_action)
        for step_order, step in enumerate(steps, start=1):
            step.step_order = step_order

        return RoadmapResponse(
            segment=request.segment,
            roadmap_title=title,
            steps=steps,
            needs_expert=request.segment in {Segment.A3, Segment.B2},
        )

    def compare(self, request: ProcedureCompareRequest) -> ProcedureCompareResponse:
        segment = Segment(request.segment.value)
        dissolution_steps = self._roadmap_repository.get_steps(segment, TargetAction.TERMINATE)
        conversion_steps = self._roadmap_repository.get_steps(
            segment, TargetAction.CONVERT_TO_NEW_ENTITY
        )
        checklist_segment = ChecklistSegment(segment.value)
        dissolution_documents = self._checklist_repository.get_documents(
            checklist_segment, Procedure.TERMINATE
        )
        conversion_documents = self._checklist_repository.get_documents(
            checklist_segment, Procedure.CONVERT_TO_NEW_ENTITY
        )
        dissolution_submission = next(
            (step for step in dissolution_steps if "SUBMISSION" in step.phase),
            dissolution_steps[-1],
        )
        conversion_submission = next(
            (step for step in conversion_steps if "SUBMISSION" in step.phase),
            conversion_steps[-1],
        )
        complex_factors = (
            request.segment == "B2"
            or request.has_multiple_members
            or request.has_large_capital_contribution
            or request.has_dispute
            or request.has_outstanding_items
        )
        expert_note = (
            "Cần chuyên gia rà soát do có tồn đọng hoặc yếu tố thành viên, vốn góp hay tranh chấp."
            if complex_factors
            else "Cân nhắc chuyên gia nếu phát sinh nội dung chưa rõ hoặc hồ sơ cần xác minh."
        )
        return ProcedureCompareResponse(
            segment=request.segment,
            rows=[
                ProcedureComparisonRow(
                    criterion="Trình tự",
                    dissolution=(
                        "Thực hiện lộ trình giải thể, xử lý các nghĩa vụ rồi nộp hồ sơ kết thúc."
                    ),
                    transfer_or_conversion=(
                        "Tham khảo lộ trình chuyển đổi hiện có; chuyển nhượng cần rà soát riêng "
                        "theo thỏa thuận và tình trạng doanh nghiệp."
                    ),
                ),
                ProcedureComparisonRow(
                    criterion="Hồ sơ chính",
                    dissolution="; ".join(document.doc_name for document in dissolution_documents),
                    transfer_or_conversion="; ".join(
                        document.doc_name for document in conversion_documents
                    ),
                ),
                ProcedureComparisonRow(
                    criterion="Cơ quan tiếp nhận",
                    dissolution=dissolution_submission.agency,
                    transfer_or_conversion=conversion_submission.agency,
                ),
                ProcedureComparisonRow(
                    criterion="Nghĩa vụ",
                    dissolution=(
                        "Rà soát và hoàn tất nghĩa vụ liên quan trước khi xác nhận kết thúc; "
                        "không mặc định các khoản tồn được xóa."
                    ),
                    transfer_or_conversion=(
                        "Nghĩa vụ có thể được kế thừa theo phương án chuyển đổi/chuyển nhượng; "
                        "cần xác minh theo căn cứ và thỏa thuận áp dụng."
                    ),
                ),
                ProcedureComparisonRow(
                    criterion="Khi nào cần chuyên gia",
                    dissolution=expert_note,
                    transfer_or_conversion=expert_note,
                ),
            ],
            recommendation_boundary=(
                "Hệ thống chỉ so sánh thông tin định tính từ lộ trình và checklist hiện có; "
                "không khuyến nghị chọn hướng nào."
            ),
        )
