from typing import Literal

from src.modules.assessments.schemas import Option, Question, Questionnaire

VERSION = "groups-draft-3"
NOTICE = "Bản tổng hợp câu trả lời và danh mục hồ sơ cần chuẩn bị để trao đổi với chuyên viên."
CHECKLIST_NOTE = "Mục gợi ý để khảo sát; chuyên viên cần xác nhận có áp dụng cho hồ sơ của bạn."
YES_NO = [("yes", "Có"), ("no", "Không")]
# Đáp án nghĩa là "chưa rõ": đưa vào danh sách thông tin chưa biết của bản tổng hợp
UNKNOWN_VALUES = {"unknown", "unknown_location", "unclear", "unreconciled"}
NO_IDENTIFIER_HINT = "Không nhập tên, số điện thoại, mã số thuế hay địa chỉ cụ thể."

COMPANY = {"businessType": ["company"]}
HOUSEHOLD = {"businessType": ["household"]}
DISSOLUTION = {"procedure": ["dissolution"]}
# Phạm vi có danh mục giấy tờ; các phạm vi khác chỉ ghi nhận và chuyển cho chuyên viên
IN_SCOPE = {"a1", "a2", "a3", "b1", "b2", "household"}


def choice(
    id: str,
    label: str,
    options: list[tuple[str, str]],
    show_if: dict[str, list[str]] | None = None,
) -> Question:
    return Question(
        id=id,
        label=label,
        kind="choice",
        options=[Option(value=value, label=text) for value, text in options],
        show_if=show_if,
    )


def fill_in(
    id: str,
    label: str,
    kind: Literal["year", "text", "number"],
    show_if: dict[str, list[str]] | None = None,
    required: bool = False,
    help: str | None = None,
    unit: str | None = None,
) -> Question:
    return Question(
        id=id, label=label, kind=kind, required=required, show_if=show_if, help=help, unit=unit
    )


