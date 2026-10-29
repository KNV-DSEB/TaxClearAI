# Nhật ký dùng thử

## S1 — khách đã chạy thử và chấp nhận luồng nội bộ

- Người thử: khách hàng/trưởng nhóm trong phiên, không gán đây là khách doanh nghiệp thật.
- Bản local: khảo sát 11 câu, tổng hợp và 19 mục gợi ý có nhãn chờ cố vấn; lưu PostgreSQL, cập nhật và mở lại checklist.
- Phản hồi nguyên văn: “Đã thử, luồng phù hợp để làm S2”, trả lời yêu cầu hoàn tất khảo sát, đổi trạng thái và tải lại. Không có yêu cầu sửa cụ thể trong phản hồi này.
- Kiểm tra thực tế trình duyệt: chưa hoàn tất. Computer Use dừng do không xác định URL Chrome đủ chắc chắn; không dùng kết quả test component thay bằng chứng browser E2E.
- Quyết định: đã sang S2 sau phản hồi S1, đúng thứ tự cổng. Chưa có nguồn luật cố vấn duyệt.

## S2 — khách đã chạy thử và chấp nhận bản thử nội bộ

- Khách đã thêm Gemini key trực tiếp vào backend/.env; key không được gửi trong chat hoặc commit.
- Gọi Gemini thật qua adapter và HTTP endpoint đã trả 200, providerUsed=true, dẫn product-guide. Chỉ dùng câu hỏi giả định về cách sử dụng checklist.
- Phản hồi nguyên văn: “Đã thử S2, phù hợp bản thử nội bộ”, sau yêu cầu hỏi cách dùng checklist và hỏi số tiền thuế.
- Quyết định: chuyển sang chốt QC/CI và bàn giao bản thử nội bộ. Đây chưa phải ký nghiệm thu MVP pháp lý dùng hồ sơ thật.
- E2E thủ công có bằng chứng là xác nhận của khách; E2E browser tự động, kiểm tra Chrome/điện thoại và screenshot trực quan do Codex thực hiện vẫn chưa xác minh vì host trình duyệt không khả dụng.

## Điều chỉnh đã duyệt trong chat

- Cổng 0: khách trả lời “Đúng”.
- Cổng 1: khách trả lời “Duyệt”, yêu cầu Codex tự thực hiện, chưa giao A/B khi chưa cần bàn giao.
- Khách yêu cầu tự dựng DB: đã tạo cụm riêng 127.0.0.1:5543, DB dev/test riêng; không sửa server PostgreSQL đang có tại 5432.
- Khách cho phép nâng python-jose và cài pip-audit/coverage; sau đó trả lời “+” vào đề xuất cập nhật bản vá frontend, được ghi nhận là đồng ý. Không có duyệt deploy, dịch vụ trả phí hoặc mở cổng ra mạng.
- Khách duyệt sửa CI theo docs/ci-proposal.md/.patch. Đã áp dụng pr-check.yml, parse YAML và kiểm tra cấu trúc job; chưa coi đó là run CI GitHub thành công cho code mới.
