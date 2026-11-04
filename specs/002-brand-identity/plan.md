# Plan 002 — Logo và bộ nhận diện

Trạng thái: **Approved** (2026-11-04). Đầu vào: `spec.md`, `.specify/memory/constitution.md`.

## Nghiên cứu và quyết định thiết kế
Tám vòng phác, ảnh so sánh lưu tại `docs/brand/exploration/`:

| Vòng | Hướng | Kết quả |
|---|---|---|
| 1 | Nét gỡ, dòng hồ sơ, vòng mở (nét mảnh, có tick) | Khách: quá đơn giản, nhạt |
| 2–3 | Nút gỡ đan, bìa hồ sơ, hai tờ chồng (khối đặc, có tick) | Khách: tick quá quen, màu và chữ chưa có cá tính |
| 4 | C pha lê, lăng kính, bình minh (trừu tượng, teal + vàng nghệ) | Chốt C2, đã áp dụng; sau đó khách: chưa đặc sắc, chưa cuốn mắt |
| 5 | Tia sáng C, C kính, monogram T–C, nút gỡ bứt phá, dải giấy gấp (màu chuyển, phát quang) | Khách đưa brief mới: C + khiên + tick/đường đi lên |
| 6 | Khiên mở + tick, khiên mở + đường đi lên, khiên đặc + C + tick | Khách: thiếu đặc sắc |
| 7 | Tick khép khiên, khiên hồ sơ (vát hai mặt, góc gấp giấy), khiên hồ sơ tick bứt phá | Khách: chữ C nhạt nhòa |
| 8 | C trắng nổi khối, **C vàng nghệ**, C ôm khiên, rãnh C | **Chốt C2 vòng 8 — khiên hồ sơ, chữ C vàng nghệ** |

**Ý tưởng (bản chốt):** một chiếc **khiên** teal vát hai mặt (niềm tin), góc trên phải gấp như tờ giấy (hồ sơ); giữa khiên là **chữ C** khối đặc màu vàng nghệ, hai đầu cắt vát song song nếp gấp (Clear, nhân vật chính, hút mắt đầu tiên); trong lòng chữ C là **dấu tick trắng** (xử lý chính xác, minh bạch). Thứ tự đọc: khiên → C → tick. Màu nóng duy nhất dồn vào chữ C.

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
