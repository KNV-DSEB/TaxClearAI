from collections.abc import Iterable

from src.core.privacy import redact_sensitive_data
from src.modules.case_brief.repository import CaseBriefRepository
from src.modules.case_brief.schemas import (
    CaseBriefRequest,
    CaseBriefResponse,
    EstimatedCost,
    ServiceFee,
)


class CaseBriefService:
    def __init__(self, repository: CaseBriefRepository) -> None:
        self._repository = repository

    def generate(self, request: CaseBriefRequest) -> CaseBriefResponse:
        diagnosis = request.diagnosis
        blockers = self._deduplicate(
            self._sanitize(item)
            for item in [*diagnosis.blockers, *diagnosis.risk_flags, *diagnosis.notes]
            if item.strip()
        )
        scope = self._scope(diagnosis.segment.value, blockers)
        questions = self._deduplicate(
            [
                *(self._interview_questions(diagnosis.segment.value, blockers)),
                *(self._sanitize(item) for item in request.user_questions if item.strip()),
            ]
        )
        cost = self._repository.get_cost_reference(diagnosis.segment)
        return CaseBriefResponse(
            case_classification=(
                f"{diagnosis.segment.value} — {self._sanitize(diagnosis.procedure)}"
            ),
            target_group=(
                f"{self._sanitize(diagnosis.entity_type)}; mục tiêu: "
                f"{self._sanitize(diagnosis.target_action)}"
            ),
            main_blockers=blockers,
            scope_of_work=scope,
            expert_interview_questions=questions,
            estimated_cost=EstimatedCost(
                minimum=cost.minimum,
                maximum=cost.maximum,
                reference_basis=cost.basis,
                complexity_note=cost.complexity_note,
                sources=list(cost.sources),
                service_fee=ServiceFee(
                    minimum=cost.service_fee_minimum,
                    maximum=cost.service_fee_maximum,
                    note=cost.service_fee_note,
                ),
                state_payments_note=cost.state_payments_note,
                quote_requires_survey=cost.quote_requires_survey,
            ),
            privacy_note=(
                "Brief đã lọc số điện thoại, email, mã số thuế và chuỗi định danh "
                "giống số giấy tờ. "
                "Chỉ chuyển bản tóm tắt này cho chuyên gia đã xác thực qua kênh bảo mật; không "
                "gửi bản gốc hoặc dữ liệu định danh nhạy cảm ở giai đoạn này."
            ),
        )

    @staticmethod
    def _scope(segment: str, blockers: list[str]) -> dict[str, list[str]]:
        expert_tasks = [
            "Đối chiếu tình trạng đăng ký, mã số thuế và nghĩa vụ kê khai trên hệ thống "
            "hoặc với cơ quan có thẩm quyền.",
            "Xác định thứ tự thủ tục, biểu mẫu và đầu mối tiếp nhận phù hợp với hồ sơ thực tế.",
            "Báo rõ phạm vi đại diện, sản phẩm bàn giao, thời gian dự kiến và khoản phí "
            "chưa bao gồm.",
        ]
        client_tasks = [
            "Cung cấp timeline hoạt động và danh mục tình trạng giấy tờ; chưa gửi bản gốc "
            "hoặc ảnh giấy tờ nhạy cảm.",
            "Tự rà soát, lập bảng kê các kỳ đã/chưa kê khai, hóa đơn, tài khoản dùng cho "
            "kinh doanh và công nợ.",
            "Xác nhận mục tiêu (chấm dứt hay chuyển đổi) và người có thẩm quyền ký/ủy quyền.",
        ]
        if segment in {"A1", "A2", "A3"}:
            expert_tasks.append("Rà soát nghĩa vụ HKD, hồ sơ thuế và điều kiện chấm dứt hoạt động.")
        if segment == "A3" or any(
            "lệch" in item.lower() or "mismatch" in item.lower() for item in blockers
        ):
            expert_tasks.append(
                "Đối soát doanh thu kê khai với sao kê, hóa đơn và dữ liệu bán hàng; lập "
                "danh sách chênh lệch cần giải trình."
            )
            client_tasks.append(
                "Chuẩn bị bảng đối chiếu số liệu đã ẩn danh; chỉ cung cấp chứng từ qua kênh "
                "an toàn theo yêu cầu chuyên gia."
            )
        if segment == "B2":
            expert_tasks.extend(
                [
                    "Khoanh vùng kỳ khai thiếu, nghĩa vụ thuế và khả năng cần quyết toán/bổ sung.",
                    "Rà soát hóa đơn còn tồn, lao động/BHXH, chủ nợ và tài sản trước khi "
                    "chốt lộ trình giải thể.",
                ]
            )
            client_tasks.append(
                "Lập danh mục hóa đơn, nhân sự/BHXH, tài sản và chủ nợ; không tải hồ sơ "
                "gốc lên ứng dụng."
            )
        return {"expert_to_do": expert_tasks, "client_to_prepare": client_tasks}

    @staticmethod
    def _interview_questions(segment: str, blockers: list[str]) -> list[str]:
        questions = [
            "Anh/chị có kinh nghiệm xử lý hồ sơ thuộc phân khúc này tại địa phương của tôi không?",
            "Phạm vi phí gồm những việc nào, và khoản nào như thuế, tiền phạt hoặc lệ phí "
            "nhà nước bị loại trừ?",
            "Tài liệu đầu vào tối thiểu nào cần cung cấp, và có thể bắt đầu bằng danh mục "
            "khai báo đã ẩn danh không?",
            "Ai trực tiếp xử lý hồ sơ, cách cập nhật tiến độ và sản phẩm bàn giao "
            "sau mỗi giai đoạn là gì?",
        ]
        if segment == "A3" or any(
            "lệch" in item.lower() or "mismatch" in item.lower() for item in blockers
        ):
            questions.append(
                "Chuyên gia sẽ đối soát chênh lệch doanh thu/sao kê như thế nào và cần "
                "khách hàng xác nhận số liệu nào?"
            )
        if segment == "B2":
            questions.extend(
                [
                    "Phí xử lý từng phần tờ khai thiếu, hóa đơn tồn, nợ thuế và lao động/BHXH "
                    "được tách ra sao?",
                    "Những tình huống nào có thể làm phát sinh yêu cầu giải trình hoặc kéo "
                    "dài thời gian xử lý?",
                ]
            )
        return questions

    @classmethod
    def _sanitize(cls, value: str) -> str:
        return " ".join(redact_sensitive_data(value).split())

    @staticmethod
    def _deduplicate(items: Iterable[str]) -> list[str]:
        result: list[str] = []
        seen: set[str] = set()
        for item in items:
            if item and item not in seen:
                seen.add(item)
                result.append(item)
        return result
