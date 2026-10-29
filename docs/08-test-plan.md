# Kế hoạch kiểm thử — S1

Chưa phải báo cáo phát hành toàn MVP. S2/chat chưa bắt đầu, UAT chưa ký.

| Yêu cầu | Kiểm tra | Bằng chứng/trạng thái |
|---|---|---|
| US-01 khảo sát, chưa biết, input sai | tests/unit/test_assessment_acceptance.py; QuestionnaireForm.test.tsx | Test chấp nhận viết trước code, xem kết quả cuối phiên tại s1-verification.md |
| US-02 tổng hợp/checklist có nhãn, ngoài phạm vi | test_assessment_acceptance.py; AssessmentWorkspace.test.tsx | Không biến dữ liệu draft thành yêu cầu pháp lý bắt buộc |
| US-03 lưu/mở lại, cập nhật, xóa | tests/integration/test_assessment_flow.py | PostgreSQL thật, DB riêng tax_clear_ai_test; không rebuild DB dev |
| Quyền truy cập | test_foreign_owner_cannot_read_change_or_delete_case | Kiểm tra GET/PATCH/DELETE trả 404 khi principal khác |
| Auth/session | LoginForm.test.tsx; test_refresh_rotates_and_logout_revokes_refresh | Cookie HttpOnly, refresh rotate/logout, lỗi đăng nhập có phản hồi |
| Sai/rỗng/quá lớn | Validation Pydantic, CSRF/body-limit/rate-limit test | 422 RFC7807 không echo input, 413 cho >8 KiB; chưa load test public |
| US-04 Gemini | Chưa triển khai | Phải test mock ở unit và gọi thật riêng ở S2; không gọi Gemini từ unit test |
| US-05 responsive/a11y | Rà tĩnh nhãn/focus/keyboard CSS, component tests | Cần khách/QA thử Chrome và điện thoại thực tế; chưa khẳng định đạt WCAG toàn diện |
| Browser E2E xuyên UI–API–DB | Checklist docs/09 | Chưa chạy tự động do Computer Use dừng; kiểm thử API thật và component riêng không thay thế browser E2E |
| Dependencies/secrets | pip-audit; pnpm audit; git ignore/tracked-files check | Ghi tất cả phát hiện, không dùng audit --fix mù, không ignore advisory để báo xanh |

DB test dùng migration như dev. Mỗi test tạo tài khoản ngẫu nhiên/dữ liệu riêng và finally xóa chính tài khoản test đó, FK cascade dọn dữ liệu liên quan. Không truncate/drop DB dev, không dùng credentials thật trong fixture. Bộ pytest yêu cầu TEST_DATABASE_URL trỏ đúng tax_clear_ai_test. Workflow CI đã được khách duyệt và sửa cho PostgreSQL test riêng, SHA mới chưa được báo xanh khi chưa có run thật.

Skill testing đã được dùng để đối chiếu ma trận: còn thiếu QA browser/thiết bị cụ thể, kiểm thử tải đồng thời, rollback migration có dữ liệu và nguồn pháp lý đã duyệt. Các điểm này không được suy ra là đã đạt từ coverage hoặc unit tests. Khách đã xác nhận chạy thủ công S1 và S2 nội bộ, nguồn xác nhận lưu tại docs/07.

Backend coverage mục tiêu 80% theo AGENTS; đo bằng coverage run -m pytest và coverage report. Frontend đo riêng bằng test:cov; không suy ra từ số test pass.

Rà security-audit/code-review/database/frontend/ui-design-review là rà tĩnh cộng kết quả kiểm tra; không tuyên bố đã pentest hay có người rà độc lập. Không tag/release khi còn lỗi Major/Critical cốt lõi hoặc UAT chưa ký.
