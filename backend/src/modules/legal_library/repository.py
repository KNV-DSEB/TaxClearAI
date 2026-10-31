from datetime import date

from src.modules.legal_library.schemas import (
    ApplicableProvision,
    LegalProcedure,
    LegalReference,
)


class LegalLibraryRepository:
    """Procedure references joined with the shared law text store by the service."""

    def get_references(
        self, procedure: LegalProcedure | None, query: str | None
    ) -> list[LegalReference]:
        catalogue = self._catalogue()
        references = [
            reference
            for procedures, reference, keywords in catalogue
            if (procedure is None or procedure in procedures)
            and self._matches(query, reference, keywords)
        ]
        return references

    @staticmethod
    def _matches(query: str | None, reference: LegalReference, keywords: str) -> bool:
        if query is None:
            return True
        searchable_text = " ".join(
            [
                reference.document_name,
                reference.document_number,
                reference.summary,
                keywords,
                " ".join(
                    f"{item.article} {item.clause} {item.point or ''} {item.regulated_action}"
                    for item in reference.applicable_provisions
                ),
            ]
        ).casefold()
        return query.casefold().strip() in searchable_text

    @staticmethod
    def _catalogue() -> list[tuple[set[LegalProcedure], LegalReference, str]]:
        hkd_close = {LegalProcedure.HKD_TERMINATION}
        new_hkd = {LegalProcedure.HKD_NEW_REGISTRATION}
        tax_close = {
            LegalProcedure.TAX_ID_TERMINATION,
            LegalProcedure.HKD_TERMINATION,
            LegalProcedure.COMPANY_DISSOLUTION,
        }
        company_close = {LegalProcedure.COMPANY_DISSOLUTION}
        all_procedures = set(LegalProcedure)

        law_108 = LegalReference(
            document_name="Luật Quản lý thuế",
            document_number="108/2025/QH15",
            issuing_authority="Quốc hội",
            issued_date=date(2025, 12, 10),
            effective_date=date(2026, 7, 1),
            effectiveness_status="Đang có hiệu lực từ ngày 01/07/2026.",
            applicable_provisions=[
                ApplicableProvision(
                    article="Điều 10",
                    clause="Khoản 1",
                    regulated_action=(
                        "Xác định đăng ký thuế bao gồm đăng ký lần đầu, thay đổi, tạm ngừng, "
                        "chấm dứt hiệu lực mã số thuế và khôi phục mã số thuế."
                    ),
                ),
                ApplicableProvision(
                    article="Điều 10",
                    clause="Khoản 2",
                    regulated_action=(
                        "Quy định đăng ký thuế liên thông với đăng ký doanh nghiệp và đăng ký "
                        "hộ kinh doanh đối với các đối tượng thuộc diện đăng ký liên thông."
                    ),
                ),
            ],
            summary=(
                "Luật Quản lý thuế hiện hành từ 01/07/2026; thủ tục, hồ sơ và xử lý chấm dứt "
                "mã số thuế được cụ thể hóa tại Nghị định 252/2026/NĐ-CP và Thông tư "
                "90/2026/TT-BTC."
            ),
            source_url="https://vanban.chinhphu.vn/?docid=216541&orggroupid=1&pageid=27160",
        )

        tax_registration_rules = LegalReference(
            document_name="Thông tư quy định về đăng ký thuế",
            document_number="90/2026/TT-BTC",
            issuing_authority="Bộ Tài chính",
            issued_date=date(2026, 6, 30),
            effective_date=date(2026, 7, 1),
            effectiveness_status="Đang có hiệu lực từ ngày 01/07/2026.",
            applicable_provisions=[
                ApplicableProvision(
                    article="Điều 27",
                    clause="Khoản 1",
                    point="Điểm a",
                    regulated_action=(
                        "Xác định trường hợp chấm dứt hiệu lực mã số thuế khi người nộp thuế "
                        "chấm dứt hoạt động kinh doanh hoặc giải thể, phá sản."
                    ),
                ),
                ApplicableProvision(
                    article="Điều 27",
                    clause="Khoản 4, khoản 5",
                    regulated_action=(
                        "Hộ kinh doanh phải nộp hồ sơ thuế và hoàn thành nghĩa vụ tại cơ quan "
                        "thuế trước khi nộp hồ sơ chấm dứt hoạt động ở cơ quan đăng ký kinh doanh; "
                        "hồ sơ chấm dứt mã số thuế dùng mẫu 24/ĐKT."
                    ),
                ),
                ApplicableProvision(
                    article="Điều 28",
                    clause="Khoản 1, khoản 2",
                    regulated_action=(
                        "Quy định nghĩa vụ cần hoàn tất về hồ sơ khai thuế, hóa đơn, tiền thuế "
                        "và xử lý khoản nộp thừa trước khi chấm dứt mã số thuế."
                    ),
                ),
                ApplicableProvision(
                    article="Điều 29",
                    clause="Khoản 1",
                    point="Điểm a.1, a.5",
                    regulated_action=(
                        "Cơ quan thuế gửi thông báo đang làm thủ tục trong 02 ngày làm việc từ "
                        "khi nhận đủ hồ sơ/thông tin; ban hành thông báo chấm dứt trong 03 ngày "
                        "làm việc kể từ khi hoàn tất nghĩa vụ thuế."
                    ),
                ),
            ],
            summary=(
                "Văn bản hiện hành về đăng ký thuế. Với HKD, Điều 27 quy định hồ sơ; Điều 28 "
                "quy định nghĩa vụ phải xử lý; Điều 29 quy định xử lý và thời hạn phản hồi "
                "của cơ quan thuế."
            ),
            source_url="https://vanban.chinhphu.vn/?docid=218839&pageid=27160",
        )

        tax_decree = LegalReference(
            document_name=(
                "Nghị định quy định chi tiết một số điều và biện pháp để tổ chức, hướng dẫn "
                "thi hành Luật Quản lý thuế"
            ),
            document_number="252/2026/NĐ-CP",
            issuing_authority="Chính phủ",
            issued_date=date(2026, 6, 30),
            effective_date=date(2026, 7, 1),
            effectiveness_status="Đang có hiệu lực từ ngày 01/07/2026.",
            applicable_provisions=[
                ApplicableProvision(
                    article="Điều 7",
                    clause="Khoản 1",
                    point="Điểm d.1",
                    regulated_action=(
                        "Quy định nghĩa vụ khai/nộp thuế và xử lý số thuế nộp thừa, số thuế "
                        "GTGT chưa khấu trừ khi chấm dứt hoạt động."
                    ),
                )
            ],
            summary=(
                "Nghị định hướng dẫn thi hành Luật Quản lý thuế 108/2025/QH15; áp dụng cùng "
                "Thông tư 90/2026/TT-BTC khi xử lý nghĩa vụ và chấm dứt mã số thuế."
            ),
            source_url="https://vanban.chinhphu.vn/?docid=218690&orggroupid=2&pageid=27160",
        )

        hkd_registration = LegalReference(
            document_name="Nghị định về đăng ký doanh nghiệp",
            document_number="168/2025/NĐ-CP",
            issuing_authority="Chính phủ",
            issued_date=date(2025, 6, 30),
            effective_date=date(2025, 7, 1),
            effectiveness_status=(
                "Đang có hiệu lực; đã được sửa đổi, bổ sung bởi Nghị định 296/2026/NĐ-CP "
                "có hiệu lực từ 23/07/2026."
            ),
            applicable_provisions=[
                ApplicableProvision(
                    article="Điều 83",
                    clause="Khoản 1",
                    regulated_action=(
                        "Một cá nhân/thành viên hộ gia đình chỉ được đăng ký một hộ kinh doanh "
                        "trên toàn quốc."
                    ),
                ),
                ApplicableProvision(
                    article="Điều 99",
                    clause="Khoản 1, khoản 2",
                    regulated_action=(
                        "Hồ sơ thành lập hộ kinh doanh nộp tại cơ quan đăng ký kinh doanh cấp xã; "
                        "hồ sơ gồm giấy đề nghị và văn bản ủy quyền có công chứng/chứng thực nếu "
                        "do các thành viên hộ gia đình thành lập."
                    ),
                ),
                ApplicableProvision(
                    article="Điều 99",
                    clause="Khoản 3",
                    regulated_action=(
                        "Cơ quan đăng ký kinh doanh cấp xã cấp giấy chứng nhận hoặc thông báo yêu "
                        "cầu sửa đổi trong 03 ngày làm việc kể từ ngày nhận hồ sơ."
                    ),
                ),
            ],
            summary=(
                "Quy định đăng ký HKD tại cấp xã. Khi chủ thể đang có HKD cũ, cần xử lý trạng thái "
                "chấm dứt hộ cũ trước khi đăng ký hộ mới; hồ sơ thành lập và thời hạn được "
                "quy định tại Điều 99."
            ),
            source_url="https://xaydungchinhsach.chinhphu.vn/toan-van-nghi-dinh-168-2025-nd-cp-ve-dang-ky-doanh-nghiep-119250702175708554.htm",
            change_note="Được sửa đổi, bổ sung bởi Nghị định 296/2026/NĐ-CP.",
        )

        hkd_termination = LegalReference(
            document_name="Nghị định về đăng ký doanh nghiệp",
            document_number="168/2025/NĐ-CP",
            issuing_authority="Chính phủ",
            issued_date=date(2025, 6, 30),
            effective_date=date(2025, 7, 1),
            effectiveness_status=(
                "Đang có hiệu lực; đã được sửa đổi, bổ sung bởi Nghị định 296/2026/NĐ-CP "
                "có hiệu lực từ 23/07/2026."
            ),
            applicable_provisions=[
                ApplicableProvision(
                    article="Điều 104",
                    clause="Khoản 1",
                    point="Điểm a",
                    regulated_action=(
                        "HKD phải thanh toán các khoản nợ, gồm nợ thuế và nghĩa vụ tài chính khác, "
                        "trước khi nộp hồ sơ, trừ thỏa thuận khác với chủ nợ."
                    ),
                ),
                ApplicableProvision(
                    article="Điều 104",
                    clause="Khoản 1",
                    point="Điểm b",
                    regulated_action=(
                        "Trong 05 ngày làm việc kể từ ngày thanh toán hết nợ, HKD nộp thông báo "
                        "chấm dứt đến cơ quan đăng ký kinh doanh cấp xã."
                    ),
                ),
                ApplicableProvision(
                    article="Điều 104",
                    clause="Khoản 1",
                    point="Điểm c, điểm d",
                    regulated_action=(
                        "Sau khi nhận hồ sơ đăng ký chấm dứt, cơ quan đăng ký kinh doanh cấp xã "
                        "chuyển thông tin cho cơ quan thuế; "
                        "cơ quan thuế phản hồi trong 02 ngày làm việc; cơ quan đăng ký cập nhật "
                        "chấm dứt trong 05 ngày làm việc nếu đủ điều kiện."
                    ),
                ),
            ],
            summary=(
                "Trình tự phối hợp đăng ký HKD được quy định tại Điều 104. Đối với HKD thuộc "
                "trường hợp phải đề nghị chấm dứt MST, khoản 4 Điều 27 Thông tư 90/2026/TT-BTC "
                "yêu cầu hoàn tất thủ tục thuế trước khi nộp hồ sơ chấm dứt tại cơ quan đăng ký; "
                "Điều 104 tiếp tục quy định cơ quan thuế phản hồi hồ sơ liên thông."
            ),
            source_url="https://xaydungchinhsach.chinhphu.vn/toan-van-nghi-dinh-168-2025-nd-cp-ve-dang-ky-doanh-nghiep-119250702175708554.htm",
            change_note="Được sửa đổi, bổ sung bởi Nghị định 296/2026/NĐ-CP.",
        )

        company_law = LegalReference(
            document_name="Luật Doanh nghiệp",
            document_number="59/2020/QH14",
            issuing_authority="Quốc hội",
            issued_date=date(2020, 6, 17),
            effective_date=date(2021, 1, 1),
            effectiveness_status=(
                "Đang có hiệu lực, đã được sửa đổi, bổ sung một số điều, gồm Luật 76/2025/QH15 "
                "có hiệu lực từ 01/07/2025."
            ),
            applicable_provisions=[
                ApplicableProvision(
                    article="Điều 207",
                    clause="Khoản 1, khoản 2",
                    regulated_action=(
                        "Nêu các trường hợp giải thể và điều kiện: thanh toán hết nợ/nghĩa vụ "
                        "tài sản, "
                        "không trong quá trình giải quyết tranh chấp tại Tòa án hoặc Trọng tài."
                    ),
                ),
                ApplicableProvision(
                    article="Điều 208",
                    clause="Khoản 1, khoản 2, khoản 3, khoản 4, khoản 5",
                    regulated_action=(
                        "Quy định nghị quyết/quyết định giải thể, thanh lý tài sản, thông báo và "
                        "phương án nợ, hoàn thành nghĩa vụ, nộp hồ sơ đăng ký giải thể."
                    ),
                ),
                ApplicableProvision(
                    article="Điều 209",
                    clause="Khoản 1 đến khoản 6",
                    regulated_action=(
                        "Quy định giải thể trong trường hợp bị thu hồi giấy chứng nhận đăng ký "
                        "doanh nghiệp "
                        "hoặc theo quyết định của Tòa án."
                    ),
                ),
                ApplicableProvision(
                    article="Điều 210",
                    clause="Khoản 1",
                    regulated_action="Quy định bộ hồ sơ đăng ký giải thể doanh nghiệp cuối cùng.",
                ),
            ],
            summary=(
                "Luật khung về điều kiện, quyết định, nghĩa vụ nợ và hồ sơ giải thể doanh nghiệp; "
                "quy trình đăng ký chi tiết được hướng dẫn tại Điều 64 Nghị định 168/2025/NĐ-CP."
            ),
            source_url="https://vanban.chinhphu.vn/?amp=&docid=200447&pageid=27160",
        )

        company_registration_rules = LegalReference(
            document_name="Nghị định về đăng ký doanh nghiệp",
            document_number="168/2025/NĐ-CP",
            issuing_authority="Chính phủ",
            issued_date=date(2025, 6, 30),
            effective_date=date(2025, 7, 1),
            effectiveness_status=(
                "Đang có hiệu lực; đã được sửa đổi, bổ sung bởi Nghị định 296/2026/NĐ-CP "
                "có hiệu lực từ 23/07/2026."
            ),
            applicable_provisions=[
                ApplicableProvision(
                    article="Điều 64",
                    clause="Khoản 1",
                    regulated_action=(
                        "Trong 07 ngày làm việc từ khi thông qua nghị quyết/quyết định giải thể, "
                        "gửi tài liệu ban đầu đến cơ quan đăng ký kinh doanh cấp tỉnh."
                    ),
                ),
                ApplicableProvision(
                    article="Điều 64",
                    clause="Khoản 2",
                    regulated_action=(
                        "Cơ quan đăng ký kinh doanh đăng tải và cập nhật tình trạng đang làm "
                        "thủ tục "
                        "giải thể trong 03 ngày làm việc."
                    ),
                ),
                ApplicableProvision(
                    article="Điều 64",
                    clause="Khoản 3, khoản 4, khoản 5",
                    regulated_action=(
                        "Hồ sơ cuối nộp trong 05 ngày làm việc kể từ ngày thanh toán hết nợ; phải "
                        "chấm dứt đơn vị phụ thuộc trước; cơ quan thuế phản hồi trong 02 ngày "
                        "làm việc."
                    ),
                ),
            ],
            summary=(
                "Quy trình giải thể doanh nghiệp tự nguyện theo các điểm a, b, c khoản 1 Điều 207 "
                "Luật Doanh nghiệp. Trường hợp thu hồi đăng ký hoặc quyết định của Tòa án "
                "áp dụng Điều 65."
            ),
            source_url="https://xaydungchinhsach.chinhphu.vn/toan-van-nghi-dinh-168-2025-nd-cp-ve-dang-ky-doanh-nghiep-119250702175708554.htm",
            change_note="Được sửa đổi, bổ sung bởi Nghị định 296/2026/NĐ-CP.",
        )

        company_law_amendment = LegalReference(
            document_name="Luật sửa đổi, bổ sung một số điều của Luật Doanh nghiệp",
            document_number="76/2025/QH15",
            issuing_authority="Quốc hội",
            issued_date=date(2025, 6, 17),
            effective_date=date(2025, 7, 1),
            effectiveness_status="Đang có hiệu lực từ ngày 01/07/2025.",
            applicable_provisions=[
                ApplicableProvision(
                    article="Điều 1",
                    clause="Khoản 23",
                    regulated_action=(
                        "Sửa đổi điểm c khoản 1 Điều 207 Luật Doanh nghiệp về trường hợp công ty "
                        "không còn đủ số lượng thành viên/cổ đông tối thiểu."
                    ),
                )
            ],
            summary=(
                "Văn bản sửa đổi Luật Doanh nghiệp; được nêu để xác định đúng bản hiện hành "
                "của Điều 207."
            ),
            source_url="https://vanban.chinhphu.vn/?classid=1&docid=214562&orggroupid=2&pageid=27160",
        )

        decree_296 = LegalReference(
            document_name="Nghị định sửa đổi, bổ sung một số điều của Nghị định 168/2025/NĐ-CP",
            document_number="296/2026/NĐ-CP",
            issuing_authority="Chính phủ",
            issued_date=date(2026, 7, 23),
            effective_date=date(2026, 7, 23),
            effectiveness_status="Đang có hiệu lực từ ngày 23/07/2026.",
            applicable_provisions=[
                ApplicableProvision(
                    article="Điều 1",
                    clause="Các khoản sửa đổi, bổ sung Nghị định 168/2025/NĐ-CP",
                    regulated_action=(
                        "Sửa đổi một số quy định đăng ký doanh nghiệp; khi áp dụng Nghị định 168 "
                        "cần đọc cùng các nội dung sửa đổi có hiệu lực từ 23/07/2026."
                    ),
                )
            ],
            summary=(
                "Văn bản sửa đổi một số điều của Nghị định 168/2025/NĐ-CP; cần đọc cùng văn bản "
                "gốc và đối chiếu nội dung sửa đổi được lưu trong kho luật chung."
            ),
            source_url="https://vanban.chinhphu.vn/?docid=218986&orggroupid=2&pageid=27160",
            change_note="Sửa đổi, bổ sung một số điều của Nghị định 168/2025/NĐ-CP.",
        )

        ecommerce_tax = LegalReference(
            document_name=(
                "Nghị định quy định quản lý thuế đối với hoạt động kinh doanh trên nền tảng "
                "thương mại điện tử, nền tảng số của hộ, cá nhân"
            ),
            document_number="117/2025/NĐ-CP",
            issuing_authority="Chính phủ",
            issued_date=date(2025, 6, 9),
            effective_date=date(2025, 7, 1),
            effectiveness_status="Đang có hiệu lực từ ngày 01/07/2025.",
            applicable_provisions=[],
            summary=(
                "Quy định quản lý thuế đối với hoạt động kinh doanh trên nền tảng thương mại "
                "điện tử, nền tảng số của hộ và cá nhân."
            ),
            source_url=(
                "https://congbao.chinhphu.vn/van-ban/nghi-dinh-so-117-2025-nd-cp-45045.htm"
            ),
        )
        tax_penalties_amendment = LegalReference(
            document_name=(
                "Nghị định sửa đổi, bổ sung một số điều của Nghị định 125/2020/NĐ-CP về xử "
                "phạt vi phạm hành chính về thuế, hóa đơn"
            ),
            document_number="310/2025/NĐ-CP",
            issuing_authority="Chính phủ",
            issued_date=date(2025, 12, 2),
            effective_date=date(2026, 1, 16),
            effectiveness_status="Đang có hiệu lực từ ngày 16/01/2026.",
            applicable_provisions=[],
            summary=(
                "Sửa đổi, bổ sung một số điều của Nghị định 125/2020/NĐ-CP về xử phạt vi phạm "
                "hành chính về thuế, hóa đơn."
            ),
            source_url=(
                "https://congbao.chinhphu.vn/van-ban/nghi-dinh-so-310-2025-nd-cp-46755.htm"
            ),
            change_note="Sửa đổi, bổ sung Nghị định 125/2020/NĐ-CP.",
        )
        private_economy_resolution = LegalReference(
            document_name=(
                "Nghị quyết về một số cơ chế, chính sách đặc biệt phát triển kinh tế tư nhân"
            ),
            document_number="198/2025/QH15",
            issuing_authority="Quốc hội",
            issued_date=date(2025, 5, 17),
            effective_date=date(2025, 5, 17),
            effectiveness_status="Đang có hiệu lực từ ngày 17/05/2025.",
            summary=(
                "Nghị quyết quy định một số cơ chế, chính sách đặc biệt phát triển kinh tế tư nhân."
            ),
            source_url=(
                "https://congbao.chinhphu.vn/van-ban/nghi-quyet-so-198-2025-qh15-44898.htm"
            ),
            applicable_provisions=[
                ApplicableProvision(
                    article="Điều 10",
                    clause="Khoản 7",
                    regulated_action=("Chấm dứt việc thu, nộp lệ phí môn bài từ ngày 01/01/2026."),
                )
            ],
            change_note=(
                "Nghị quyết nêu việc chấm dứt thu, nộp lệ phí môn bài từ ngày 01/01/2026."
            ),
        )

        return [
            (tax_close, law_108, "thuế mã số thuế chấm dứt đăng ký"),
            (tax_close, tax_decree, "thuế mã số thuế chấm dứt hoạt động nghĩa vụ"),
            (tax_close, tax_registration_rules, "thuế mã số thuế 24/ĐKT cơ quan thuế hồ sơ"),
            (hkd_close, hkd_termination, "đóng chấm dứt hộ kinh doanh HKD"),
            (new_hkd, hkd_registration, "thành lập lập mở đăng ký hộ mới hộ kinh doanh"),
            (company_close, company_law, "giải thể doanh nghiệp công ty dissolution"),
            (company_close, company_law_amendment, "giải thể luật doanh nghiệp sửa đổi"),
            (company_close, company_registration_rules, "giải thể đăng ký doanh nghiệp thủ tục"),
            (company_close, decree_296, "giải thể đăng ký nghị định sửa đổi 296"),
            (hkd_close, ecommerce_tax, "thương mại điện tử nền tảng số hộ cá nhân thuế"),
            (tax_close, tax_penalties_amendment, "xử phạt thuế hóa đơn sửa đổi 125"),
            (all_procedures, private_economy_resolution, "kinh tế tư nhân lệ phí môn bài"),
        ]
