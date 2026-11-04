from src.modules.assessments.schemas import Option, Question, Questionnaire

VERSION = "groups-draft-2"
NOTICE = "Bản tổng hợp câu trả lời và danh mục hồ sơ cần chuẩn bị để trao đổi với chuyên viên."
CHECKLIST_NOTE = "Mục gợi ý để khảo sát; chuyên viên cần xác nhận có áp dụng cho hồ sơ của bạn."
TRI = [("yes", "Có"), ("no", "Không"), ("unknown", "Chưa biết")]
QUESTION_DATA = [
    (
        "businessType",
        "Bạn đang chuẩn bị hồ sơ cho loại hình nào?",
        [("company", "Doanh nghiệp"), ("household", "Hộ kinh doanh"), ("unknown", "Chưa biết")],
    ),
    ("registrationStatus", "Hộ kinh doanh đã đăng ký kinh doanh chưa?", TRI),
    (
        "householdGoal",
        "Mục tiêu đối với hộ kinh doanh là gì?",
        [
            ("new_household", "Chấm dứt hộ hiện tại để mở hộ mới"),
            ("stop", "Chấm dứt hẳn"),
            ("continue", "Điều chỉnh để tiếp tục hoạt động"),
            ("unknown", "Chưa xác định"),
        ],
    ),
    (
        "goal",
        "Bạn muốn thực hiện việc gì?",
        [
            ("dissolution", "Chuẩn bị giải thể doanh nghiệp"),
            ("other", "Nhu cầu khác"),
            ("unknown", "Chưa xác định"),
        ],
    ),
    ("establishedYear", "Doanh nghiệp được thành lập năm nào?", []),
    ("revenueStatus", "Doanh nghiệp đã từng phát sinh doanh thu chưa?", TRI),
    ("revenueStartedYear", "Năm bắt đầu phát sinh doanh thu?", []),
    (
        "filingStatus",
        "Bạn biết tình trạng kê khai hiện tại không?",
        [
            ("complete", "Theo thông tin tôi có: đã kê khai đầy đủ"),
            ("incomplete", "Có kỳ chưa kê khai"),
            ("never", "Chưa từng kê khai"),
            ("unknown", "Chưa biết"),
        ],
    ),
    ("discrepancyStatus", "Có chênh lệch hoặc rủi ro sai lệch kê khai cần rà soát không?", TRI),
    (
        "recordsStatus",
        "Hồ sơ và chứng từ hiện còn ở mức nào?",
        [
            ("complete", "Còn đầy đủ theo thông tin tôi có"),
            ("partial", "Chỉ còn một phần"),
            ("missing", "Chưa tìm thấy"),
            ("unknown", "Chưa biết"),
        ],
    ),
    ("taxNoticeStatus", "Bạn có nhận thông báo nghĩa vụ thuế hoặc yêu cầu giải trình?", TRI),
    (
        "laborInsuranceStatus",
        "Doanh nghiệp còn vấn đề lao động hoặc bảo hiểm cần rà soát?",
        [
            ("none", "Theo thông tin tôi có: không còn"),
            ("obligations", "Có việc cần rà soát"),
            ("unknown", "Chưa biết"),
        ],
    ),
    ("assetsInventoryStatus", "Doanh nghiệp còn tài sản hoặc hàng tồn kho?", TRI),
    ("receivablesPayablesStatus", "Doanh nghiệp còn khoản phải thu hoặc phải trả?", TRI),
]

DOCUMENTS = [
    ("registration", "Giấy đăng ký kinh doanh"),
    ("representative_identity", "Căn cước người đại diện — chỉ kiểm tra tình trạng có/thiếu"),
    ("ownership", "Danh sách cổ đông và chủ sở hữu hưởng lợi"),
    ("charter", "Điều lệ công ty"),
    ("finance_policy", "Quy chế tài chính nội bộ"),
    ("personal_statements", "Sao kê tài khoản chủ sở hữu/giám đốc liên quan kinh doanh"),
    ("purchase_invoices", "Hóa đơn đầu vào, hợp đồng và biên bản giao nhận"),
    ("purchase_schedules", "Bảng kê mua hàng theo kỳ áp dụng"),
    ("sales_invoices", "Hóa đơn đầu ra, hợp đồng và biên bản giao nhận"),
    ("company_statements", "Sổ phụ ngân hàng doanh nghiệp"),
    ("general_ledgers", "Sổ tài khoản loại 1–9"),
    ("detailed_ledgers", "Sổ chi tiết công nợ và các khoản vay"),
    ("inventory", "Sổ kho, thẻ kho và bảng nhập–xuất–tồn"),
    ("balances", "Bảng tổng hợp công nợ và tài khoản ngân hàng"),
    ("vat_returns", "Tờ khai thuế GTGT"),
    ("financial_statements", "Báo cáo tài chính"),
    ("corporate_returns", "Tờ khai quyết toán thuế TNDN"),
    ("personal_returns", "Tờ khai quyết toán thuế TNCN"),
    ("invoice_schedules", "Bảng kê mua/bán theo kỳ, tổng hợp theo năm"),
]
DOCUMENTS_B2 = DOCUMENTS

DOCUMENTS_A1 = [
    ("actual_records", "Chứng từ doanh thu/chi phí thực tế"),
    ("tax_explanation", "Văn bản giải trình với Chi cục Thuế — cần xác nhận cơ quan tiếp nhận"),
    ("registration_or_termination", "Hồ sơ đăng ký mới hoặc chấm dứt"),
]
DOCUMENTS_A2 = [
    ("household_registration", "Giấy chứng nhận đăng ký hộ kinh doanh"),
    (
        "tax_id_termination",
        "Đơn đề nghị chấm dứt hiệu lực MST mẫu 24/ĐK-TCT — cần chuyên viên xác nhận",
    ),
    ("missing_tax_returns", "Tờ khai thuế môn bài và thuế khoán các kỳ còn thiếu"),
    (
        "household_termination_notice",
        "Thông báo chấm dứt hoạt động hộ kinh doanh gửi UBND quận/huyện — cần xác nhận",
    ),
    (
        "tax_obligation_confirmation",
        "Giấy xác nhận hoàn thành nghĩa vụ thuế — cần chuyên viên xác nhận",
    ),
]
DOCUMENTS_A3 = [
    ("business_bank_statements", "Sao kê tài khoản kinh doanh"),
    ("revenue_invoice_schedule", "Bảng kê hóa đơn/doanh thu thực tế"),
    ("submitted_tax_returns", "Các tờ khai thuế đã nộp"),
    ("discrepancy_explanation", "Tài liệu giải trình chênh lệch số liệu"),
]
DOCUMENTS_B1 = [
    ("dissolution_decision", "Quyết định giải thể"),
    ("meeting_minutes", "Biên bản họp về việc giải thể (nếu áp dụng)"),
    ("no_revenue_evidence", "Báo cáo xác nhận chưa phát sinh hóa đơn và doanh thu"),
    ("tax_id_closure", "Đơn đề nghị đóng mã số thuế"),
    ("business_registry_notice", "Thông báo giải thể gửi Phòng Đăng ký kinh doanh"),
]


def get_questionnaire() -> Questionnaire:
    questions = [
        Question(
            id=key,
            label=label,
            kind="choice" if options else "year",
            options=[Option(value=value, label=text) for value, text in options],
        )
        for key, label, options in QUESTION_DATA
    ]
    return Questionnaire(version=VERSION, questions=questions)
