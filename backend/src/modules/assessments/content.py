from src.modules.assessments.schemas import Option, Question, Questionnaire

VERSION = "b2-draft-1"
NOTICE = "Bản tổng hợp câu trả lời và danh mục hồ sơ cần chuẩn bị để trao đổi với chuyên viên."
TRI = [("yes", "Có"), ("no", "Không"), ("unknown", "Chưa biết")]
QUESTION_DATA = [
    (
        "businessType",
        "Bạn đang chuẩn bị hồ sơ cho loại hình nào?",
        [("company", "Doanh nghiệp"), ("household", "Hộ kinh doanh"), ("unknown", "Chưa biết")],
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
