"""Nạp hồ sơ đối tác MINH HỌA (không phải người/đơn vị thật) cho phát triển và trình diễn."""

import asyncio
from uuid import NAMESPACE_URL, uuid5

from src.core.database import _session_factory
from src.modules.experts.domain import ExpertSeed
from src.modules.experts.repository import ExpertRepository

EXPERTS_DATA = [
    ExpertSeed(
        id=uuid5(NAMESPACE_URL, "taxclearai:expert:minh-khang"),
        full_name="Đối tác mẫu A · Công ty kế toán – đại lý thuế",
        title="Vai trò minh họa: Công ty dịch vụ kế toán và đại lý thuế",
        organization="Hồ sơ minh họa, không phải đơn vị thật",
        bio=(
            "15 năm kinh nghiệm; nhận trọn gói quyết toán thuế, hoàn thiện sổ sách và giải thể "
            "doanh nghiệp. Hồ sơ mẫu, chưa được Tax Clear xác minh độc lập."
        ),
        specializations="Quyết toán thuế, Giải thể DN, Dọn sổ sách",
        location="Hà Nội",
        experience_years=15,
        consultation_fee_text="Phí minh họa: Từ 3.500.000 đ / hồ sơ",
        partner_type="accounting_firm",
        services_offered="Quyết toán giải thể, Dọn sổ sách, Báo cáo tài chính, Đóng mã số thuế",
    ),
    ExpertSeed(
        id=uuid5(NAMESPACE_URL, "taxclearai:expert:ac-partner"),
        full_name="Đối tác mẫu B · Công ty kế toán – đại lý thuế",
        title="Vai trò minh họa: Công ty dịch vụ kế toán",
        organization="Hồ sơ minh họa, không phải đơn vị thật",
        bio=(
            "Chuyên dọn dẹp sổ sách tồn đọng và lập báo cáo tài chính giải thể cho doanh nghiệp "
            "nhóm B2. Hồ sơ mẫu, chưa được Tax Clear xác minh độc lập."
        ),
        specializations="Dọn sổ sách, Báo cáo tài chính, Giải thể DN B2",
        location="TP. Hồ Chí Minh",
        experience_years=12,
        consultation_fee_text="Phí minh họa: Từ 4.000.000 đ / hồ sơ",
        partner_type="accounting_firm",
        services_offered="Dọn sổ sách, Báo cáo tài chính, Quyết toán giải thể",
    ),
    ExpertSeed(
        id=uuid5(NAMESPACE_URL, "taxclearai:expert:le-thu-trang"),
        full_name="Đối tác mẫu C · Kế toán viên",
        title="Vai trò minh họa: Kế toán trưởng / Chứng chỉ Đại lý Thuế",
        organization="Hồ sơ minh họa, không phải đơn vị thật",
        bio=(
            "11 năm kinh nghiệm; chuyên gỡ rối thuế hộ kinh doanh A2/A3 và doanh nghiệp vừa và "
            "nhỏ. Hồ sơ mẫu, chưa được Tax Clear xác minh độc lập."
        ),
        specializations="Hộ kinh doanh A2/A3, Quyết toán thuế, Sổ sách kế toán",
        location="TP. Hồ Chí Minh",
        experience_years=11,
        consultation_fee_text="Phí minh họa: Từ 1.500.000 đ / hồ sơ",
        partner_type="accountant",
        services_offered="Rà soát hóa đơn, Kê khai bổ sung, Sổ sách kế toán",
    ),
    ExpertSeed(
        id=uuid5(NAMESPACE_URL, "taxclearai:expert:nguyen-van-hung"),
        full_name="Đối tác mẫu D · Kế toán viên",
        title="Vai trò minh họa: CPA Việt Nam",
        organization="Hồ sơ minh họa, không phải đơn vị thật",
        bio=(
            "8 năm kinh nghiệm kiểm toán và kế toán thuế trọn gói cho hộ kinh doanh và doanh "
            "nghiệp nhỏ. Hồ sơ mẫu, chưa được Tax Clear xác minh độc lập."
        ),
        specializations="Kiểm toán, Kế toán thuế, Sổ sách kế toán",
        location="Toàn quốc",
        experience_years=8,
        consultation_fee_text="Phí minh họa: Từ 2.000.000 đ / hồ sơ",
        partner_type="accountant",
        services_offered="Kế toán thuế trọn gói, Rà soát hóa đơn, Báo cáo tài chính",
    ),
    ExpertSeed(
        id=uuid5(NAMESPACE_URL, "taxclearai:expert:do-trong"),
        full_name="Đối tác mẫu E · Tư vấn thuế – pháp lý",
        title="Vai trò minh họa: Luật sư thành viên",
        organization="Hồ sơ minh họa, không phải đơn vị thật",
        bio=(
            "12 năm kinh nghiệm tư vấn thủ tục giải thể, tranh chấp tài sản và tái cấu trúc. "
            "Hồ sơ mẫu, chưa được Tax Clear xác minh độc lập."
        ),
        specializations="Giải thể DN B2, Tranh chấp tài sản, Tái cấu trúc",
        location="Hà Nội",
        experience_years=12,
        consultation_fee_text="Phí minh họa: Từ 5.000.000 đ / hồ sơ",
        partner_type="tax_consultant",
        services_offered="Tư vấn pháp lý thuế, Tranh chấp tài sản, Thủ tục giải thể",
    ),
    ExpertSeed(
        id=uuid5(NAMESPACE_URL, "taxclearai:expert:tran-mai-anh"),
        full_name="Đối tác mẫu F · Tư vấn thuế – pháp lý",
        title="Vai trò minh họa: Luật sư tư vấn doanh nghiệp và thuế",
        organization="Hồ sơ minh họa, không phải đơn vị thật",
        bio=(
            "Chuyên chuyển đổi mô hình, đóng hộ cũ và mở hộ mới; 10 năm kinh nghiệm tư vấn. "
            "Hồ sơ mẫu, chưa được Tax Clear xác minh độc lập."
        ),
        specializations="Chuyển đổi mô hình, Đóng hộ kinh doanh, Thuế",
        location="TP. Hồ Chí Minh",
        experience_years=10,
        consultation_fee_text="Phí minh họa: Từ 2.500.000 đ / hồ sơ",
        partner_type="tax_consultant",
        services_offered="Tư vấn pháp lý thuế, Chuyển đổi mô hình, Đóng hộ kinh doanh",
    ),
    ExpertSeed(
        id=uuid5(NAMESPACE_URL, "taxclearai:expert:nguyen-thi-bich-lien"),
        full_name="Đối tác mẫu G · Tư vấn thuế – pháp lý",
        title="Vai trò minh họa: Chuyên gia Đại lý Thuế",
        organization="Hồ sơ minh họa, không phải đơn vị thật",
        bio=(
            "Hồ sơ chuyên gia mẫu do Tax Clear cung cấp. Có 15 năm kinh nghiệm theo dữ liệu "
            "đầu vào; hỗ trợ quyết toán thuế và hộ kinh doanh A2/A3. Chưa được Tax Clear "
            "xác minh độc lập."
        ),
        specializations="Quyết toán thuế, Hộ kinh doanh A2/A3",
        location="TP. Hồ Chí Minh",
        experience_years=15,
        consultation_fee_text="Phí minh họa: Từ 1.500.000 đ / hồ sơ",
        partner_type="tax_consultant",
        services_offered="Quyết toán thuế, Kê khai thuế hộ kinh doanh, Rà soát hóa đơn",
    ),
    ExpertSeed(
        id=uuid5(NAMESPACE_URL, "taxclearai:expert:le-hoang-nam"),
        full_name="Đối tác mẫu H · Tư vấn thuế – pháp lý",
        title="Vai trò minh họa: CPA Việt Nam",
        organization="Hồ sơ minh họa, không phải đơn vị thật",
        bio=(
            "Hồ sơ chuyên gia mẫu do Tax Clear cung cấp. Có 9 năm kinh nghiệm theo dữ liệu "
            "đầu vào; "
            "hỗ trợ hóa đơn VAT và sổ sách kế toán. Thông tin chứng chỉ và hành nghề chưa được "
            "Tax Clear xác minh độc lập."
        ),
        specializations="Hóa đơn VAT, Sổ sách kế toán",
        location="Toàn quốc",
        experience_years=9,
        consultation_fee_text="Phí minh họa: Từ 2.000.000 đ / hồ sơ",
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