# Bộ câu hỏi chuẩn hóa do trưởng nhóm cung cấp ngày 06/11/2026.
# Các ô tự điền chỉ nhận tỉnh/thành phố, không nhận mã số doanh nghiệp hay địa chỉ cụ thể.
QUESTIONS: list[Question] = [
    choice(
        "businessType",
        "Bạn đang chuẩn bị hồ sơ cho loại hình nào?",
        [("company", "Doanh nghiệp"), ("household", "Hộ kinh doanh")],
    ),
    choice(
        "procedure",
        "Bạn muốn thực hiện thủ tục nào?",
        [
            ("dissolution", "Giải thể hoặc chấm dứt hoạt động"),
            ("suspension", "Tạm ngừng kinh doanh"),
            ("conversion", "Chuyển đổi loại hình kinh doanh"),
        ],
    ),
    choice(
        "operatingStatus",
        "Hiện tại cơ sở kinh doanh của bạn đang ở trạng thái nào?",
        [
            ("active", "Vẫn đang hoạt động"),
            ("stopped_not_started", "Đã ngừng hoạt động nhưng chưa làm thủ tục"),
            ("stopped_preparing", "Đã ngừng và đang chuẩn bị hồ sơ"),
            ("forced", "Bị yêu cầu hoặc buộc phải chấm dứt"),
        ],
    ),
    choice(
        "sector",
        "Lĩnh vực kinh doanh của bạn là gì?",
        [
            ("trade", "Thương mại, bán buôn, bán lẻ"),
            ("hospitality", "Ăn uống, lưu trú hoặc dịch vụ tiêu dùng"),
            ("manufacturing", "Sản xuất gia công, chế biến"),
            ("services", "Công nghệ, tư vấn hoặc dịch vụ chuyên môn"),
            ("other", "Lĩnh vực khác"),
        ],
    ),
    fill_in(
        "sectorOther",
        "Lĩnh vực khác của bạn là gì?",
        "text",
        show_if={"sector": ["other"]},
        required=True,
        help="Điền ngắn gọn, ví dụ: vận tải, giáo dục.",
    ),
    fill_in("establishedYear", "Cơ sở kinh doanh được thành lập vào năm nào?", "year"),
    choice(
        "hasRevenue",
        "Trong thời gian gần đây, bạn có phát sinh doanh thu không?",
        [("yes", "Có phát sinh doanh thu"), ("no", "Không phát sinh doanh thu")],
    ),
    fill_in(
        "lastRevenue",
        "Giao dịch tạo doanh thu gần đây nhất phát sinh khi nào?",
        "text",
        show_if={"hasRevenue": ["yes"]},
        help="Ví dụ: tháng 3/2024. Bỏ trống nếu chưa nhớ.",
    ),
    choice(
        "hasCosts",
        "Bạn có phát sinh chi phí hay giao dịch mua vào không?",
        [("yes", "Có phát sinh chi phí"), ("no", "Không phát sinh chi phí")],
    ),
    choice(
        "recordsAccess",
        "Bạn có thể truy xuất hồ sơ không?",
        [
            ("complete", "Có đầy đủ hồ sơ dữ liệu"),
            ("partial", "Chỉ có một phần hồ sơ"),
            ("none", "Không truy xuất được hồ sơ"),
            ("unknown_location", "Chưa biết hồ sơ đang được lưu ở đâu"),
        ],
    ),
    # ---- Hộ kinh doanh
    fill_in(
        "hhProvince",
        "Hộ kinh doanh đăng ký tại tỉnh, thành phố nào?",
        "text",
        show_if=HOUSEHOLD,
        required=True,
        help="Chỉ cần tỉnh hoặc thành phố. " + NO_IDENTIFIER_HINT,
    ),
    choice(
        "hhLocations",
        "Hộ kinh doanh hiện có bao nhiêu địa điểm kinh doanh?",
        [
            ("one", "Một địa điểm"),
            ("many", "Nhiều địa điểm"),
            ("none", "Không còn địa điểm hoạt động"),
        ],
        HOUSEHOLD,
    ),
    choice(
        "hhConditional",
        "Hộ kinh doanh có ngành nghề kinh doanh có điều kiện hoặc giấy phép chuyên ngành không?",
        YES_NO,
        HOUSEHOLD,
    ),
    choice(
        "hhTaxObligation",
        "Hộ kinh doanh còn nghĩa vụ khai, nộp hoặc quyết toán thuế nào chưa xác định không?",
        [("yes", "Có"), ("no", "Không có")],
        HOUSEHOLD,
    ),
    choice(
        "hhInvoiceSystem",
        "Hộ kinh doanh có sử dụng hóa đơn hoặc hệ thống bán hàng không?",
        [
            ("einvoice", "Có hóa đơn điện tử"),
            ("pos", "Có phần mềm hoặc máy POS"),
            ("inaccessible", "Có nhưng không truy cập được dữ liệu"),
            ("none", "Không sử dụng"),
        ],
        HOUSEHOLD,
    ),
    choice(
        "hhEmployees",
        "Hộ kinh doanh có thuê người làm việc không?",
        [
            ("unresolved", "Có người chưa giải quyết xong quyền lợi"),
            ("resolved", "Đã giải quyết đầy đủ"),
            ("none", "Không thuê người"),
        ],
        HOUSEHOLD,
    ),
    fill_in(
        "hhRevenueEstimate",
        "Doanh thu của hộ kinh doanh trong kỳ gần nhất ước tính khoảng bao nhiêu?",
        "number",
        show_if=HOUSEHOLD,
        unit="đồng",
        help="Điền số ước tính, bỏ trống nếu chưa biết.",
    ),
    # ---- Doanh nghiệp
    choice(
        "dnType",
        "Loại hình doanh nghiệp là gì?",
        [
            ("sole", "Doanh nghiệp tư nhân"),
            ("llc1", "Công ty TNHH một thành viên"),
            ("llc2", "Công ty TNHH hai thành viên trở lên"),
            ("jsc", "Công ty cổ phần"),
            ("partnership", "Công ty hợp danh"),
        ],
        COMPANY,
    ),
    fill_in(
        "dnRegistry",
        "Cơ quan đăng ký kinh doanh nơi đặt trụ sở thuộc tỉnh, thành phố nào?",
        "text",
        show_if=COMPANY,
        required=True,
        help="Chỉ cần tỉnh hoặc thành phố; không nhập mã số doanh nghiệp. " + NO_IDENTIFIER_HINT,
    ),
    fill_in(
        "dnApprover",
        "Ai có thẩm quyền thông qua việc giải thể?",
        "text",
        show_if={**COMPANY, **DISSOLUTION},
        help="Điền theo hiểu biết của bạn, bỏ trống nếu chưa rõ. Chuyên viên sẽ xác nhận.",
    ),
    choice(
        "dnDecision",
        "Doanh nghiệp đã có quyết định hoặc nghị quyết giải thể chưa?",
        [
            ("adopted", "Đã thông qua"),
            ("none", "Chưa"),
            ("drafting", "Đang soạn"),
            ("unknown", "Không biết"),
        ],
        {**COMPANY, **DISSOLUTION},
    ),
    choice(
        "dnDebtGuarantee",
        "Doanh nghiệp có bảo đảm thanh toán toàn bộ nợ và nghĩa vụ tài sản không?",
        YES_NO,
        {**COMPANY, **DISSOLUTION},
    ),
    choice(
        "dnRevenue",
        "Doanh nghiệp có phát sinh doanh thu trong kỳ gần nhất hoặc sau ngày dự kiến ngừng không?",
        YES_NO,
        COMPANY,
    ),
    fill_in(
        "dnRevenueAmount",
        "Doanh thu phát sinh khoảng bao nhiêu?",
        "number",
        show_if={**COMPANY, "dnRevenue": ["yes"]},
        unit="đồng",
        help="Điền số ước tính, bỏ trống nếu chưa biết.",
    ),
    choice(
        "dnExpenses",
        "Doanh nghiệp có phát sinh chi phí, mua vào, khấu hao, lãi vay "
        "hoặc giao dịch ngân hàng không?",
        YES_NO,
        COMPANY,
    ),
    fill_in(
        "dnExpenseNote",
        "Doanh nghiệp phát sinh những khoản nào?",
        "text",
        show_if={**COMPANY, "dnExpenses": ["yes"]},
        help="Ví dụ: lãi vay ngân hàng, khấu hao tài sản. " + NO_IDENTIFIER_HINT,
    ),
    choice(
        "dnRecords",
        "Báo cáo tài chính, sổ kế toán, hóa đơn và tờ khai thuế có truy xuất được không?",
        [
            ("complete", "Đầy đủ"),
            ("partial", "Một phần"),
            ("lost", "Mất dữ liệu"),
            ("old_accountant", "Kế toán cũ đang giữ"),
            ("unclear", "Không rõ"),
        ],
        COMPANY,
    ),
    choice(
        "dnTaxDebt",
        "Doanh nghiệp còn nợ thuế, tiền phạt, tiền chậm nộp "
        "hoặc nghĩa vụ thuế chưa được xác nhận không?",
        [("yes", "Có"), ("no", "Không"), ("unreconciled", "Chưa đối chiếu")],
        COMPANY,
    ),
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


# Hộ kinh doanh chấm dứt hoạt động: bản nháp, chuyên viên cần xác nhận từng mục
DOCUMENTS_HOUSEHOLD = [
    ("household_registration", "Giấy chứng nhận đăng ký hộ kinh doanh"),
    (
        "tax_id_termination",
        "Đơn đề nghị chấm dứt hiệu lực MST mẫu 24/ĐK-TCT — cần chuyên viên xác nhận",
    ),
    (
        "household_termination_notice",
        "Thông báo chấm dứt hoạt động hộ kinh doanh gửi cơ quan đăng ký — cần xác nhận",
    ),
    (
        "tax_obligation_confirmation",
        "Giấy xác nhận hoàn thành nghĩa vụ thuế — cần chuyên viên xác nhận",
    ),
]

# Mục chỉ thêm khi chính câu trả lời của người dùng cho thấy có liên quan
HOUSEHOLD_CONDITIONAL = {
    "missing_tax_returns": "Hồ sơ kê khai và nộp thuế các kỳ còn thiếu — cần chuyên viên xác nhận",
    "licenses": (
        "Giấy phép hoặc điều kiện ngành nghề đang áp dụng — cần xác nhận cách xử lý khi chấm dứt"
    ),
    "labor_rights": (
        "Danh sách người lao động và quyền lợi chưa giải quyết — cần chuyên viên xác nhận"
    ),
    "invoice_data": "Dữ liệu hóa đơn điện tử hoặc phần mềm bán hàng",
    "locations": "Danh sách các địa điểm kinh doanh đã đăng ký",
}
COMPANY_CONDITIONAL = {
    "debt_plan": "Danh sách khoản nợ và phương án thanh toán — cần chuyên gia xác nhận",
    "tax_debt_confirmation": (
        "Xác nhận nghĩa vụ thuế còn tồn từ cơ quan thuế — cần chuyên viên xác nhận"
    ),
    "record_recovery": "Văn bản bàn giao hoặc khôi phục sổ sách, chứng từ từ nơi đang giữ",
}


def is_visible(question: Question, answers: dict[str, object]) -> bool:
    """Câu hỏi có áp dụng với bộ câu trả lời này không (answers theo khóa camelCase)."""
    if not question.show_if:
        return True
    return all(str(answers.get(key)) in allowed for key, allowed in question.show_if.items())


def get_questionnaire() -> Questionnaire:
    return Questionnaire(version=VERSION, questions=QUESTIONS)
