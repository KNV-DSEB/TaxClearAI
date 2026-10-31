"""AI phân loại (tình huống + dấu hiệu rủi ro trong câu hỏi)."""

import re
import unicodedata

RISK_LABELS = {
    "bi_co_quan_lien_he",
    "sai_lech_so_lieu",
    "no_ton_dong",
    "hoi_so_tien",
    "hoi_co_bi_phat",
    "ne_thue",
    "chuyen_nhuong_phuc_tap",
    "hoi_quyet_dinh_thay",
    "khong_chac_chan",
    "ngoai_pham_vi",
}
_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "khong_chac_chan",
        re.compile(
            r"(bo qua quy tac|in.{0,30}(system|sys) prompt|"
            r"tiet lo.{0,30}(system|sys) prompt|dong vai)"
        ),
    ),
    (
        "ne_thue",
        re.compile(
            r"\b(ne thue|tron thue|lach thue|giau doanh thu|che giau doanh thu|xoa dau vet|"
            r"khong bi (?:co quan )?thue phat hien|"
            r"khong bi phat hien.{0,50}(?:thue|so lieu|doanh thu|hoa don)|"
            r"(?:thue|so lieu|doanh thu|hoa don).{0,50}khong bi phat hien|"
            r"giam.{0,30}thue.{0,50}khong bi phat hien.{0,60}(?:sao ke|chenh lech)|"
            r"dong it thue hon|giam thue bang cach|khai thap (doanh thu|dt)|"
            r"(hoa don|hd) khong|(hoa don|hd) gia|"
            r"hop thuc hoa chi phi|"
            r"hop ly hoa chi phi.{0,50}(?:dong it thue hon|giam thue|ne thue|tron thue)|"
            r"\b(?:an|giau|bot|che)\b.{0,20}(?:doanh thu|dt)|"
            r"(?:doanh thu|dt).{0,20}(?:an bot|giau bot|che bot)|"
            r"khong khai.{0,20}(?:doanh thu|dt)|"
            r"(?:chia nho|tach nho).{0,30}(?:doanh thu|dt)|"
            r"(?:doanh thu|dt).{0,30}(?:chia nho|tach nho)|"
            r"(?:dung ten ho|nguoi khac dung ten|nhieu nguoi dung ten).{0,40}(?:thue|dong thue)|"
            r"(?:khoi dong|khoi chiu|tranh|ne).{0,20}thue|"
            r"(?:thue|co quan thue).{0,30}khong biet|"
            r"\b(?:xoa|huy|sua)\b.{0,20}(?:so sach|so ke toan|sach ke toan)|"
            r"(?:so sach|so ke toan).{0,20}(?:xoa|huy|sua))\b"
        ),
    ),
    (
        "bi_co_quan_lien_he",
        re.compile(
            r"\b(bi.{0,15}thanh tra thue|kiem tra thue|"
            r"nhan.{0,30}(thong bao|yeu cau giai trinh|quyet dinh|bien ban)|"
            r"(?:thong bao|yeu cau).{0,25}giai trinh|"
            r"quyet dinh.{0,20}truy thu|bien ban.{0,20}kiem tra|bi truy thu(?: thue)?|"
            r"co quan thue lien he|cqt lien he|cqt yeu cau giai trinh|"
            r"chi cuc thue lien he|co quan thue.{0,30}yeu cau giai trinh)\b"
        ),
    ),
    (
        "sai_lech_so_lieu",
        re.compile(r"\b(sai lech|chenh lech|khong khop|lech thuc te|sao ke.*(khac|lech))\b"),
    ),
    (
        "hoi_quyet_dinh_thay",
        re.compile(
            r"\b(tôi nen|toi nen).{0,30}(giai the|chuyen nhuong)|"
            r"\b(giai the|chuyen nhuong).{0,35}(hay|hoac).{0,35}(giai the|chuyen nhuong)|"
            r"\blam sao.{0,30}(do|giam|tranh).{0,15}bi phat|"
            r"\bnen chon.{0,25}(giai the|chuyen nhuong)"
        ),
    ),
    (
        "chuyen_nhuong_phuc_tap",
        re.compile(r"\b(tranh chap|nhieu co dong|nhieu cd|nhieu thanh vien|von gop lon)\b"),
    ),
    (
        "no_ton_dong",
        re.compile(
            r"\b(no thue|no ton dong|(hoa don|hd) ton|bhxh no|tien phat con no|"
            r"thanh ly tai san)\b"
        ),
    ),
    (
        "ngoai_pham_vi",
        re.compile(
            r"\b(thoi tiet|ket qua bong da|kq bong da|bau cu|tong thong|mon an|du lich|"
            r"dinh luat|bai tho|gia dien thoai|bo phim|trong cay)\b"
        ),
    ),
    (
        "hoi_co_bi_phat",
        re.compile(
            r"\b(co bi(?: xu)? phat khong|co the bi phat khong|co bi xu ly vi pham khong)\b"
        ),
    ),
    (
        "hoi_so_tien",
        re.compile(
            r"\b(?!.*\bbao nhieu\s+(?:ngay|thang|nam|thoi\s+gian|lau)\b)("
            r"bao nhieu (tien|thue|phi|le phi|phat)|"
            r"(?:phi|le phi).{0,20}bao nhieu(?!\s+(ngay|ban|nguoi|lan|buoc|nam|thang|ky)\b)|"
            r"bao nhieu\s+(phi|le phi)\b|"
            r"phi\s+(la\s+)?bao nhieu\b|"
            r"(?:mat|ton|het).{0,15}bao nhieu(?!\s+(ngay|ban|nguoi|lan|buoc|nam|thang|ky)\b)|"
            r"gia.{0,15}bao nhieu(?!\s+(ngay|ban|nguoi|lan|buoc|nam|thang|ky)\b)|"
            r"(?:muc )?phat.{0,35}(?:bao nhieu(?!\s+(ngay|lan|buoc|nam|thang|ky|loai|giay to)\b)|"
            r"bn)\b|"
            r"phat.{0,35}may phan tram|"
            r"phai nop bao nhieu(?!\s+(ngay|lan|buoc|nam|thang|ky|to khai|ho so|giay to)\b)|"
            r"tinh thue|tinh tien phat|muc phat bao nhieu|"
            r"chi phi.{0,20}bao nhieu(?!\s+(ngay|ban|nguoi|lan|buoc|nam|thang|ky)\b)|"
            r"le phi.{0,20}bao nhieu(?!\s+(ngay|ban|nguoi|lan|buoc|nam|thang|ky)\b)|"
            r"thue suat|uoc luong so tien|"
            r"so tien.{0,30}(thue|bao nhieu(?!\s+(ngay|lan|buoc|nam|thang|ky)\b))|"
            r"(muc )?thue bao nhieu|thue (gtgt|tndn|tncn) bao nhieu|"
            r"phan tram.{0,30}thue|thue.{0,30}phan tram)\b"
        ),
    ),
)


def normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFC", text).lower()
    normalized = normalized.replace("đ", "d")
    decomposed = unicodedata.normalize("NFD", normalized)
    unaccented = "".join(char for char in decomposed if unicodedata.category(char) != "Mn")
    return re.sub(r"\s+", " ", unaccented).strip()


def detect_risk_label(text: str) -> str | None:
    normalized = normalize_text(text)
    return next((label for label, pattern in _PATTERNS if pattern.search(normalized)), None)


def detect_risk_label_at_start(text: str) -> str | None:
    """Return a guardrail label only when its pattern begins at the supplied text start."""
    normalized = normalize_text(text)
    return next((label for label, pattern in _PATTERNS if pattern.match(normalized)), None)
