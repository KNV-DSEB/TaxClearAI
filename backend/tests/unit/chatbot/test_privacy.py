import pytest

from src.modules.chatbot.guardrail import detect_risk_label
from src.modules.chatbot.privacy import redact_sensitive_data

IDENTITY_CASES = [
    ("Tôi tên là Nguyễn Văn An, hồ sơ đang cần xử lý.", "Nguyễn Văn An"),
    ("tôi tên là nguyễn văn an, hồ sơ đang cần xử lý.", "nguyễn văn an"),
    ("toi ten la nguyen van an, ho so dang can xu ly.", "nguyen van an"),
    ("toi la vuong thi a, ho so dang can xu ly.", "vuong thi a"),
    ("Tên tôi là tran thi binh.", "tran thi binh"),
    ("Họ tên: Lê Thị Hoa.", "Lê Thị Hoa"),
    ("Chủ hộ: pham van minh.", "pham van minh"),
    ("Người đại diện: dang thi mai.", "dang thi mai"),
    ("Ông Nguyen Van A đã liên hệ.", "Nguyen Van A"),
    ("Bà Trần Thị Lan đã liên hệ.", "Trần Thị Lan"),
    ("Anh Hoang Duc Long.", "Hoang Duc Long"),
    ("Chị Võ Thị Ngọc.", "Võ Thị Ngọc"),
    ("Nguyễn Văn B gửi câu hỏi.", "Nguyễn Văn B"),
    ("tôi tên là tran thi c, gui cau hoi.", "tran thi c"),
    ("Email: an@example.vn", "an@example.vn"),
    ("Số điện thoại 0912345678", "0912345678"),
    ("MST 0123456789", "0123456789"),
    ("MST 0123456789012", "0123456789012"),
    ("CCCD 012345678901", "012345678901"),
    ("Mã tham chiếu 1234567890", "1234567890"),
    (
        "Tôi tên là Nguyễn Văn An, CCCD 012345678901, địa chỉ: 12 Đường ABC.",
        "12 Đường ABC",
    ),
]

NORMAL_CASES = [
    "Hộ Kinh Doanh Cá Thể Đăng Ký Tại Quận Ba Đình",
    "Hộ kinh doanh đăng ký tại Quận Ba Đình.",
    "Doanh nghiệp đang hoạt động tại Thành phố Hồ Chí Minh.",
    "Cơ quan thuế tiếp nhận hồ sơ tại Quận Lê Chân.",
    "Quận Ba Đình tiếp nhận hồ sơ.",
    "Huyện Đan Phượng có địa điểm kinh doanh.",
    "Phường Tân Định là nơi đăng ký.",
    "Xã Hòa Bình có hộ kinh doanh.",
    "Tỉnh Đắk Lắk có doanh nghiệp nhỏ.",
    "Thành phố Hồ Chí Minh là địa danh được nêu trong câu hỏi.",
    "Ông nguyen van a đã liên hệ.",
    "Anh hoang duc long.",
    "Chị võ thị ngọc.",
    "Luật [CHƯA XÁC ĐỊNH]",
    "Nghị định [CHƯA XÁC ĐỊNH]",
    "Thông tư [CHƯA XÁC ĐỊNH]",
    "Hộ kinh doanh và Doanh nghiệp là thuật ngữ nghiệp vụ.",
    "Hồ sơ cần kiểm tra lý do và điều kiện.",
    "Thời gian xử lý hồ sơ là bao lâu?",
]


@pytest.mark.parametrize(("source", "raw_value"), IDENTITY_CASES)
def test_redacts_identity_data_and_contextual_names(source: str, raw_value: str) -> None:
    assert raw_value not in redact_sensitive_data(source)


@pytest.mark.parametrize("source", NORMAL_CASES)
def test_preserves_business_terms_locations_and_normal_capitalization(source: str) -> None:
    assert redact_sensitive_data(source) == source


def test_redacts_email_tax_id_cccd_phone_name_and_address() -> None:
    source = (
        "Tôi tên là Nguyễn Văn An, MST: 0123456789, CCCD 012345678901, "
        "địa chỉ: 12 Đường ABC, gọi 0912345678, email an@example.vn"
    )

    redacted = redact_sensitive_data(source)

    for raw_value in (
        "Nguyễn Văn An",
        "0123456789",
        "012345678901",
        "12 Đường ABC",
        "0912345678",
        "an@example.vn",
    ):
        assert raw_value not in redacted


def test_honorific_redaction_preserves_words_after_the_name() -> None:
    source = "Ông Minh giám đốc công ty ABC muốn giải thể"

    redacted = redact_sensitive_data(source)

    assert "Minh" not in redacted
    assert "giám đốc công ty ABC muốn giải thể" in redacted


def test_honorific_redaction_preserves_ordinary_lowercase_words() -> None:
    source = "chị Lan bán tạp hóa đã đăng ký hộ"

    redacted = redact_sensitive_data(source)

    assert "Lan" not in redacted
    assert "bán tạp hóa đã đăng ký hộ" in redacted


def test_explicit_name_capture_stops_before_risk_terms() -> None:
    source = "Tôi tên là lan giấu doanh thu"

    redacted = redact_sensitive_data(source)

    assert "lan" not in redacted
    assert "giấu doanh thu" in redacted


RISK_PREFIXES = [
    "Anh Hùng",
    "chị Lan",
    "Tôi là Nguyễn Văn An,",
    "tôi tên là lan",
    "bà Hoa",
    "ông Nam",
    "Chủ hộ: Lê Thị Mai",
    "Tên tôi là Trần Minh Tuấn",
    "Họ tên: pham van minh",
    "Cô Hà",
    "Chú Bình",
    "anh Trần Văn B",
]

RISK_SUFFIXES = [
    "bị thanh tra thuế",
    "bị truy thu thuế",
    "nợ thuế",
    "muốn né thuế",
    "giấu doanh thu",
    "kê khai không khớp sao kê",
    "có tranh chấp nhiều cổ đông",
    "hóa đơn khống",
]


@pytest.mark.parametrize("prefix", RISK_PREFIXES)
@pytest.mark.parametrize("suffix", RISK_SUFFIXES)
def test_redaction_preserves_guardrail_label_for_name_and_risk_combinations(
    prefix: str, suffix: str
) -> None:
    source = f"{prefix} {suffix}"

    original_label = detect_risk_label(source)
    redacted_label = detect_risk_label(redact_sensitive_data(source))

    assert original_label is not None, source
    assert redacted_label == original_label, source
