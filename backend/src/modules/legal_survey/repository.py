from src.modules.legal_survey.schemas import SurveyQuestion


class LegalSurveyRepository:
    """Provides the versioned survey definition; answers are not persisted."""

    def get_questions(self) -> list[SurveyQuestion]:
        return [
            SurveyQuestion(
                id="entity_type",
                prompt="Bạn đang hoạt động theo loại hình nào?",
                selection_type="single",
                options=[
                    {"value": "HKD", "label": "Hộ kinh doanh"},
                    {"value": "DN", "label": "Doanh nghiệp"},
                ],
            ),
            SurveyQuestion(
                id="registration_status",
                prompt="Tình trạng đăng ký kinh doanh hiện tại?",
                selection_type="single",
                options=[
                    {"value": "registered", "label": "Đã đăng ký"},
                    {"value": "not_registered", "label": "Chưa đăng ký"},
                    {"value": "unknown", "label": "Không rõ"},
                ],
            ),
            SurveyQuestion(
                id="tax_id_status",
                prompt="Mã số thuế đang ở trạng thái nào?",
                selection_type="single",
                options=[
                    {"value": "active", "label": "Đang hoạt động"},
                    {"value": "inactive", "label": "Ngừng/đóng mã số thuế"},
                    {"value": "unknown", "label": "Không rõ"},
                ],
                show_if={
                    "registration_status": ["registered"],
                    "operating_status": ["currently_active", "never_had_revenue", "unknown"],
                },
            ),
            SurveyQuestion(
                id="operating_status",
                prompt="Tình hình kinh doanh/doanh thu thực tế?",
                selection_type="single",
                options=[
                    {"value": "currently_active", "label": "Hiện đang kinh doanh"},
                    {"value": "never_had_revenue", "label": "Chưa từng phát sinh doanh thu"},
                    {
                        "value": "abandoned_after_operation",
                        "label": "Đã hoạt động, nay bỏ/ngừng không xử lý hồ sơ",
                    },
                    {"value": "unknown", "label": "Không rõ"},
                ],
            ),
            SurveyQuestion(
                id="declaration_status",
                prompt="Các kỳ thuế gần nhất đã được kê khai thế nào?",
                selection_type="single",
                options=[
                    {"value": "filed_all", "label": "Đã nộp đủ"},
                    {"value": "filed_some", "label": "Chỉ nộp một phần"},
                    {"value": "not_filed", "label": "Chưa nộp"},
                    {"value": "unknown", "label": "Không rõ"},
                ],
            ),
            SurveyQuestion(
                id="declaration_matches_reality",
                prompt="Số liệu kê khai có khớp doanh thu thực tế không?",
                selection_type="single",
                options=[
                    {"value": "yes", "label": "Có, khớp"},
                    {"value": "no", "label": "Không khớp"},
                    {"value": "unknown", "label": "Chưa đối chiếu/không rõ"},
                ],
                show_if={
                    "declaration_status": ["filed_all", "filed_some"],
                    "operating_status": [
                        "currently_active",
                        "abandoned_after_operation",
                        "unknown",
                    ],
                },
            ),
            SurveyQuestion(
                id="invoice_status",
                prompt="Hóa đơn điện tử còn vấn đề chưa xử lý không?",
                selection_type="single",
                options=[
                    {"value": "none", "label": "Không phát sinh"},
                    {"value": "resolved", "label": "Có nhưng đã xử lý xong"},
                    {"value": "unresolved", "label": "Còn tồn đọng"},
                    {"value": "unknown", "label": "Không rõ"},
                ],
            ),
            SurveyQuestion(
                id="bank_status",
                prompt="Sao kê tài khoản dùng cho kinh doanh đã đối chiếu với kê khai chưa?",
                selection_type="single",
                options=[
                    {"value": "matches", "label": "Đã đối chiếu, khớp"},
                    {"value": "mismatch", "label": "Có chênh lệch"},
                    {"value": "not_reviewed", "label": "Chưa đối chiếu"},
                ],
                show_if={
                    "declaration_status": ["filed_all", "filed_some"],
                    "operating_status": [
                        "currently_active",
                        "abandoned_after_operation",
                        "unknown",
                    ],
                },
            ),
            SurveyQuestion(
                id="unpaid_obligations",
                prompt="Hiện còn khoản nợ/nghĩa vụ nào chưa xử lý? (Có thể chọn nhiều)",
                selection_type="multiple",
                options=[
                    {"value": "unpaid_tax", "label": "Nợ thuế"},
                    {"value": "unresolved_invoices", "label": "Hóa đơn tồn đọng"},
                    {"value": "unpaid_labour", "label": "Nợ lương/lao động"},
                    {"value": "unpaid_social_security", "label": "Nợ BHXH"},
                    {"value": "other", "label": "Khoản khác"},
                    {"value": "none", "label": "Không có khoản tồn đọng"},
                    {"value": "unknown", "label": "Không rõ"},
                ],
            ),
            SurveyQuestion(
                id="tax_audit_notice",
                prompt="Đã nhận thông báo kiểm tra/yêu cầu giải trình từ cơ quan thuế chưa?",
                selection_type="single",
                options=[
                    {"value": "yes", "label": "Đã nhận"},
                    {"value": "no", "label": "Chưa nhận"},
                    {"value": "unknown", "label": "Không rõ"},
                ],
            ),
            SurveyQuestion(
                id="target_action",
                prompt="Mục tiêu hiện tại của bạn là gì?",
                selection_type="single",
                options=[
                    {"value": "terminate", "label": "Chấm dứt hẳn"},
                    {
                        "value": "convert_to_new_entity",
                        "label": "Chuyển đổi/lập chủ thể kinh doanh mới",
                    },
                    {"value": "suspend", "label": "Tạm ngừng kinh doanh"},
                ],
            ),
            SurveyQuestion(
                id="business_start_period",
                prompt="Hộ kinh doanh/doanh nghiệp bắt đầu đăng ký vào giai đoạn nào?",
                selection_type="single",
                show_if={"operating_status": ["never_had_revenue"]},
                options=[
                    {"value": "before_2012", "label": "Trước năm 2012"},
                    {"value": "2012_2019", "label": "Từ năm 2012 đến 2019"},
                    {"value": "2020_2024", "label": "Từ năm 2020 đến 2024"},
                    {"value": "2025_onward", "label": "Từ năm 2025 trở đi"},
                    {"value": "unknown", "label": "Không rõ"},
                ],
            ),
            SurveyQuestion(
                id="idle_duration",
                prompt="Đã ngừng hoạt động hoặc không kê khai trong khoảng bao lâu?",
                selection_type="single",
                show_if={"operating_status": ["abandoned_after_operation"]},
                options=[
                    {"value": "under_1y", "label": "Dưới 1 năm"},
                    {"value": "1_to_3y", "label": "Từ 1 đến 3 năm"},
                    {"value": "over_3y", "label": "Trên 3 năm"},
                    {"value": "unknown", "label": "Không rõ"},
                ],
            ),
            SurveyQuestion(
                id="has_assets_or_inventory",
                prompt="Doanh nghiệp có tài sản hoặc hàng tồn kho không?",
                selection_type="single",
                show_if={
                    "entity_type": ["DN"],
                    "operating_status": ["never_had_revenue"],
                },
                options=[
                    {"value": "yes", "label": "Có"},
                    {"value": "no", "label": "Không"},
                    {"value": "unknown", "label": "Không rõ"},
                ],
            ),
            SurveyQuestion(
                id="has_employees",
                prompt="Chủ thể có hoặc đã từng có người lao động không?",
                selection_type="single",
                show_if={"registration_status": ["registered"]},
                options=[
                    {"value": "yes", "label": "Có"},
                    {"value": "no", "label": "Không"},
                    {"value": "unknown", "label": "Không rõ"},
                ],
            ),
        ]
