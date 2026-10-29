# Bảng việc — Cổng 1 đã duyệt, cập nhật thực thi

Ngày: 2026-10-30. Khách đã yêu cầu Codex tự thực hiện toàn bộ, chỉ bàn giao teammate khi gần hết token. Vì vậy A/B trong bảng phân chia dự kiến bên dưới chưa được giao hoặc khởi chạy; Codex thực thi cả hai phần theo ủy quyền, giữ các ranh giới module/file dùng chung. Không giả định có agent khác đang làm việc.

| Nhóm việc | Trạng thái thực tế |
|---|---|
| P00 | Cổng 1/API đã duyệt; DB dev/test riêng hoạt động; Gemini key đã cấp và gọi thật thành công; nội dung cố vấn vẫn thiếu |
| S1-T01–S1-T07 | Đã triển khai, test API–PostgreSQL thật và component, khách xác nhận dùng thử rồi cho phép S2 |
| S2-T01–S2-T03 | Đã nối Gemini/UI, có nguồn hướng dẫn sử dụng, chặn tính tiền/thiếu nguồn/PII phổ biến; khách xác nhận phù hợp bản thử nội bộ |
| Q01 | Đã có test plan, UAT checklist và defects; kết quả tự động/giới hạn cập nhật tại docs/12-verification.md |
| Q02 | Rà tĩnh và kiểm tra tự động đã chạy; UAT nội bộ S1/S2 có xác nhận khách; responsive/QA browser đầy đủ và nghiệm thu pháp lý còn mở |
| R01 | Runbook và bản sửa CI đã có; chờ commit/push/CI của SHA mới được kiểm chứng; chưa tag hoặc deploy |
| O01 | Không làm bản in trong đợt này, ưu tiên Must/QA và nội dung cần cố vấn duyệt |

Hợp đồng API phải duyệt từ docs/05 trước A/B làm song song. Mỗi người giữ quyền sở hữu HANDOFF mục 5. `backend/src/main.py`, core/models/alembic và cấu hình chung chỉ trưởng nhóm sửa. Nhánh `feature/<ticket>-description`, Conventional Commits; không push main, không merge khi chưa rà soát.

