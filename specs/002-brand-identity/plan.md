# Plan 002 — Logo và bộ nhận diện

Trạng thái: **Approved** (2026-11-04). Đầu vào: `spec.md`, `.specify/memory/constitution.md`.

## Nghiên cứu và quyết định thiết kế
Bốn vòng phác, ảnh so sánh lưu tại `docs/brand/exploration/`:

| Vòng | Hướng | Kết quả |
|---|---|---|
| 1 | Nét gỡ, dòng hồ sơ, vòng mở (nét mảnh, có tick) | Khách: quá đơn giản, nhạt |
| 2–3 | Nút gỡ đan, bìa hồ sơ, hai tờ chồng (khối đặc, có tick) | Khách: tick quá quen, màu và chữ chưa có cá tính |
| 4 | C pha lê, lăng kính, bình minh (trừu tượng, teal + vàng nghệ) | **Chốt C2 — C pha lê** |

**Ý tưởng:** chữ C của *Clear* dựng từ 14 mặt cắt như một viên pha lê. Ánh sáng chiếu từ góc trên trái nên mỗi mặt có độ sáng theo hướng của nó; ánh vàng nghệ bắt ở mép khe mở. Hồ sơ rối được "mài" thành một khối rõ ràng, có giá trị. Nguyên lý tham chiếu: biểu tượng hình học nhiều lớp như Mastercard, Chase; một điểm nhấn màu duy nhất.

**Wordmark:** Be Vietnam Pro SemiBold (OFL, font do người Việt thiết kế), chuyển thành đường vector. Chữ **x** vẽ riêng: hai nét đan chéo, một nét màu vàng nghệ. "AI" viết nhỏ, màu teal.

## Hệ thống
- **Màu:** thang teal 7 bậc (`#0a3a33` → `#c9f0e2`), vàng nghệ `#f4a23c` / `#e07f1f` chỉ dùng cho đồ họa và điểm nhấn (không dùng cho chữ trên nền trắng vì tương phản thấp), mực `#123a35`, nền mint `#eef7f3`.
- **Chữ:** Be Vietnam Pro cho tiêu đề và giao diện (qua `next/font/google`, có sẵn trong Next.js, không thêm package).
- **Nguồn sự thật:** script dựng logo sinh mọi SVG/PNG từ một định nghĩa hình học; web dùng component sinh từ cùng dữ liệu.

## Cấu trúc file
- `docs/brand/` — bản gốc SVG, PNG xuất, ấn phẩm, `README.md` hướng dẫn nhanh, `exploration/`.
- `docs/brand/tools/build_brand.py` — script dựng tài sản (cần Python, fontTools, Playwright có sẵn trên máy).
- `frontend/public/brand/` — logo dùng trên web; `frontend/src/app/icon.svg`, `apple-icon.png`, `favicon.ico`, `opengraph-image.png`.
- `frontend/src/components/features/brand/` — `BrandMark`, `BrandLogo` (SVG nội tuyến), `AnimatedMark`.
- Design System artifact "Tax Clear AI Brand" — trang hướng dẫn thương hiệu cho nhóm.

## Rủi ro
- Vàng nghệ trên nền trắng không đạt 4.5:1 cho chữ → chỉ dùng cho hình.
- Logo động phải tắt khi `prefers-reduced-motion`.
- Chưa tra cứu nhãn hiệu trùng; ghi rõ trong hướng dẫn là chưa đăng ký.
