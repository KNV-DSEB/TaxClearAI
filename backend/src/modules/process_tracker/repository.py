from dataclasses import dataclass

from src.modules.process_tracker.schemas import TrackedProcedure


@dataclass(frozen=True)
class DeadlineRule:
    phase: str
    milestone: str
    duration: int | None
    unit: str
    anchor_description: str
    legal_reference: str
    warning_window: int


class ProcessTrackerRepository:
    """Current statutory deadline rules used by the tracker."""

    def get_deadline_rules(self, procedure: TrackedProcedure, phase: str) -> list[DeadlineRule]:
        rules = self._rules_by_procedure().get(procedure, [])
        return [rule for rule in rules if rule.phase == phase]

    @staticmethod
    def _rules_by_procedure() -> dict[TrackedProcedure, list[DeadlineRule]]:
        tax_rules = [
            DeadlineRule(
                phase="TAX_SUBMISSION",
                milestone="Nộp hồ sơ khai thuế cuối cùng (nếu thuộc diện phải nộp)",
                duration=45,
                unit="calendar_days",
                anchor_description="ngày xảy ra sự kiện chấm dứt hoạt động",
                legal_reference="Nghị định 252/2026/NĐ-CP, khoản 5 Điều 10, điểm b",
                warning_window=5,
            ),
            DeadlineRule(
                phase="TAX_FINALIZATION",
                milestone="Nộp hồ sơ khai thuế cuối cùng (nếu thuộc diện phải nộp)",
                duration=45,
                unit="calendar_days",
                anchor_description="ngày xảy ra sự kiện chấm dứt hoạt động",
                legal_reference="Nghị định 252/2026/NĐ-CP, khoản 5 Điều 10, điểm b",
                warning_window=5,
            ),
            DeadlineRule(
                phase="TAX_RESULT",
                milestone="Cơ quan thuế gửi thông báo đang làm thủ tục chấm dứt MST",
                duration=2,
                unit="business_days",
                anchor_description="ngày cơ quan thuế nhận đủ hồ sơ",
                legal_reference="Thông tư 90/2026/TT-BTC, khoản 1 Điều 29, điểm a.1",
                warning_window=2,
            ),
        ]
        return {
            TrackedProcedure.HKD_SUSPENSION: [
                DeadlineRule(
                    phase="SUSPENSION_SUBMISSION",
                    milestone="Nộp thông báo tạm ngừng hoạt động HKD",
                    duration=None,
                    unit="unknown",
                    anchor_description="Chưa xác định căn cứ trong nguồn đã đồng bộ",
                    legal_reference="Chưa xác định căn cứ trong nguồn đã đồng bộ",
                    warning_window=0,
                )
            ],
            TrackedProcedure.COMPANY_SUSPENSION: [
                DeadlineRule(
                    phase="SUSPENSION_SUBMISSION",
                    milestone="Nộp thông báo tạm ngừng hoạt động doanh nghiệp",
                    duration=None,
                    unit="unknown",
                    anchor_description="Chưa xác định căn cứ trong nguồn đã đồng bộ",
                    legal_reference="Chưa xác định căn cứ trong nguồn đã đồng bộ",
                    warning_window=0,
                )
            ],
            TrackedProcedure.HKD_TERMINATION: [
                *tax_rules,
                DeadlineRule(
                    phase="REGISTRATION_SUBMISSION",
                    milestone="Nộp thông báo chấm dứt hoạt động HKD",
                    duration=5,
                    unit="business_days",
                    anchor_description="ngày thanh toán hết các khoản nợ",
                    legal_reference="Nghị định 168/2025/NĐ-CP, khoản 1 Điều 104, điểm b",
                    warning_window=2,
                ),
                DeadlineRule(
                    phase="TAX_CONFIRMATION",
                    milestone="Cơ quan thuế gửi ý kiến xác nhận nghĩa vụ thuế của HKD",
                    duration=2,
                    unit="business_days",
                    anchor_description="ngày cơ quan thuế nhận thông tin từ cơ quan đăng ký cấp xã",
                    legal_reference="Nghị định 168/2025/NĐ-CP, khoản 1 Điều 104, điểm c",
                    warning_window=2,
                ),
                DeadlineRule(
                    phase="REGISTRATION_RESULT",
                    milestone="Cơ quan đăng ký cấp xã cập nhật kết quả chấm dứt HKD",
                    duration=5,
                    unit="business_days",
                    anchor_description="ngày cơ quan đăng ký cấp xã nhận hồ sơ",
                    legal_reference="Nghị định 168/2025/NĐ-CP, khoản 1 Điều 104, điểm c",
                    warning_window=2,
                ),
            ],
            TrackedProcedure.TAX_ID_TERMINATION: tax_rules,
            TrackedProcedure.HKD_NEW_REGISTRATION: [
                DeadlineRule(
                    phase="NEW_ENTITY_RESULT",
                    milestone="Cơ quan đăng ký cấp xã trả kết quả đăng ký HKD mới",
                    duration=3,
                    unit="business_days",
                    anchor_description="ngày cơ quan đăng ký cấp xã nhận hồ sơ",
                    legal_reference="Nghị định 168/2025/NĐ-CP, khoản 3 Điều 99",
                    warning_window=2,
                )
            ],
            TrackedProcedure.COMPANY_DISSOLUTION: [
                DeadlineRule(
                    phase="INITIAL_SUBMISSION",
                    milestone="Nộp nghị quyết/quyết định giải thể và hồ sơ ban đầu",
                    duration=7,
                    unit="business_days",
                    anchor_description="ngày thông qua nghị quyết/quyết định giải thể",
                    legal_reference="Nghị định 168/2025/NĐ-CP, khoản 1 Điều 64",
                    warning_window=2,
                ),
                DeadlineRule(
                    phase="INITIAL_RESULT",
                    milestone="Cơ quan đăng ký kinh doanh đăng thông báo đang giải thể",
                    duration=3,
                    unit="business_days",
                    anchor_description="ngày cơ quan đăng ký kinh doanh nhận hồ sơ ban đầu",
                    legal_reference="Nghị định 168/2025/NĐ-CP, khoản 2 Điều 64",
                    warning_window=2,
                ),
                DeadlineRule(
                    phase="OBLIGATION_SETTLEMENT",
                    milestone="Nộp hồ sơ khai thuế cuối cùng (nếu thuộc diện phải nộp)",
                    duration=45,
                    unit="calendar_days",
                    anchor_description="ngày xảy ra sự kiện chấm dứt hoạt động",
                    legal_reference="Nghị định 252/2026/NĐ-CP, khoản 5 Điều 10, điểm b",
                    warning_window=5,
                ),
                DeadlineRule(
                    phase="FINAL_SUBMISSION",
                    milestone="Nộp hồ sơ đăng ký giải thể cuối cùng",
                    duration=5,
                    unit="business_days",
                    anchor_description="ngày thanh toán hết các khoản nợ",
                    legal_reference="Nghị định 168/2025/NĐ-CP, khoản 3 Điều 64",
                    warning_window=2,
                ),
                DeadlineRule(
                    phase="TAX_CONFIRMATION",
                    milestone="Cơ quan thuế phản hồi tình trạng hoàn thành nghĩa vụ thuế",
                    duration=2,
                    unit="business_days",
                    anchor_description="ngày cơ quan thuế nhận thông tin giải thể",
                    legal_reference="Nghị định 168/2025/NĐ-CP, khoản 5 Điều 64",
                    warning_window=2,
                ),
            ],
        }
