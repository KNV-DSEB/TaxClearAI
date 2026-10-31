from src.modules.procedure_roadmap.schemas import ProcedureStep, Segment, TargetAction


class ProcedureRoadmapRepository:
    """Stores the reviewed procedure catalogue used to compose roadmaps."""

    def get_steps(self, segment: Segment, target_action: TargetAction) -> list[ProcedureStep]:
        if target_action == TargetAction.SUSPEND:
            steps = self._suspension_steps(segment)
        elif segment in {Segment.A1, Segment.A2, Segment.A3}:
            steps = self._household_steps(segment, target_action)
        elif target_action == TargetAction.CONVERT_TO_NEW_ENTITY:
            steps = self._company_conversion_steps(segment)
        else:
            steps = self._company_dissolution_steps(segment)
        if segment == Segment.A3:
            steps = [*self._a3_review_steps(), *steps]
            for order, step in enumerate(steps, start=1):
                step.step_order = order
        return steps

    @staticmethod
    def _a3_review_steps() -> list[ProcedureStep]:
        return [
            ProcedureStep(
                step_order=1,
                phase="A3_DECLARATION_RECONCILIATION",
                action=(
                    "Tự lập danh mục các kỳ đã kê khai và đối chiếu với sao kê/hóa đơn đang lưu; "
                    "chỉ lập danh mục, không tính tiền thuế hoặc tiền phạt."
                ),
                agency="Chủ thể tự tổng hợp",
                law_reference="Chưa xác định căn cứ trong nguồn đã đồng bộ",
                expected_duration="Chưa xác định căn cứ trong nguồn đã đồng bộ",
                can_self_do=True,
            ),
            ProcedureStep(
                step_order=2,
                phase="A3_EXPERT_REVIEW",
                action=(
                    "Kết nối chuyên gia thuế để xem xét chênh lệch và hỗ trợ giải trình nếu được "
                    "yêu cầu. Hệ thống không đánh giá mức độ sai lệch và không đề xuất cách xử lý."
                ),
                agency="Chuyên gia thuế",
                law_reference="Chưa xác định căn cứ trong nguồn đã đồng bộ",
                expected_duration="Chưa xác định căn cứ trong nguồn đã đồng bộ",
                can_self_do=False,
            ),
            ProcedureStep(
                step_order=3,
                phase="A3_OUTSTANDING_OBLIGATIONS",
                action=(
                    "Làm rõ và hoàn tất nghĩa vụ thuế còn tồn với cơ quan có thẩm quyền trước khi "
                    "nộp hồ sơ chấm dứt; hệ thống không ước tính số tiền phải nộp."
                ),
                agency="Chủ thể phối hợp với cơ quan thuế và chuyên gia",
                law_reference="Chưa xác định căn cứ trong nguồn đã đồng bộ",
                expected_duration="Chưa xác định căn cứ trong nguồn đã đồng bộ",
                can_self_do=False,
            ),
        ]

    @staticmethod
    def _suspension_steps(segment: Segment) -> list[ProcedureStep]:
        is_household = segment in {Segment.A1, Segment.A2, Segment.A3}
        subject = "hộ kinh doanh" if is_household else "doanh nghiệp"
        authority = (
            "Cơ quan đăng ký kinh doanh cấp xã"
            if is_household
            else "Cơ quan đăng ký kinh doanh cấp tỉnh"
        )
        steps = [
            ProcedureStep(
                step_order=1,
                phase="SUSPENSION_DOCUMENT_PREPARATION",
                action=(
                    f"Rà soát tình trạng đăng ký và chuẩn bị thông báo tạm ngừng {subject}; "
                    "doanh nghiệp chuẩn bị thêm quyết định/nghị quyết theo hồ sơ nội bộ áp dụng."
                ),
                agency=f"Chủ thể tự chuẩn bị / {authority} hướng dẫn",
                law_reference="Chưa xác định căn cứ trong nguồn đã đồng bộ",
                expected_duration="Chưa xác định căn cứ trong nguồn đã đồng bộ",
                can_self_do=True,
            ),
            ProcedureStep(
                step_order=2,
                phase="SUSPENSION_SUBMISSION",
                action=(
                    f"Nộp thông báo tạm ngừng kinh doanh {subject} đến cơ quan đăng ký kinh doanh "
                    "có thẩm quyền. Thời hạn và hồ sơ áp dụng cần được xác minh trước khi nộp."
                ),
                agency=authority,
                law_reference="Chưa xác định căn cứ trong nguồn đã đồng bộ",
                expected_duration="Chưa xác định căn cứ trong nguồn đã đồng bộ",
                can_self_do=True,
            ),
            ProcedureStep(
                step_order=3,
                phase="SUSPENSION_OBLIGATIONS",
                action=(
                    "Rà soát các nghĩa vụ thuế, hóa đơn, lao động và bảo hiểm xã hội còn liên quan "
                    "trong thời gian tạm ngừng; không giả định nghĩa vụ tự chấm dứt."
                ),
                agency="Chủ thể tự rà soát / cơ quan thuế và cơ quan liên quan",
                law_reference="Chưa xác định căn cứ trong nguồn đã đồng bộ",
                expected_duration="Chưa xác định căn cứ trong nguồn đã đồng bộ",
                can_self_do=True,
            ),
            ProcedureStep(
                step_order=4,
                phase="SUSPENSION_RESULT",
                action=(
                    "Theo dõi kết quả ghi nhận tạm ngừng và lưu xác nhận; kiểm tra các mốc tiếp "
                    "tục kinh doanh hoặc gia hạn theo hướng dẫn đã được cơ quan có thẩm quyền "
                    "xác nhận."
                ),
                agency=authority,
                law_reference="Chưa xác định căn cứ trong nguồn đã đồng bộ",
                expected_duration="Chưa xác định căn cứ trong nguồn đã đồng bộ",
                can_self_do=False,
            ),
        ]
        return steps

    @staticmethod
    def _household_steps(segment: Segment, target_action: TargetAction) -> list[ProcedureStep]:
        is_unregistered = segment == Segment.A1
        steps = [
            ProcedureStep(
                step_order=1,
                phase="PRECONDITION",
                action=(
                    "Dừng hoạt động thực tế; đối chiếu doanh thu, kỳ thuế, hóa đơn, lao động và "
                    "các khoản nợ. A1 chưa có đăng ký HKD để làm thủ tục chấm dứt đăng ký; "
                    "nếu chưa đăng ký thuế, liên hệ cơ quan thuế để rà soát và hoàn tất nghĩa vụ "
                    "phát sinh trước khi đóng hồ sơ kinh doanh."
                    if is_unregistered
                    else "Dừng hoạt động; đối chiếu và hoàn thành các khoản nợ, nghĩa vụ thuế, "
                    "hóa đơn và nghĩa vụ tài chính khác trước khi nộp hồ sơ chấm dứt HKD."
                ),
                agency="Chủ hộ tự thực hiện / Thuế cơ sở quản lý trực tiếp",
                law_reference=(
                    "Thông tư 90/2026/TT-BTC, Điều 27–29; Nghị định 252/2026/NĐ-CP, Điều 10"
                ),
                expected_duration=(
                    "Không có thời hạn cố định; phụ thuộc số kỳ cần đối chiếu và nghĩa vụ còn "
                    "thiếu."
                ),
                can_self_do=True,
            ),
            ProcedureStep(
                step_order=2,
                phase="DOCUMENT_PREPARATION",
                action=(
                    "Chuẩn bị hồ sơ thuế: Văn bản đề nghị chấm dứt hiệu lực mã số thuế mẫu "
                    "24/ĐKT; hoàn thiện tờ khai còn thiếu, nghĩa vụ hóa đơn và chứng từ "
                    "nộp thuế "
                    "theo phương pháp kê khai hoặc khoán áp dụng cho hộ."
                ),
                agency="Chủ hộ tự chuẩn bị / Thuế cơ sở quản lý trực tiếp hướng dẫn",
                law_reference="Thông tư 90/2026/TT-BTC, Điều 27–29",
                expected_duration=(
                    "Không có thời hạn chuẩn bị hồ sơ cố định theo các điều khoản này."
                ),
                can_self_do=True,
            ),
            ProcedureStep(
                step_order=3,
                phase="TAX_SUBMISSION",
                action=(
                    "Nộp hồ sơ đề nghị chấm dứt hiệu lực mã số thuế và hoàn thành nghĩa vụ thuế "
                    "trước khi nộp hồ sơ chấm dứt HKD tại cơ quan đăng ký kinh doanh. Hạn khai "
                    "hồ sơ thuế cuối cùng (nếu phát sinh) là 45 ngày kể từ sự kiện chấm dứt. "
                    "Với A1, chỉ đề nghị chấm dứt MST nếu đã có đăng ký thuế tương ứng."
                ),
                agency=(
                    "Thuế cơ sở quản lý trực tiếp (trước đây là Chi cục Thuế/Chi cục Thuế khu vực)"
                ),
                law_reference=(
                    "Thông tư 90/2026/TT-BTC, Điều 27; Nghị định 252/2026/NĐ-CP, Điều 10"
                ),
                expected_duration=(
                    "Hồ sơ thuế cuối cùng (nếu thuộc diện phải nộp): chậm nhất ngày thứ 45 kể từ "
                    "ngày xảy ra sự kiện chấm dứt hoạt động; không phải hạn 10 ngày làm việc."
                ),
                can_self_do=True,
            ),
            ProcedureStep(
                step_order=4,
                phase="TAX_RESULT",
                action=(
                    "Nhận thông báo trạng thái đang làm thủ tục chấm dứt mã số thuế; sau khi hoàn "
                    "thành nghĩa vụ thuế, nhận Thông báo chấm dứt hiệu lực mã số thuế mẫu "
                    "18/TB-ĐKT."
                ),
                agency="Thuế cơ sở quản lý trực tiếp",
                law_reference="Thông tư 90/2026/TT-BTC, Điều 29",
                expected_duration=(
                    "02 ngày làm việc để ra thông báo đang làm thủ tục kể từ khi nhận đủ hồ sơ; "
                    "03 ngày làm việc kể từ khi hoàn tất nghĩa vụ để ban hành thông báo chấm dứt."
                ),
                can_self_do=False,
            ),
        ]

        if not is_unregistered:
            steps.extend(
                [
                    ProcedureStep(
                        step_order=5,
                        phase="REGISTRATION_DOCUMENT_PREPARATION",
                        action=(
                            "Chuẩn bị Thông báo chấm dứt hoạt động hộ kinh doanh; rà soát đã thanh "
                            "toán các khoản nợ, trừ trường hợp có thỏa thuận khác với chủ nợ."
                        ),
                        agency="Chủ hộ tự chuẩn bị",
                        law_reference="Nghị định 168/2025/NĐ-CP, Điều 104 khoản 1 điểm a, b",
                        expected_duration="Không có thời hạn chuẩn bị hồ sơ cố định.",
                        can_self_do=True,
                    ),
                    ProcedureStep(
                        step_order=6,
                        phase="REGISTRATION_SUBMISSION",
                        action=(
                            "Nộp Thông báo chấm dứt hoạt động HKD đến cơ quan đăng ký kinh doanh "
                            "cấp xã; nộp trong 05 ngày làm việc kể từ ngày thanh toán hết các "
                            "khoản nợ."
                        ),
                        agency="Cơ quan đăng ký kinh doanh cấp xã nơi HKD đặt trụ sở",
                        law_reference="Nghị định 168/2025/NĐ-CP, Điều 104 khoản 1 điểm b",
                        expected_duration=(
                            "Nộp trong 05 ngày làm việc kể từ ngày thanh toán hết nợ."
                        ),
                        can_self_do=True,
                    ),
                    ProcedureStep(
                        step_order=7,
                        phase="TAX_CONFIRMATION",
                        action=(
                            "Cơ quan đăng ký kinh doanh chuyển thông tin hồ sơ cho cơ quan thuế; "
                            "cơ quan thuế gửi ý kiến xác nhận tình trạng hoàn thành nghĩa vụ thuế."
                        ),
                        agency=(
                            "Thuế cơ sở quản lý trực tiếp phối hợp với cơ quan đăng ký kinh "
                            "doanh cấp "
                            "xã"
                        ),
                        law_reference="Nghị định 168/2025/NĐ-CP, Điều 104 khoản 1 điểm c",
                        expected_duration=(
                            "02 ngày làm việc kể từ khi cơ quan thuế nhận được thông tin."
                        ),
                        can_self_do=False,
                    ),
                    ProcedureStep(
                        step_order=8,
                        phase="REGISTRATION_RESULT",
                        action=(
                            "Nhận Thông báo chấm dứt hoạt động HKD và kiểm tra tình trạng đã chấm "
                            "dứt trong cơ sở dữ liệu; cơ quan đăng ký kinh doanh chỉ cập nhật "
                            "kết quả "
                            "khi thuế xác nhận đã hoàn thành nghĩa vụ hoặc không nhận ý kiến thuế."
                        ),
                        agency="Cơ quan đăng ký kinh doanh cấp xã",
                        law_reference="Nghị định 168/2025/NĐ-CP, Điều 104 khoản 1 điểm c",
                        expected_duration=(
                            "05 ngày làm việc kể từ khi nhận hồ sơ; nếu cơ quan thuế từ chối "
                            "do còn "
                            "nghĩa vụ, cơ quan đăng ký thông báo để hộ xử lý tiếp."
                        ),
                        can_self_do=False,
                    ),
                ]
            )
        else:
            steps.append(
                ProcedureStep(
                    step_order=5,
                    phase="REGISTRATION_RESULT",
                    action=(
                        "Không nộp hồ sơ chấm dứt HKD tại cơ quan đăng ký kinh doanh nếu chưa từng "
                        "được cấp đăng ký HKD. Lưu kết quả xử lý thuế và xác minh không có "
                        "HKD đang "
                        "hoạt động đứng tên chủ thể trước khi lập hộ mới."
                    ),
                    agency="Chủ thể tự tra cứu / Cơ quan đăng ký kinh doanh cấp xã hỗ trợ xác minh",
                    law_reference="Nghị định 168/2025/NĐ-CP, Điều 83, 99, 104",
                    expected_duration=(
                        "Không áp dụng thời hạn chấm dứt đăng ký HKD khi không có đăng ký cũ."
                    ),
                    can_self_do=True,
                )
            )

        if target_action == TargetAction.CONVERT_TO_NEW_ENTITY:
            next_order = len(steps) + 1
            if not is_unregistered:
                steps.append(
                    ProcedureStep(
                        step_order=next_order,
                        phase="NEW_ENTITY_PRECONDITION",
                        action=(
                            "Chỉ chuyển sang bước đăng ký hộ mới đứng tên cùng cá nhân/thành viên "
                            "sau khi đã nhận Thông báo chấm dứt hoạt động hộ cũ. Mỗi cá nhân/thành "
                            "viên hộ gia đình chỉ được đăng ký một HKD trên toàn quốc."
                        ),
                        agency="Cơ quan đăng ký kinh doanh cấp xã",
                        law_reference="Nghị định 168/2025/NĐ-CP, Điều 83 khoản 1 và Điều 104",
                        expected_duration=(
                            "Điều kiện tiền đề; chờ đến khi có Thông báo chấm dứt hoạt động hộ cũ."
                        ),
                        can_self_do=False,
                    )
                )
                next_order += 1
            steps.extend(
                [
                    ProcedureStep(
                        step_order=next_order,
                        phase="NEW_ENTITY_DOCUMENT_PREPARATION",
                        action=(
                            "Chuẩn bị Giấy đề nghị đăng ký HKD mới; nếu hộ do các thành viên gia "
                            "đình đăng ký, kèm văn bản ủy quyền cho một thành viên làm chủ hộ."
                        ),
                        agency="Chủ thể tự chuẩn bị",
                        law_reference="Nghị định 168/2025/NĐ-CP, Điều 99 khoản 2",
                        expected_duration="Không có thời hạn chuẩn bị hồ sơ cố định.",
                        can_self_do=True,
                    ),
                    ProcedureStep(
                        step_order=next_order + 1,
                        phase="NEW_ENTITY_SUBMISSION",
                        action="Nộp hồ sơ đăng ký HKD mới tại cơ quan đăng ký kinh doanh cấp xã.",
                        agency="Cơ quan đăng ký kinh doanh cấp xã nơi đặt trụ sở HKD mới",
                        law_reference="Nghị định 168/2025/NĐ-CP, Điều 99 khoản 1–2",
                        expected_duration=(
                            "Nộp sau khi hoàn tất điều kiện tiền đề; không có hạn chót riêng."
                        ),
                        can_self_do=True,
                    ),
                    ProcedureStep(
                        step_order=next_order + 2,
                        phase="NEW_ENTITY_RESULT",
                        action=(
                            "Nhận Giấy chứng nhận đăng ký HKD mới hoặc thông báo yêu cầu sửa đổi, "
                            "bổ sung hồ sơ."
                        ),
                        agency="Cơ quan đăng ký kinh doanh cấp xã",
                        law_reference="Nghị định 168/2025/NĐ-CP, Điều 99 khoản 3",
                        expected_duration="03 ngày làm việc kể từ ngày nhận hồ sơ.",
                        can_self_do=False,
                    ),
                ]
            )

        return steps

    @staticmethod
    def _company_dissolution_steps(segment: Segment) -> list[ProcedureStep]:
        category_note = (
            "B1: dù chưa có doanh thu, rà soát và nộp đủ tờ khai/ báo cáo bắt buộc; không mặc định "
            "được miễn nghĩa vụ thuế."
            if segment == Segment.B1
            else "B2: phải xử lý nợ thuế, hóa đơn, lao động/BHXH và chủ nợ; nếu mất khả năng thanh "
            "toán thì dừng quy trình giải thể tự nguyện và đánh giá thủ tục phá sản."
        )
        steps = [
            ProcedureStep(
                step_order=1,
                phase="PRECONDITION",
                action=(
                    "Xác nhận doanh nghiệp thuộc trường hợp được giải thể tự nguyện, không trong "
                    "quá trình tranh chấp bị cấm giải thể; phải thanh toán hết nợ hoặc có "
                    "thỏa thuận "
                    "với chủ nợ trước hồ sơ cuối. " + category_note
                ),
                agency="Doanh nghiệp tự rà soát; luật sư/kế toán có thể hỗ trợ",
                law_reference=(
                    "Luật Doanh nghiệp 2020, Điều 207–209, đã sửa đổi bởi Luật 76/2025/QH15"
                ),
                expected_duration=(
                    "Không có thời hạn cố định; phụ thuộc việc đối chiếu nợ và nghĩa vụ."
                ),
                can_self_do=True,
            ),
            ProcedureStep(
                step_order=2,
                phase="DOCUMENT_PREPARATION",
                action=(
                    "Chuẩn bị nghị quyết/quyết định giải thể, biên bản họp nếu áp dụng và "
                    "phương án "
                    "giải quyết nợ (nếu có); lập danh sách chủ nợ, người lao động, thuế, BHXH và "
                    "nghĩa vụ hợp đồng."
                ),
                agency="Doanh nghiệp tự chuẩn bị / cơ quan quản trị có thẩm quyền thông qua",
                law_reference=(
                    "Luật Doanh nghiệp 2020, Điều 208; Nghị định 168/2025/NĐ-CP, Điều 64 khoản 1"
                ),
                expected_duration="Không có thời hạn chuẩn bị hồ sơ cố định.",
                can_self_do=True,
            ),
            ProcedureStep(
                step_order=3,
                phase="INITIAL_SUBMISSION",
                action=(
                    "Gửi nghị quyết/quyết định giải thể, biên bản họp và phương án giải quyết nợ "
                    "(nếu có) đến cơ quan đăng ký kinh doanh cấp tỉnh trong 07 ngày làm việc kể từ "
                    "ngày thông qua quyết định."
                ),
                agency="Cơ quan đăng ký kinh doanh cấp tỉnh nơi DN đặt trụ sở chính",
                law_reference=(
                    "Luật Doanh nghiệp 2020, Điều 208; Nghị định 168/2025/NĐ-CP, Điều 64 khoản 1"
                ),
                expected_duration="Nộp trong 07 ngày làm việc kể từ ngày thông qua quyết định.",
                can_self_do=True,
            ),
            ProcedureStep(
                step_order=4,
                phase="INITIAL_RESULT",
                action=(
                    "Nhận thông báo doanh nghiệp đang làm thủ tục giải thể; cơ quan đăng ký chuyển "
                    "trạng thái và gửi thông tin cho thuế, thi hành án dân sự."
                ),
                agency="Cơ quan đăng ký kinh doanh cấp tỉnh",
                law_reference="Nghị định 168/2025/NĐ-CP, Điều 64 khoản 2",
                expected_duration="03 ngày làm việc kể từ khi nhận nghị quyết/quyết định giải thể.",
                can_self_do=False,
            ),
            ProcedureStep(
                step_order=5,
                phase="PRECONDITION",
                action=(
                    "Chấm dứt hoạt động tất cả chi nhánh, văn phòng đại diện và địa điểm kinh "
                    "doanh "
                    "trước khi nộp hồ sơ giải thể cuối cùng."
                ),
                agency="Cơ quan đăng ký kinh doanh cấp tỉnh nơi từng đơn vị phụ thuộc đặt trụ sở",
                law_reference="Nghị định 168/2025/NĐ-CP, Điều 64 khoản 4; Điều 66",
                expected_duration=(
                    "Hoàn thành trước hồ sơ giải thể cuối; thời gian tùy số đơn vị và nghĩa "
                    "vụ thuế."
                ),
                can_self_do=True,
            ),
            ProcedureStep(
                step_order=6,
                phase="OBLIGATION_SETTLEMENT",
                action=(
                    (
                        "Rà soát các tờ khai và lệ phí môn bài của những năm chưa nộp. "
                        if segment == Segment.B1
                        else ""
                    )
                    + (
                        "Nộp các tờ khai/báo cáo đến thời điểm chấm dứt, hoàn thành "
                        "quyết toán thuế và hóa đơn, chốt nghĩa vụ lao động/BHXH, "
                        "thanh lý hợp đồng và thanh toán nợ theo thứ tự luật định. "
                        "Không nộp hồ sơ cuối khi còn khoản nợ chưa xử lý."
                    )
                ),
                agency="Cơ quan thuế quản lý trực tiếp; cơ quan BHXH; người lao động và chủ nợ",
                law_reference=(
                    "Luật Doanh nghiệp 2020, Điều 208–210; Luật Quản lý thuế 108/2025/QH15; "
                    "Nghị định 252/2026/NĐ-CP"
                ),
                expected_duration="Không có tổng thời hạn cố định; phải hoàn tất trước hồ sơ cuối.",
                can_self_do=True,
            ),
            ProcedureStep(
                step_order=7,
                phase="FINAL_DOCUMENT_PREPARATION",
                action=(
                    "Chuẩn bị hồ sơ giải thể cuối: thông báo giải thể, báo cáo thanh lý tài sản, "
                    "danh sách chủ nợ và xác nhận đã thanh toán nợ, gồm nợ thuế và BHXH; công "
                    "ty cổ "
                    "phần không niêm yết/không đăng ký giao dịch chuẩn bị thêm bản sao sổ "
                    "đăng ký cổ đông."
                ),
                agency="Doanh nghiệp tự chuẩn bị / người đại diện theo pháp luật ký",
                law_reference=(
                    "Luật Doanh nghiệp 2020, Điều 210; Nghị định 168/2025/NĐ-CP, Điều 64 "
                    "khoản 3 đã được sửa đổi bởi Nghị định 296/2026/NĐ-CP"
                ),
                expected_duration=(
                    "Không có thời hạn chuẩn bị cố định; hoàn thành trước khi nộp hồ sơ cuối."
                ),
                can_self_do=True,
            ),
            ProcedureStep(
                step_order=8,
                phase="FINAL_SUBMISSION",
                action=(
                    "Nộp hồ sơ đăng ký giải thể cuối cùng sau khi đã thanh toán hết các khoản nợ, "
                    "hoàn tất nghĩa vụ thuế và chấm dứt các đơn vị phụ thuộc."
                ),
                agency="Cơ quan đăng ký kinh doanh cấp tỉnh nơi DN đặt trụ sở chính",
                law_reference=(
                    "Nghị định 168/2025/NĐ-CP, Điều 64 khoản 3–4 đã được sửa đổi bởi Nghị "
                    "định 296/2026/NĐ-CP"
                ),
                expected_duration=(
                    "Nộp trong 05 ngày làm việc kể từ ngày thanh toán hết các khoản nợ."
                ),
                can_self_do=True,
            ),
            ProcedureStep(
                step_order=9,
                phase="TAX_CONFIRMATION",
                action=(
                    "Cơ quan đăng ký kinh doanh chuyển thông tin hồ sơ giải thể cho cơ quan thuế; "
                    "cơ quan thuế phản hồi về tình trạng hoàn thành nghĩa vụ thuế."
                ),
                agency=(
                    "Cơ quan thuế quản lý trực tiếp phối hợp với Cơ quan đăng ký kinh doanh "
                    "cấp tỉnh"
                ),
                law_reference=(
                    "Nghị định 168/2025/NĐ-CP, Điều 64 khoản 5 đã được sửa đổi bởi Nghị định "
                    "296/2026/NĐ-CP"
                ),
                expected_duration=(
                    "Cơ quan thuế phản hồi trong 02 ngày làm việc; cơ quan đăng ký chuyển hồ "
                    "sơ trong 01 ngày làm việc kể từ khi nhận hồ sơ."
                ),
                can_self_do=False,
            ),
            ProcedureStep(
                step_order=10,
                phase="FINAL_RESULT",
                action=(
                    "Nhận thông báo và kiểm tra trạng thái doanh nghiệp đã giải thể trên Cơ "
                    "sở dữ liệu "
                    "quốc gia về đăng ký doanh nghiệp. Nếu thuế xác nhận còn nghĩa vụ, xử lý "
                    "nghĩa vụ "
                    "đó rồi tiếp tục theo yêu cầu của cơ quan đăng ký."
                ),
                agency="Cơ quan đăng ký kinh doanh cấp tỉnh",
                law_reference=(
                    "Nghị định 168/2025/NĐ-CP, Điều 64 khoản 5 đã được sửa đổi bởi Nghị định "
                    "296/2026/NĐ-CP"
                ),
                expected_duration=(
                    "01 ngày làm việc sau khi nhận xác nhận thuế hoặc sau khi hết hạn 02 ngày "
                    "cơ quan thuế phản hồi."
                ),
                can_self_do=False,
            ),
        ]
        if segment == Segment.B2:
            steps[6:6] = [
                ProcedureStep(
                    step_order=7,
                    phase="B2_OUTSTANDING_SUMMARY",
                    action=(
                        "Lập bảng tổng hợp nội dung tồn đọng gồm VAT, TNDN, TNCN, nợ thuế, tiền "
                        "phạt và BHXH để chuyên gia xem xét; hệ thống chỉ ghi nhận nội dung, "
                        "không tính tiền."
                    ),
                    agency="Doanh nghiệp tự tổng hợp / chuyên gia thuế rà soát",
                    law_reference="Chưa xác định căn cứ trong nguồn đã đồng bộ",
                    expected_duration="Chưa xác định căn cứ trong nguồn đã đồng bộ",
                    can_self_do=True,
                ),
                ProcedureStep(
                    step_order=8,
                    phase="B2_BOOKS_RESTORATION",
                    action=(
                        "Chuẩn bị hoặc khôi phục sổ sách kế toán và báo cáo tài chính của các năm "
                        "có phát sinh trước khi tiếp tục hồ sơ giải thể cuối."
                    ),
                    agency="Doanh nghiệp tự chuẩn bị / đơn vị chuyên môn hỗ trợ",
                    law_reference="Chưa xác định căn cứ trong nguồn đã đồng bộ",
                    expected_duration="Chưa xác định căn cứ trong nguồn đã đồng bộ",
                    can_self_do=True,
                ),
                ProcedureStep(
                    step_order=9,
                    phase="B2_ASSET_AND_DEBT_REVIEW",
                    action=(
                        "Lập danh mục tài sản cần thanh lý, xử lý hàng tồn kho và đối chiếu công "
                        "nợ trước khi hoàn thiện hồ sơ giải thể cuối."
                    ),
                    agency="Doanh nghiệp tự rà soát / chuyên gia hỗ trợ đối chiếu",
                    law_reference="Chưa xác định căn cứ trong nguồn đã đồng bộ",
                    expected_duration="Chưa xác định căn cứ trong nguồn đã đồng bộ",
                    can_self_do=True,
                ),
                ProcedureStep(
                    step_order=10,
                    phase="B2_EXPERT_SUPPORT",
                    action=(
                        "Kết nối chuyên gia thuế/luật sư để xử lý các tồn đọng và rà soát trước "
                        "khi tiếp tục nộp hồ sơ giải thể cuối."
                    ),
                    agency="Chuyên gia thuế / luật sư",
                    law_reference="Chưa xác định căn cứ trong nguồn đã đồng bộ",
                    expected_duration="Chưa xác định căn cứ trong nguồn đã đồng bộ",
                    can_self_do=False,
                ),
            ]
        for step_order, step in enumerate(steps, start=1):
            step.step_order = step_order
        return steps

    @staticmethod
    def _company_conversion_steps(segment: Segment) -> list[ProcedureStep]:
        steps = [
            ProcedureStep(
                step_order=1,
                phase="PRECONDITION",
                action=(
                    "Chọn loại hình DN sau chuyển đổi và kiểm tra điều kiện thành viên/cổ "
                    "đông, vốn,"
                    "ngành nghề. Đây là chuyển đổi loại hình của doanh nghiệp hiện hữu, không "
                    "phải giải "
                    "thể rồi thành lập pháp nhân khác; nghĩa vụ và công nợ tiếp tục được kế thừa."
                ),
                agency="Doanh nghiệp tự rà soát / cơ quan quản trị thông qua phương án",
                law_reference=(
                    "Luật Doanh nghiệp 2020, Điều 202–205; Nghị định 168/2025/NĐ-CP, Điều 26"
                ),
                expected_duration="Không có thời hạn chuẩn bị cố định.",
                can_self_do=True,
            ),
            ProcedureStep(
                step_order=2,
                phase="DOCUMENT_PREPARATION",
                action=(
                    "Chuẩn bị hồ sơ đăng ký chuyển đổi theo loại hình mới, gồm hồ sơ đăng ký DN "
                    "tương ứng và nghị quyết/quyết định, biên bản hoặc giấy tờ bổ sung theo "
                    "loại chuyển "
                    "đổi. Với B2, đưa rõ khoản nợ, hợp đồng, người lao động và nghĩa vụ thuế "
                    "được kế thừa;"
                    "không khai là đã tất toán nếu chưa tất toán."
                ),
                agency="Doanh nghiệp tự chuẩn bị / người đại diện theo pháp luật",
                law_reference=(
                    "Nghị định 168/2025/NĐ-CP, Điều 24 và Điều 26; Luật Doanh nghiệp 2020, "
                    "Điều 202–205"
                ),
                expected_duration=(
                    "Không có thời hạn chuẩn bị cố định; thành phần hồ sơ phụ thuộc loại hình đích."
                ),
                can_self_do=True,
            ),
            ProcedureStep(
                step_order=3,
                phase="SUBMISSION",
                action="Nộp hồ sơ đăng ký chuyển đổi loại hình doanh nghiệp.",
                agency="Cơ quan đăng ký kinh doanh cấp tỉnh nơi DN đặt trụ sở chính",
                law_reference="Nghị định 168/2025/NĐ-CP, Điều 26 và Điều 32",
                expected_duration=(
                    "Nộp sau khi hoàn thiện hồ sơ; không có hạn chót riêng trong lộ trình này."
                ),
                can_self_do=True,
            ),
            ProcedureStep(
                step_order=4,
                phase="RESULT",
                action=(
                    "Nhận Giấy chứng nhận đăng ký doanh nghiệp theo loại hình mới hoặc thông "
                    "báo yêu "
                    "cầu sửa đổi, bổ sung hồ sơ."
                ),
                agency="Cơ quan đăng ký kinh doanh cấp tỉnh",
                law_reference="Luật Doanh nghiệp 2020, Điều 26; Nghị định 168/2025/NĐ-CP, Điều 32",
                expected_duration="03 ngày làm việc kể từ ngày nhận hồ sơ hợp lệ.",
                can_self_do=False,
            ),
            ProcedureStep(
                step_order=5,
                phase="POST_REGISTRATION",
                action=(
                    "Cập nhật thông tin thuế, hóa đơn điện tử, ngân hàng, hợp đồng lao động, BHXH, "
                    "giấy phép con và thông tin với đối tác theo loại hình mới; tiếp tục thực "
                    "hiện các "
                    "khoản nợ/nghĩa vụ đã được kế thừa."
                ),
                agency=(
                    "Doanh nghiệp sau chuyển đổi / cơ quan thuế, BHXH và cơ quan cấp phép liên quan"
                ),
                law_reference=(
                    "Luật Doanh nghiệp 2020, Điều 202–205; pháp luật thuế, lao động và BHXH "
                    "tương ứng"
                ),
                expected_duration="Thời hạn riêng tùy từng thay đổi và giấy phép liên quan.",
                can_self_do=True,
            ),
        ]
        steps.insert(
            0,
            ProcedureStep(
                step_order=1,
                phase="ALTERNATIVE_PATH_SELECTION",
                action=(
                    "Chuyển nhượng phần vốn góp/cổ phần là lựa chọn thay thế cho chuyển đổi loại "
                    "hình. Nếu có nhiều thành viên, vốn góp lớn hoặc tranh chấp, cần kết nối "
                    "chuyên gia trước khi chọn hướng."
                ),
                agency="Doanh nghiệp tự cân nhắc / chuyên gia thuế hoặc luật sư hỗ trợ",
                law_reference="Chưa xác định căn cứ trong nguồn đã đồng bộ",
                expected_duration="Chưa xác định căn cứ trong nguồn đã đồng bộ",
                can_self_do=False,
            ),
        )
        if segment == "B2":
            submission_index = next(
                index for index, step in enumerate(steps) if step.phase == "SUBMISSION"
            )
            steps[submission_index:submission_index] = [
                ProcedureStep(
                    step_order=0,
                    phase="B2_CONVERSION_OUTSTANDING_SUMMARY",
                    action=(
                        "Lập danh mục tồn đọng cần xử lý hoặc bàn giao khi chuyển đổi/chuyển "
                        "nhượng, gồm VAT, TNDN, TNCN, nợ thuế, tiền phạt và BHXH. Hệ thống "
                        "chỉ lập danh mục, không tính tiền."
                    ),
                    agency="Doanh nghiệp tự tổng hợp để rà soát hoặc bàn giao",
                    law_reference="Chưa xác định căn cứ trong nguồn đã đồng bộ",
                    expected_duration="Chưa xác định căn cứ trong nguồn đã đồng bộ",
                    can_self_do=True,
                ),
                ProcedureStep(
                    step_order=0,
                    phase="B2_CONVERSION_LEGAL_REVIEW",
                    action=(
                        "Thẩm định tình trạng pháp lý và thuế trước khi chuyển đổi hoặc chuyển "
                        "nhượng. Cần chuyên gia khi có nhiều thành viên, vốn góp lớn hoặc "
                        "tranh chấp."
                    ),
                    agency="Chuyên gia thuế hoặc luật sư",
                    law_reference="Chưa xác định căn cứ trong nguồn đã đồng bộ",
                    expected_duration="Chưa xác định căn cứ trong nguồn đã đồng bộ",
                    can_self_do=False,
                ),
            ]
        for step_order, step in enumerate(steps, start=1):
            step.step_order = step_order
        return steps