| ID | Lát / việc | Người nhận | Thư mục/file chạm | Phụ thuộc | Tiêu chí xong |
|---|---|---|---|---|---|
| P00 | Chốt API, lịch demo, key/quota và nguồn | Trưởng nhóm | docs/04–06, dữ liệu cấu hình local không commit | Cổng 1 | API được duyệt, môi trường/nguồn có trạng thái thật, mốc khách thử đã hẹn |
| S1-T01 | Viết test chấp nhận API/DB cho US-01/02/03 trước code | A | backend/tests/ của auth/assessments | P00 | Có ca hợp lệ/chưa biết/out-of-scope/input sai/không có quyền; test đỏ vì chưa triển khai được ghi lại |
| S1-T02 | Viết test UI chấp nhận trước code | B | frontend/src/components/features/…/*.test.tsx | P00 | Kiểm tra hoàn tất khảo sát, lỗi lưu, trạng thái checklist, mở lại; mock API đúng contract |
| S1-T03 | DB, schema bốn bảng và migration; secret/cookie/CORS bootstrap | Trưởng nhóm | backend/src/core/, backend/src/models/, backend/alembic/, backend/.env.example | Duyệt cụ thể Cổng 1, P00 | Migration DB test riêng thành công, secret mẫu bị từ chối, cấu hình không chứa credential commit; rà database/security |
| S1-T04 | Auth và khảo sát end-to-end phía API | A | backend/src/modules/auth/, backend/src/modules/assessments/, backend/tests/ tương ứng | S1-T01, contract; tích hợp sau S1-T03 | Router/service/repository đúng lớp, owner filter/refresh/dữ liệu/checklist đúng; backend checks đạt |
| S1-T05 | UI khảo sát/kết quả/checklist/auth, services/types | B | frontend/src/app/, components/features/, services/, types/, hooks/ khi cần | S1-T02, contract | ui-design trước markup, không inline fetch, responsive/có lỗi rõ; frontend checks đạt; nếu cần sửa common gửi trưởng nhóm |
| S1-T06 | Đăng ký router và nối local, chạy browser E2E | Trưởng nhóm phối hợp A/B | backend/src/main.py, docs/07-feedback-log.md; mỗi người sửa phần mình | S1-T03/04/05 | Luồng UI–API–PostgreSQL chạy thật, mở lại giữ dữ liệu; ghi kiểm tra và demo giờ 4 |
| S1-T07 | Khách thử và quyết định S2 | Khách + Codex ghi nhận | docs/07-feedback-log.md, docs/04 nếu đổi phạm vi | S1-T06 | Có phản hồi thật; chưa có thì không đánh dấu S1 hoàn tất |
| S2-T01 | Test trước, nguồn hợp lệ và adapter Gemini | A | backend/src/modules/chat/, tests của chat; assessments/service.py nếu cần hàm cung cấp nguồn | S1-T07, key/quota/nguồn | Unit mock provider; thiếu nguồn/key/quota/injection/PII được kiểm chứng; không gửi hồ sơ, ít nhất một gọi thật an toàn |
| S2-T02 | Chat UI, lỗi/quota/disclosure/nguồn | B | components/features/chat/, services/chat.service.ts, types/api.types.ts, app/ho-so/ | S1-T07, contract S2 | Chat tự do không gửi assessment/history, không render HTML thô, nhãn providerUsed đúng; frontend checks đạt |
| S2-T03 | Rà bảo mật, integration và demo S2 | Trưởng nhóm phối hợp A/B | main.py nếu đăng ký router, docs/07-feedback-log.md | S2-T01/02 | Review code/security/UI; kiểm tra bắt buộc xanh; khách chạy chat thật và phản hồi |
| Q01 | Test plan và truy vết, UAT checklist, defects | Trưởng nhóm/Codex, A/B sửa theo sở hữu | docs/08-test-plan.md, 09-uat-checklist.md, 10-defects.md | S1, S2 | Có đường chính/lỗi/rỗng/sai/quá lớn/quyền; API–DB, E2E; lỗi có severity/bước tái hiện; chưa giả kết quả |
| Q02 | Full checks, kiểm tra bảo mật/thiết bị/p95 và UAT | Trưởng nhóm phối hợp A/B, khách ký | docs/08–10, code theo quyền sở hữu | Q01 | Tất cả lệnh bắt buộc có output; không Critical/Major cốt lõi; số đo có môi trường và số mẫu; UAT thật |
| R01 | Runbook, CI, release candidate/tag | Trưởng nhóm/Codex | docs/11-runbook.md, HANDOFF.md; tag Git khi đủ điều kiện | Q02 + quyền GitHub + nguồn cố vấn duyệt | Hướng dẫn env/chạy/migration/rollback/log; CI được xác minh xanh, UAT ký rồi mới tag v0.1.0; chưa có quyền thì báo chờ, không tự cài gh |
| O01 | Bản in tổng hợp (Should) | B | components/features/assessments/ | Must và QA đạt, còn thời gian | In có trạng thái/chờ duyệt; không chiếm đệm hoặc bỏ test để làm |

## Giao diện bàn giao và tránh xung đột

- Trưởng nhóm duyệt content version/câu hỏi/nguồn tại docs; A chuyển nội dung sang module theo bản duyệt, B chỉ đọc API. Không để hai người tự tạo bộ field khác nhau.
- A không sửa models/migrations/core/main; B không sửa common/cấu hình/package. Nhu cầu ở các file này thành thay đổi nhỏ do trưởng nhóm nhận.
- Không dùng chung DB test để drop/rebuild; thống nhất tên DB test và chủ chạy migration trước kiểm tra. Không đụng DB chứa dữ liệu khách trong quá trình test.
- Hết mỗi task: file đổi, lệnh chạy và output thật, lỗi còn mở, phụ thuộc. Mọi edit/test qua skill codeagent. Khi lỗi tạm thời retry đúng một lần, không force/no-verify.
- Khi thiếu người/môi trường/nguồn: cập nhật trạng thái task, không tự ghi “đã giao/đã test/đã demo”. Phần chưa có chuyên gia hoặc khách thử không được Codex tự đóng thay.
