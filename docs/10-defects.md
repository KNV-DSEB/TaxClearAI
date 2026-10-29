# Defects và giới hạn kiểm chứng

| ID | Mức độ | Tái hiện / vấn đề | Trạng thái |
|---|---|---|---|
| D01 | Major | Dùng DATABASE_URL mẫu: đăng nhập PostgreSQL thất bại | Đã xử lý bằng cụm dev/test riêng cổng 5543, không sửa server cũ |
| D02 | Major | Passlib 1.7.4 tự kiểm tra bcrypt 5 bằng mật khẩu >72 bytes khiến bootstrap lỗi | Đã sửa adapter dùng bcrypt có sẵn trực tiếp, giữ hashing bcrypt; test mật khẩu đa byte không bị cắt ngắn |
| D03 | Major | Alembic check báo lệch tên check constraints giữa model/migration | Đã đặt tên khớp, alembic check không còn phát sinh thao tác |
| D04 | Critical/High dependency | pnpm audit trên Next.js 16.3.1, Zod/Vite/Vitest cũ | Đã cập nhật Next 16.4.1, Zod 4.6.6, Vite 8.2.4, Vitest/coverage 4.1.12 và eslint-config-next tương ứng; audit sau cập nhật 0 advisory |
| D05 | Medium residual | Python-jose 3.5.0 vẫn có PYSEC-2026-4298/CVE-2026-85394, chưa có fix theo audit | Chưa vá upstream; app chỉ HS256 với secret ngẫu nhiên riêng, không dùng public/asymmetric key làm HMAC; không gọi audit Python sạch |
| D06 | Low residual | Transitive ecdsa 0.19.2 có Minerva/CVE-2024-23342, chưa có fix | App không dùng ECDSA signing/keygen/ECDH, HMAC-only; cần đánh giá lại nếu mở thuật toán |
| D07 | Low dev-only | Black 26.5.1 có CVE-2026-114134 trong GitHub Action use_pyproject | Đã cài/pin 26.10.1 và chạy kiểm tra; báo cáo audit trước vá giữ lại như bằng chứng lịch sử, kết quả audit môi trường mới cần đối chiếu riêng |
| D08 | Minor | Corepack/pnpm trỏ tệp pnpm.cjs không tồn tại | Đã tìm bản pnpm.mjs có sẵn; không cài pnpm mới; dùng đường dẫn này trong kiểm tra cuối |
| D09 | Chưa kiểm chứng một phần | Computer Use không xác định URL Chrome chắc chắn và dừng; sau phục hồi host browser vẫn không khả dụng | Khách xác nhận E2E thủ công S1/S2; E2E tự động/QA responsive và trình duyệt cụ thể vẫn chưa kiểm chứng; không dùng công cụ UI khác để vượt chặn |
| D10 | Minor | Hai warning lint có sẵn ở Image.test.tsx; cảnh báo Next workspace root/Vite config __dirname | Giữ nguyên các sửa bàn giao, không tắt rule để làm xanh; build/test vẫn phải đạt |
| D11 | Major release gate | Chưa có nguồn pháp luật/cây quyết định/checklist do cố vấn duyệt | Key đã cấp, Gemini đã gọi thật và khách chấp nhận S1/S2 nội bộ. Nội dung pháp lý vẫn chờ, chặn gọi MVP hướng dẫn hồ sơ thật hoàn chỉnh |
| D12 | Minor test | Hai test wizard chọn text trùng h2/legend và fail | Đã sửa dùng role heading, kiểm tra lại xanh; không disable test |
| D13 | Major trước dữ liệu thật | Hết hạn truy cập 7 ngày chưa phải purge vật lý; bảo vệ ổ đĩa/TLS production chưa xác minh | Đã công bố giới hạn trong UI/runbook; chỉ dữ liệu giả định local, cần chốt vận hành/xác nhận pháp lý trước nhận hồ sơ thật |
| D14 | Đã sửa, công cụ dev | Audit installed environment phát hiện pip 25.2 có bản vá | Đã nâng pip 26.2 và kiểm tra lại: không còn pip/Black trong findings; còn 2 advisory duy nhất ở ecdsa/python-jose |

Không có lỗi dữ liệu thật được ghi nhận vì chưa nhận dữ liệu thật. Danh sách này không có nghĩa sản phẩm đã qua pentest, UAT hay được phát hành.
