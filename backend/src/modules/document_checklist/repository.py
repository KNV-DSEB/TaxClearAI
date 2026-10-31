from dataclasses import dataclass

from src.modules.document_checklist.schemas import Procedure, Segment


@dataclass(frozen=True)
class ChecklistDocument:
    doc_id: str
    doc_name: str
    template_download_available: bool
    missing_guide: str
    verification_guide: str


class DocumentChecklistRepository:
    """Reviewed checklist catalogue; accepts metadata only, never document files."""

    def get_documents(self, segment: Segment, procedure: Procedure) -> list[ChecklistDocument]:
        is_hkd = segment in {Segment.A1, Segment.A2, Segment.A3}
        if procedure == Procedure.SUSPEND:
            return self._suspension_documents(is_hkd)
        if procedure == Procedure.TERMINATE:
            if is_hkd:
                documents = self._hkd_termination()
                if segment == Segment.A1:
                    documents = [
                        doc
                        for doc in documents
                        if doc.doc_id not in {"DOC_HKD_TERMINATION", "DOC_HKD_REGISTRATION_INFO"}
                    ]
                return [*documents, *self._hkd_termination_additions(segment)]
            documents = [*self._company_termination(), *self._company_termination_common()]
            if segment == Segment.B1:
                documents.extend(self._company_b1_termination_additions())
            else:
                documents.extend(self._company_b2_termination_additions())
            return documents
        if is_hkd:
            return self._hkd_new_registration()
        documents = self._company_conversion()
        if segment == Segment.B2:
            documents.append(self._company_b2_conversion_addition())
        return documents

    @staticmethod
    def _suspension_documents(is_hkd: bool) -> list[ChecklistDocument]:
        documents = [
            ChecklistDocument(
                "DOC_SUSPENSION_NOTICE",
                "Thông báo tạm ngừng kinh doanh",
                False,
                "Tự xác nhận biểu mẫu và thông tin cần kê khai theo hướng dẫn chính thức; "
                "không tải giấy tờ lên hệ thống.",
                "Đối chiếu thông tin chủ thể và thời gian dự kiến với căn cứ trong nguồn đã "
                "đồng bộ.",
            ),
            ChecklistDocument(
                "DOC_OUTSTANDING_OBLIGATIONS_STATUS",
                "Danh mục nghĩa vụ thuế và nghĩa vụ liên quan còn tồn (nếu có)",
                False,
                "Chỉ lập danh mục nghĩa vụ cần hỏi cơ quan thuế/chuyên gia; không nhập số tiền "
                "hoặc tải chứng từ.",
                "Cần cơ quan thuế hoặc chuyên gia xác nhận trạng thái nghĩa vụ; checklist "
                "không kết luận đã hoàn thành.",
            ),
        ]
        if not is_hkd:
            documents.append(
                ChecklistDocument(
                    "DOC_COMPANY_SUSPENSION_RESOLUTION",
                    "Quyết định hoặc nghị quyết về việc tạm ngừng (nếu áp dụng)",
                    False,
                    "Tự xác nhận văn bản nội bộ phù hợp với loại hình và thẩm quyền; không tải "
                    "văn bản lên hệ thống.",
                    "Nhờ chuyên gia kiểm tra thẩm quyền, nội dung và chữ ký nếu cần.",
                )
            )
        return documents

    @staticmethod
    def _hkd_termination_additions(segment: Segment) -> list[ChecklistDocument]:
        documents = [
            ChecklistDocument(
                "DOC_HKD_BANK_STATEMENTS",
                "Sao kê các tài khoản dùng nhận tiền kinh doanh",
                False,
                "Tự lập danh mục tài khoản dùng cho hoạt động kinh doanh và kỳ sao kê cần rà soát; "
                "không tải sao kê lên hệ thống.",
                "Tự đối chiếu các khoản thu với bảng kê doanh thu; chỉ cung cấp thông tin cho "
                "chuyên gia qua kênh phù hợp nếu cần.",
            ),
            ChecklistDocument(
                "DOC_HKD_REVENUE_SUMMARY",
                "Bảng kê doanh thu theo quý, năm",
                False,
                "Tự tổng hợp doanh thu theo quý và năm từ dữ liệu đang có; không nhập số liệu "
                "nhạy cảm hoặc tải bảng kê lên checklist.",
                "Đối chiếu kỳ tổng hợp với dữ liệu giao dịch và tờ khai của mình; checklist không "
                "xác nhận tính đúng của số liệu.",
            ),
            ChecklistDocument(
                "DOC_HKD_SALES_COST_RECORDS",
                "Danh mục hóa đơn, chứng từ bán hàng và chi phí",
                False,
                "Tự lập danh mục hóa đơn/chứng từ bán hàng và chi phí theo kỳ; không tải bản gốc, "
                "bản chụp hoặc nội dung giấy tờ lên hệ thống.",
                "Tự đối chiếu danh mục với doanh thu và chi phí đã kê khai; xác minh bản gốc được "
                "lưu giữ an toàn.",
            ),
        ]
        if segment != Segment.A1:
            documents.insert(
                0,
                ChecklistDocument(
                    "DOC_HKD_REGISTRATION_CERTIFICATE",
                    "Giấy chứng nhận đăng ký hộ kinh doanh (nếu có)",
                    False,
                    "Tự xác nhận hộ có được cấp giấy chứng nhận hay không và lưu giấy tờ an toàn; "
                    "không tải bản gốc hoặc bản chụp lên hệ thống.",
                    "Tự đối chiếu tên hộ, chủ hộ và thông tin đăng ký theo bản khai báo; hệ thống "
                    "không xem hoặc xác nhận giấy tờ.",
                ),
            )
        if segment == Segment.A3:
            documents.extend(
                [
                    ChecklistDocument(
                        "DOC_HKD_REVENUE_RECONCILIATION",
                        "Bản tự đối chiếu doanh thu đã kê khai với sao kê/dữ liệu giao dịch",
                        False,
                        "Tự lập bảng đối chiếu theo kỳ giữa doanh thu đã kê khai và dữ liệu giao "
                        "dịch; không tải bảng hoặc chứng từ lên hệ thống.",
                        "Tự đánh dấu chênh lệch cần giải thích và đối chiếu lại nguồn dữ liệu; hệ "
                        "thống không tính toán hay kết luận sai phạm.",
                    ),
                    ChecklistDocument(
                        "DOC_HKD_TAX_EXPLANATION_NOTICE",
                        "Thông báo hoặc yêu cầu giải trình của cơ quan thuế (nếu đã nhận)",
                        False,
                        "Chỉ ghi nhận đã nhận hay chưa nhận thông báo/yêu cầu; không tải văn bản "
                        "hoặc nhập nội dung giấy tờ lên hệ thống.",
                        "Tự kiểm tra thời điểm nhận và việc đã phản hồi hay chưa; nội dung cần "
                        "được chuyên gia xem xét qua kênh phù hợp.",
                    ),
                ]
            )
        return documents

    @staticmethod
    def _company_termination_common() -> list[ChecklistDocument]:
        return [
            ChecklistDocument(
                "DOC_COMPANY_REGISTRATION_AND_CHARTER",
                "Giấy chứng nhận đăng ký doanh nghiệp và Điều lệ công ty",
                False,
                "Tự xác nhận tình trạng lưu giữ giấy chứng nhận và Điều lệ; không tải bản gốc, "
                "bản chụp hoặc nội dung lên hệ thống.",
                "Tự đối chiếu tên, loại hình và thông tin quản trị theo bản khai báo; hệ thống "
                "không xác minh giấy tờ.",
            ),
            ChecklistDocument(
                "DOC_COMPANY_REPRESENTATIVE_OWNER_INFO",
                "Thông tin giấy tờ pháp lý của người đại diện/chủ sở hữu",
                False,
                "Tự xác nhận giấy tờ pháp lý liên quan đang được lưu giữ; không nhập số định danh "
                "hoặc tải giấy tờ lên hệ thống.",
                "Tự đối chiếu vai trò, thông tin chủ thể và tình trạng giấy tờ; chỉ trao đổi với "
                "chuyên gia qua kênh phù hợp nếu cần.",
            ),
        ]

    @staticmethod
    def _company_b1_termination_additions() -> list[ChecklistDocument]:
        return [
            ChecklistDocument(
                "DOC_B1_NO_REVENUE_ASSET_REVIEW",
                "Bản tự rà soát xác nhận không phát sinh doanh thu, không có tài sản",
                False,
                "Tự lập xác nhận và căn cứ nội bộ cho tình trạng doanh thu/tài sản; không tải "
                "bảng kê hoặc chứng từ lên hệ thống.",
                "Tự kiểm tra phạm vi thời gian và đối chiếu với sổ sách, tài khoản, tài sản đang "
                "theo dõi; chuyên gia cần xác minh trước khi kết luận.",
            )
        ]

    @staticmethod
    def _company_b2_termination_additions() -> list[ChecklistDocument]:
        return [
            ChecklistDocument(
                "DOC_B2_INVOICES_VOUCHERS_BOOKS",
                "Danh mục hóa đơn, chứng từ gốc và sổ sách kế toán",
                False,
                "Tự lập danh mục hóa đơn, chứng từ và sổ sách theo kỳ phát sinh; không tải bản "
                "gốc, bản chụp hoặc nội dung lên hệ thống.",
                "Tự kiểm tra tính đầy đủ của danh mục và nơi lưu bản gốc; việc đối chiếu chi tiết "
                "được thực hiện với chuyên gia qua kênh phù hợp.",
            ),
            ChecklistDocument(
                "DOC_B2_LEDGER_ACCOUNTS_1_9",
                "Sổ chi tiết tài khoản loại 1 đến loại 9 các năm có phát sinh",
                False,
                "Tự xác định các năm có phát sinh và lập danh mục sổ chi tiết tài khoản cần rà "
                "soát; không tải sổ sách lên hệ thống.",
                "Tự đối chiếu danh mục năm/kỳ với hồ sơ kế toán đang lưu; không nhập số liệu vào "
                "checklist.",
            ),
            ChecklistDocument(
                "DOC_B2_FINANCIAL_STATEMENTS",
                "Danh mục báo cáo tài chính các năm có phát sinh",
                False,
                "Tự ghi nhận các năm có phát sinh và tình trạng lưu báo cáo tài chính; không tải "
                "báo cáo hay dữ liệu tài chính lên hệ thống.",
                "Tự đối chiếu danh sách năm với sổ sách và tình trạng nộp báo cáo; hệ thống không "
                "xác nhận số liệu.",
            ),
            ChecklistDocument(
                "DOC_B2_DEBT_INVENTORY_CONTRACTS",
                "Danh mục hợp đồng, đối chiếu công nợ và hàng tồn kho",
                False,
                "Tự lập danh mục hợp đồng, biên bản đối chiếu công nợ và hồ sơ hàng tồn kho; "
                "không tải tài liệu hoặc nội dung giấy tờ lên hệ thống.",
                "Tự kiểm tra kỳ, đối tác và trạng thái đối chiếu; chuyên gia có thể rà soát "
                "bản gốc "
                "qua kênh phù hợp.",
            ),
            ChecklistDocument(
                "DOC_B2_LABOR_SOCIAL_INSURANCE",
                "Danh mục hồ sơ lao động và bảo hiểm xã hội",
                False,
                "Tự lập danh mục hồ sơ lao động/BHXH và tình trạng nghĩa vụ liên quan; không nhập "
                "thông tin cá nhân hoặc tải hồ sơ lên hệ thống.",
                "Tự đối chiếu danh sách lao động, kỳ tham gia và hồ sơ còn cần xử lý; không đưa dữ "
                "liệu định danh vào checklist.",
            ),
            ChecklistDocument(
                "DOC_B2_TAX_RISK_SELF_REVIEW",
                "Bảng tự rà soát rủi ro thuế để người dùng và chuyên gia tham khảo",
                False,
                "Tự ghi nhận các nội dung cần chuyên gia xem xét; hệ thống không tính tiền thuế, "
                "tiền phạt hoặc nghĩa vụ tài chính.",
                "Chỉ dùng bảng tự rà soát làm danh mục trao đổi; chuyên gia cần đối chiếu hồ sơ "
                "thực tế và hệ thống không kết luận rủi ro.",
            ),
        ]

    @staticmethod
    def _hkd_termination() -> list[ChecklistDocument]:
        return [
            ChecklistDocument(
                "DOC_TAX_CLOSE",
                "Thông tin và hồ sơ đề nghị chấm dứt hiệu lực mã số thuế",
                True,
                (
                    "Tra cứu biểu mẫu hiện hành trên cổng Thuế điện tử/Thuế cơ sở; chỉ điền thông "
                    "tin, không tải giấy tờ gốc lên hệ thống rà soát."
                ),
                (
                    "Đối chiếu thông tin chủ hộ, mã số thuế và tình trạng tiếp nhận với Thuế cơ "
                    "sở; không khai số định danh hoặc gửi bản scan tại bước này."
                ),
            ),
            ChecklistDocument(
                "DOC_TAX_DECLARATIONS",
                "Bản tự rà soát tờ khai, hóa đơn và nghĩa vụ thuế còn tồn",
                False,
                (
                    "Tự lập danh sách kỳ kê khai, hóa đơn và khoản thuế còn thiếu dựa trên dữ "
                    "liệu đang có; hỏi Thuế cơ sở nếu chưa rõ."
                ),
                (
                    "Đối chiếu số kỳ, hóa đơn và số phải nộp trực tiếp với thông tin do cơ quan "
                    "thuế cung cấp."
                ),
            ),
            ChecklistDocument(
                "DOC_HKD_TERMINATION",
                "Thông báo chấm dứt hoạt động hộ kinh doanh theo biểu mẫu đăng ký HKD hiện hành",
                True,
                (
                    "Tải biểu mẫu đăng ký hộ kinh doanh đang được cơ quan đăng ký kinh doanh cấp "
                    "xã công bố; không dùng mẫu cũ nếu biểu mẫu đã được thay thế."
                ),
                (
                    "Kiểm tra tên hộ, mã số hộ, chữ ký/chủ thể ký và tình trạng đăng ký cũ; chỉ "
                    "xác minh theo bản khai báo, không tải bản gốc."
                ),
            ),
            ChecklistDocument(
                "DOC_HKD_REGISTRATION_INFO",
                "Thông tin đăng ký hộ kinh doanh để đối chiếu",
                False,
                (
                    "Nếu hộ đã đăng ký, chuẩn bị thông tin đăng ký để đối chiếu; không cần tải "
                    "bản gốc hoặc bản scan."
                ),
                (
                    "Tự đối chiếu thông tin đăng ký với hồ sơ; không yêu cầu nộp bản gốc hoặc bản "
                    "scan."
                ),
            ),
        ]

    @staticmethod
    def _hkd_new_registration() -> list[ChecklistDocument]:
        return [
            ChecklistDocument(
                "DOC_OLD_HKD_CLOSURE",
                "Thông báo/kết quả chấm dứt hoạt động hộ kinh doanh cũ (nếu cùng chủ thể đã có hộ)",
                False,
                (
                    "Hoàn tất chấm dứt hộ cũ trước; chỉ nộp đăng ký hộ mới sau khi có kết "
                    "quả/thông báo chấm dứt theo quy định."
                ),
                (
                    "Đối chiếu chủ thể và trạng thái chấm dứt với cơ quan đăng ký kinh doanh cấp "
                    "xã; không tải giấy tờ gốc."
                ),
            ),
            ChecklistDocument(
                "DOC_HKD_NEW_FORM",
                "Hồ sơ đăng ký hộ kinh doanh mới theo biểu mẫu hiện hành",
                True,
                (
                    "Tải biểu mẫu đăng ký HKD đang có hiệu lực từ cổng đăng ký hộ kinh doanh; "
                    "chuẩn bị theo hướng dẫn của cơ quan cấp xã."
                ),
                (
                    "Rà soát thông tin chủ thể, tên, địa điểm và ngành nghề theo khai báo; không "
                    "gửi giấy tờ định danh tại bước rà soát này."
                ),
            ),
            ChecklistDocument(
                "DOC_HKD_ADDRESS_PERMISSION",
                "Thông tin về quyền sử dụng địa điểm kinh doanh (nếu thủ tục/địa điểm yêu cầu)",
                False,
                (
                    "Xác định địa điểm dự kiến và căn cứ được phép sử dụng; yêu cầu cụ thể phụ "
                    "thuộc địa điểm và ngành nghề."
                ),
                (
                    "Tự kiểm tra thời hạn, chủ thể cho sử dụng và phạm vi địa điểm; không tải hợp "
                    "đồng hay giấy tờ nhà đất lên đây."
                ),
            ),
        ]

    @staticmethod
    def _company_termination() -> list[ChecklistDocument]:
        return [
            ChecklistDocument(
                "DOC_DISSOLUTION_DECISION",
                "Nghị quyết/quyết định giải thể và biên bản họp (nếu thuộc trường hợp phải có)",
                False,
                (
                    "Soạn nghị quyết/quyết định theo đúng loại hình và thẩm quyền; cần biểu "
                    "quyết/biên bản theo điều lệ và luật doanh nghiệp."
                ),
                (
                    "Đối chiếu thẩm quyền ký, ngày thông qua và nội dung phương án xử lý nghĩa "
                    "vụ; không tải bản ký hoặc dấu mộc."
                ),
            ),
            ChecklistDocument(
                "DOC_CREDITOR_PLAN",
                "Phương án thanh toán nợ và danh sách chủ nợ/người lao động (nếu có)",
                False,
                (
                    "Lập danh sách nghĩa vụ còn lại và cách xử lý; giải thể tự nguyện chỉ hoàn "
                    "tất khi đã thanh toán hết các khoản nợ."
                ),
                (
                    "Đối soát số dư, khoản nợ thuế, người lao động, BHXH và hóa đơn với bên liên "
                    "quan/cơ quan quản lý."
                ),
            ),
            ChecklistDocument(
                "DOC_TAX_CLOSE_COMPANY",
                "Hồ sơ và kết quả hoàn tất nghĩa vụ thuế, chấm dứt hiệu lực mã số thuế",
                True,
                (
                    "Rà soát hồ sơ thuế, tờ khai và hóa đơn còn thiếu; thực hiện thủ tục với cơ "
                    "quan thuế quản lý theo biểu mẫu hiện hành."
                ),
                (
                    "Xác minh trạng thái nghĩa vụ và thông báo của cơ quan thuế; không nộp tờ "
                    "khai thuế hoặc giấy tờ gốc vào checklist này."
                ),
            ),
            ChecklistDocument(
                "DOC_FINAL_DISSOLUTION",
                "Thông báo/hồ sơ đăng ký giải thể doanh nghiệp cuối cùng",
                True,
                (
                    "Dùng biểu mẫu đăng ký doanh nghiệp hiện hành và nộp sau khi hoàn tất các "
                    "nghĩa vụ tiền đề."
                ),
                (
                    "Kiểm tra tính nhất quán giữa hồ sơ đã khai, tình trạng chi nhánh/địa điểm và "
                    "xác nhận nghĩa vụ; không rà soát bản scan."
                ),
            ),
        ]

    @staticmethod
    def _company_conversion() -> list[ChecklistDocument]:
        return [
            ChecklistDocument(
                "DOC_CONVERSION_DECISION",
                (
                    "Nghị quyết/quyết định chuyển đổi loại hình và biên bản họp (nếu thuộc trường "
                    "hợp phải có)"
                ),
                False,
                (
                    "Xác định loại hình đích và chuẩn bị quyết định theo thẩm quyền, điều lệ và "
                    "luật doanh nghiệp."
                ),
                (
                    "Đối chiếu chữ ký, thẩm quyền thông qua, vốn và thành viên/cổ đông theo khai "
                    "báo; không gửi bản có chữ ký/dấu."
                ),
            ),
            ChecklistDocument(
                "DOC_CONVERSION_APPLICATION",
                "Hồ sơ đăng ký doanh nghiệp sau chuyển đổi theo loại hình đích",
                True,
                (
                    "Chọn loại hình đích trước; thành phần hồ sơ và biểu mẫu đăng ký phụ thuộc "
                    "loại hình đích theo quy định hiện hành."
                ),
                (
                    "Đối chiếu điều lệ, chủ sở hữu/thành viên/cổ đông, vốn và người đại diện; "
                    "không tải tài liệu nội bộ lên bước này."
                ),
            ),
            ChecklistDocument(
                "DOC_OBLIGATIONS_TRANSFER",
                "Bản tự rà soát nghĩa vụ, hợp đồng, lao động và tài sản chuyển tiếp",
                False,
                (
                    "Lập danh mục nghĩa vụ và hợp đồng đang tồn; chuyển đổi không tự xóa nợ hoặc "
                    "nghĩa vụ đã phát sinh."
                ),
                (
                    "Xác minh số dư nợ thuế, hóa đơn, BHXH, lao động, tài sản và chủ thể tiếp "
                    "nhận với các bên liên quan."
                ),
            ),
        ]

    @staticmethod
    def _company_b2_conversion_addition() -> ChecklistDocument:
        return ChecklistDocument(
            "DOC_B2_CONVERSION_OUTSTANDING_REVIEW",
            "Bản tự rà soát tồn đọng thuế, công nợ và lao động khi chuyển đổi",
            False,
            "Tự lập danh mục nghĩa vụ thuế, công nợ và nội dung lao động còn cần theo dõi; không "
            "tải chứng từ hoặc nhập số liệu tài chính lên hệ thống.",
            "Tự đối chiếu danh mục với hồ sơ đang lưu và đánh dấu nội dung cần chuyên gia "
            "xác minh; "
            "hệ thống không tính tiền hoặc xác nhận nghĩa vụ.",
        )
