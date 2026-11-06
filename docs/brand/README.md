# Thương hiệu Tax Clear

Biểu tượng **khiên hồ sơ**: khiên teal vát hai mặt, góc trên phải gấp như tờ giấy; giữa khiên là chữ C vàng nghệ (Clear), trong lòng chữ C là dấu tick trắng. Wordmark Be Vietnam Pro SemiBold, chữ x vẽ riêng với một nét vàng nghệ. Hướng dẫn đầy đủ: artifact "Tax Clear Brand" (https://claude.ai/artifact/D2E1ZH8ANWJZV6JsSTVUqR); quá trình và quyết định: `specs/002-brand-identity/`.

| Thư mục | Nội dung |
|---|---|
| `logo/` | SVG gốc: ngang, dọc, wordmark, biểu tượng × màu, nền tối, một màu tối, một màu trắng; biểu tượng nhỏ (bỏ đổ bóng) cho cỡ ≤ 32 px |
| `png/` | PNG xuất (logo ×4), favicon 16/32/48 + `favicon.ico`, icon ứng dụng 180/192/512 |
| `social/` | Ảnh OG 1200×630, ảnh đại diện 1080, cover Facebook, banner LinkedIn, slide bìa 1920×1080 |
| `animated/` | Logo động SVG/CSS (tắt khi giảm chuyển động) |
| `fonts/` | Be Vietnam Pro (SIL OFL, xem `OFL.txt`) |
| `exploration/` | Bảng so sánh 8 vòng phác và ảnh web sau khi áp logo |
| `tools/build_brand.py` | Dựng lại toàn bộ tài sản và `frontend/src/components/features/brand/brand-geometry.ts` |

Dựng lại: `python docs/brand/tools/build_brand.py` (cần fontTools, Pillow, Playwright Chromium). Không sửa tay file SVG/PNG hay `brand-geometry.ts`; sửa hình học hoặc màu trong script.

Màu chính: teal `#17705f` / `#0f5a4c`, vàng nghệ `#f4a23c` (chỉ cho hình), chữ vàng nghệ trên nền sáng `#a3550c`, mực `#123a35`, nền mint `#eef7f3`.
Chưa tra cứu và chưa đăng ký nhãn hiệu.

## Đổi tên hiển thị (2026-11-06)
Bỏ hậu tố "AI" khỏi wordmark và tên hiển thị: **Tax Clear**. Tính năng trợ lý vẫn gọi là "Hỏi đáp cùng AI". Tên file tài sản (`tax-clear-ai-*.svg/png`), tên repo và tên gói giữ nguyên để không làm gãy đường dẫn; sinh lại tài sản bằng `python docs/brand/tools/build_brand.py`.
