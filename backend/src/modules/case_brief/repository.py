from dataclasses import dataclass

from src.modules.case_brief.schemas import CaseSegment


@dataclass(frozen=True)
class CostReference:
    minimum: int | None
    maximum: int | None
    basis: str
    complexity_note: str
    sources: tuple[str, ...]
    service_fee_minimum: int | None
    service_fee_maximum: int | None
    service_fee_note: str
    state_payments_note: str
    quote_requires_survey: bool = False


_BAN_CO_VAN_SOURCE = ("Ban cố vấn dự án (báo giá tham khảo)",)

# Cập nhật ngày 2026-10-31; cần ban cố vấn cập nhật các mức tham khảo này.
_COST_REFERENCES: dict[CaseSegment, CostReference] = {
    CaseSegment.A1: CostReference(
        minimum=5_000_000,
        maximum=None,
        basis="Phí dịch vụ tham khảo cho HKD, không gồm khoản nộp ngân sách.",
        complexity_note=(
            "Phí làm việc với cơ quan thuế và phòng chuyên môn từ 5.000.000 VND trở lên tùy "
            "lượng hồ sơ; không có trần tham khảo. Cần ban cố vấn cập nhật."
        ),
        sources=_BAN_CO_VAN_SOURCE,
        service_fee_minimum=5_000_000,
        service_fee_maximum=None,
        service_fee_note=(
            "Phí dịch vụ làm việc với cơ quan thuế và phòng chuyên môn từ 5.000.000 VND trở lên "
            "tùy lượng hồ sơ; không có trần tham khảo."
        ),
        state_payments_note=(
            "Tiền thuế, tiền phạt và khoản nộp ngân sách khác phụ thuộc hồ sơ thực tế; hệ thống "
            "không ước tính các khoản này."
        ),
    ),
    CaseSegment.A2: CostReference(
        minimum=5_000_000,
        maximum=None,
        basis="Phí dịch vụ tham khảo cho HKD, không gồm khoản nộp ngân sách.",
        complexity_note=(
            "Phí làm việc với cơ quan thuế và phòng chuyên môn từ 5.000.000 VND trở lên tùy "
            "lượng hồ sơ; không có trần tham khảo. Cần ban cố vấn cập nhật."
        ),
        sources=_BAN_CO_VAN_SOURCE,
        service_fee_minimum=5_000_000,
        service_fee_maximum=None,
        service_fee_note=(
            "Phí dịch vụ làm việc với cơ quan thuế và phòng chuyên môn từ 5.000.000 VND trở lên "
            "tùy lượng hồ sơ; không có trần tham khảo."
        ),
        state_payments_note=(
            "Tiền thuế, tiền phạt và khoản nộp ngân sách khác phụ thuộc hồ sơ thực tế; hệ thống "
            "không ước tính các khoản này."
        ),
    ),
    CaseSegment.A3: CostReference(
        minimum=5_000_000,
        maximum=None,
        basis="Phí dịch vụ tham khảo cho HKD, không gồm khoản nộp ngân sách.",
        complexity_note=(
            "Phí làm việc với cơ quan thuế và phòng chuyên môn từ 5.000.000 VND trở lên tùy "
            "lượng hồ sơ; không có trần tham khảo. Cần ban cố vấn cập nhật."
        ),
        sources=_BAN_CO_VAN_SOURCE,
        service_fee_minimum=5_000_000,
        service_fee_maximum=None,
        service_fee_note=(
            "Phí dịch vụ làm việc với cơ quan thuế và phòng chuyên môn từ 5.000.000 VND trở lên "
            "tùy lượng hồ sơ; không có trần tham khảo."
        ),
        state_payments_note=(
            "Tiền thuế, tiền phạt và khoản nộp ngân sách khác phụ thuộc hồ sơ thực tế; hệ thống "
            "không ước tính các khoản này."
        ),
    ),
    CaseSegment.B1: CostReference(
        minimum=11_500_000,
        maximum=19_500_000,
        basis=(
            "Phí dịch vụ tham khảo, gồm phí làm việc với Sở và phí dịch vụ làm việc với cơ quan "
            "thuế; không gồm tiền phạt nộp nhà nước."
        ),
        complexity_note=(
            "Phí làm việc với Sở: 1.500.000–4.500.000 VND; phí dịch vụ làm việc với cơ quan "
            "thuế: 10.000.000–15.000.000 VND. Thời gian xử lý tham khảo 15–45 ngày. Các số "
            "này là tham khảo của ban cố vấn, không phải báo giá cho hồ sơ cụ thể. Cần ban cố "
            "vấn cập nhật."
        ),
        sources=_BAN_CO_VAN_SOURCE,
        service_fee_minimum=11_500_000,
        service_fee_maximum=19_500_000,
        service_fee_note=(
            "Tổng phí dịch vụ được tính từ hai hạng mục tham khảo: làm việc với Sở 1.500.000–"
            "4.500.000 VND và dịch vụ làm việc với cơ quan thuế 10.000.000–15.000.000 VND; "
            "chưa gồm tiền phạt nộp nhà nước."
        ),
        state_payments_note=(
            "Tiền thuế, tiền phạt và khoản nộp ngân sách không do hệ thống ước tính cho hồ sơ "
            "cụ thể. Ban cố vấn cung cấp mức tổng tham khảo gồm cả tiền nộp phạt là 30.000.000–"
            "80.000.000 VND; có trường hợp tới 150.000.000 VND. Đây không phải số tiền phải "
            "nộp của hồ sơ người dùng."
        ),
    ),
    CaseSegment.B2: CostReference(
        minimum=None,
        maximum=None,
        basis="Không báo giá trước; cần khảo sát hồ sơ thực tế.",
        complexity_note=(
            "Chưa thể xác định phí dịch vụ nếu chưa khảo sát hồ sơ thực tế. "
            "Cần ban cố vấn cập nhật."
        ),
        sources=_BAN_CO_VAN_SOURCE,
        service_fee_minimum=None,
        service_fee_maximum=None,
        service_fee_note="Không báo giá trước; cần khảo sát hồ sơ thực tế.",
        state_payments_note=(
            "Chi phí nộp ngân sách có thể lên tới hàng tỷ đồng tùy truy thu và phạt thực tế. "
            "Hệ thống không ước tính tiền thuế hoặc tiền phạt cho hồ sơ cụ thể."
        ),
        quote_requires_survey=True,
    ),
}


class CaseBriefRepository:
    """Stores project-advisor fee references separately from state payments."""

    def get_cost_reference(self, segment: CaseSegment) -> CostReference:
        return _COST_REFERENCES[segment]
