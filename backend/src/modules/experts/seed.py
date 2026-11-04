"""Nạp hồ sơ đối tác mẫu cho môi trường phát triển."""

import asyncio
from uuid import NAMESPACE_URL, uuid5

from src.core.database import _session_factory
from src.modules.experts.domain import ExpertSeed
from src.modules.experts.repository import ExpertRepository

EXPERTS_DATA = [
    ExpertSeed(
        id=uuid5(NAMESPACE_URL, "taxclearai:expert:minh-khang"),
        full_name="Công ty TNHH Kế toán & Đại lý Thuế Minh Khang",
        title="Công ty dịch vụ kế toán và đại lý thuế",
        organization="Minh Khang",
        bio=(
            "15 năm kinh nghiệm; nhận trọn gói quyết toán thuế, hoàn thiện sổ sách và giải thể "
            "doanh nghiệp. Hồ sơ mẫu, chưa được Tax Clear AI xác minh độc lập."
        ),
        specializations="Quyết toán thuế, Giải thể DN, Dọn sổ sách",
        location="Hà Nội",
        experience_years=15,
        consultation_fee_text="Từ 3.500.000 đ / hồ sơ",
        partner_type="accounting_firm",
        services_offered="Quyết toán giải thể, Dọn sổ sách, Báo cáo tài chính, Đóng mã số thuế",
    ),
    ExpertSeed(
        id=uuid5(NAMESPACE_URL, "taxclearai:expert:ac-partner"),
        full_name="Công ty Dịch vụ Kế toán & Thuế Á Châu (A&C Partner)",
        title="Công ty dịch vụ kế toán",
        organization="A&C Partner",
        bio=(
            "Chuyên dọn dẹp sổ sách tồn đọng và lập báo cáo tài chính giải thể cho doanh nghiệp "
            "nhóm B2. Hồ sơ mẫu, chưa được Tax Clear AI xác minh độc lập."
        ),
        specializations="Dọn sổ sách, Báo cáo tài chính, Giải thể DN B2",
        location="TP. Hồ Chí Minh",
        experience_years=12,
        consultation_fee_text="Từ 4.000.000 đ / hồ sơ",
        partner_type="accounting_firm",
        services_offered="Dọn sổ sách, Báo cáo tài chính, Quyết toán giải thể",
    ),
    ExpertSeed(
        id=uuid5(NAMESPACE_URL, "taxclearai:expert:le-thu-trang"),
        full_name="Bà Lê Thu Trang",
        title="Kế toán trưởng / Chứng chỉ Đại lý Thuế",
        organization="Kế toán dịch vụ độc lập",
        bio=(
            "11 năm kinh nghiệm; chuyên gỡ rối thuế hộ kinh doanh A2/A3 và doanh nghiệp vừa và "
            "nhỏ. Hồ sơ mẫu, chưa được Tax Clear AI xác minh độc lập."
        ),
        specializations="Hộ kinh doanh A2/A3, Quyết toán thuế, Sổ sách kế toán",
        location="TP. Hồ Chí Minh",
        experience_years=11,
        consultation_fee_text="Từ 1.500.000 đ / hồ sơ",
        partner_type="accountant",
        services_offered="Rà soát hóa đơn, Kê khai bổ sung, Sổ sách kế toán",
    ),
    ExpertSeed(
        id=uuid5(NAMESPACE_URL, "taxclearai:expert:nguyen-van-hung"),
        full_name="Ông Nguyễn Văn Hùng",
        title="CPA Việt Nam",
        organization="Kế toán dịch vụ độc lập",
        bio=(
            "8 năm kinh nghiệm kiểm toán và kế toán thuế trọn gói cho hộ kinh doanh và doanh "
            "nghiệp nhỏ. Hồ sơ mẫu, chưa được Tax Clear AI xác minh độc lập."
        ),
        specializations="Kiểm toán, Kế toán thuế, Sổ sách kế toán",
        location="Toàn quốc",
        experience_years=8,
        consultation_fee_text="Từ 2.000.000 đ / hồ sơ",
        partner_type="accountant",
        services_offered="Kế toán thuế trọn gói, Rà soát hóa đơn, Báo cáo tài chính",
    ),
    ExpertSeed(
        id=uuid5(NAMESPACE_URL, "taxclearai:expert:do-trong"),
        full_name="Luật sư Đỗ Trọng",
        title="Luật sư thành viên",
        organization="Đoàn Luật sư Hà Nội",
        bio=(
            "12 năm kinh nghiệm tư vấn thủ tục giải thể, tranh chấp tài sản và tái cấu trúc. "
            "Hồ sơ mẫu, chưa được Tax Clear AI xác minh độc lập."
        ),
        specializations="Giải thể DN B2, Tranh chấp tài sản, Tái cấu trúc",
        location="Hà Nội",
        experience_years=12,
        consultation_fee_text="Từ 5.000.000 đ / hồ sơ",
        partner_type="tax_consultant",
        services_offered="Tư vấn pháp lý thuế, Tranh chấp tài sản, Thủ tục giải thể",
    ),
    ExpertSeed(
        id=uuid5(NAMESPACE_URL, "taxclearai:expert:tran-mai-anh"),
        full_name="Luật sư Trần Mai Anh",
        title="Luật sư tư vấn doanh nghiệp và thuế",
        organization="Đơn vị tư vấn độc lập",
        bio=(
            "Chuyên chuyển đổi mô hình, đóng hộ cũ và mở hộ mới; 10 năm kinh nghiệm tư vấn. "
            "Hồ sơ mẫu, chưa được Tax Clear AI xác minh độc lập."
        ),
        specializations="Chuyển đổi mô hình, Đóng hộ kinh doanh, Thuế",
        location="TP. Hồ Chí Minh",
        experience_years=10,
        consultation_fee_text="Từ 2.500.000 đ / hồ sơ",
        partner_type="tax_consultant",
        services_offered="Tư vấn pháp lý thuế, Chuyển đổi mô hình, Đóng hộ kinh doanh",
    ),
    ExpertSeed(
        id=uuid5(NAMESPACE_URL, "taxclearai:expert:nguyen-thi-bich-lien"),
        full_name="Bà Nguyễn Thị Bích Liên",
        title="Chuyên gia Đại lý Thuế",
        organization="Đại lý Thuế Minh Khang",
        bio=(
            "Hồ sơ chuyên gia mẫu do Tax Clear AI cung cấp. Có 15 năm kinh nghiệm theo dữ liệu "
            "đầu vào; hỗ trợ quyết toán thuế và hộ kinh doanh A2/A3. Chưa được Tax Clear AI "
            "xác minh độc lập."
        ),
        specializations="Quyết toán thuế, Hộ kinh doanh A2/A3",
        location="TP. Hồ Chí Minh",
        experience_years=15,
        consultation_fee_text="Từ 1.500.000 đ / hồ sơ",
        partner_type="tax_consultant",
        services_offered="Quyết toán thuế, Kê khai thuế hộ kinh doanh, Rà soát hóa đơn",
    ),
    ExpertSeed(
        id=uuid5(NAMESPACE_URL, "taxclearai:expert:le-hoang-nam"),
        full_name="Ông Lê Hoàng Nam",
        title="CPA Việt Nam",
        organization="Chuyên gia tư vấn độc lập · Hồ sơ mẫu",
        bio=(
            "Hồ sơ chuyên gia mẫu do Tax Clear AI cung cấp. Có 9 năm kinh nghiệm theo dữ liệu "
            "đầu vào; "
            "hỗ trợ hóa đơn VAT và sổ sách kế toán. Thông tin chứng chỉ và hành nghề chưa được "
            "Tax Clear AI xác minh độc lập."
        ),
        specializations="Hóa đơn VAT, Sổ sách kế toán",
        location="Toàn quốc",
        experience_years=9,
        consultation_fee_text="Từ 2.000.000 đ / hồ sơ",
        partner_type="tax_consultant",
        services_offered="Rà soát hóa đơn VAT, Hoàn thiện sổ sách kế toán, Báo cáo tài chính",
    ),
]


async def seed() -> None:
    async with _session_factory() as session:
        repository = ExpertRepository(session)
        await repository.seed_experts(EXPERTS_DATA)
    print("Đã nạp 8 hồ sơ đối tác mẫu.")


if __name__ == "__main__":
    asyncio.run(seed())
