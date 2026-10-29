# Rà soát S1/S2 — tự rà, chưa phải pentest hay review độc lập

Phạm vi: diff backend/frontend/DB/CI của bản local. Áp dụng code-review, backend, database, frontend, ui-design-review, security-audit và performance. Không tuyên bố đã chứng nhận tuân thủ pháp luật hoặc WCAG toàn diện.

## Kết luận code-review

**Needs Discussion đối với phát hành dùng hồ sơ thật.** Bản thử nội bộ có thể tiếp tục theo phản hồi chấp nhận S1/S2 của khách. Không phát hiện Critical/Major chưa sửa trong luồng nội bộ đã test; các giới hạn phát hành sau đây vẫn chặn gọi MVP pháp lý hoàn chỉnh.

| Mức độ | Vị trí | Vấn đề / ảnh hưởng | Cách xử lý |
|---|---|---|---|
| Major release gate | modules/assessments/content.py:VERSION/NOTICE; service.py:get_approved_chat_sources | Nội dung hồ sơ là draft, chỉ có nguồn hướng dẫn sản phẩm; chưa đủ để hướng dẫn pháp lý thực tế | Cố vấn cung cấp/duyệt quy tắc, điều kiện áp dụng, link chính thức và thời điểm rà soát; không gắn approved trước khi có bằng chứng |
| Major trước dữ liệu thật | core/config.py:environment; assessments/service.py:create; UI hướng dẫn | Local HTTP, mã hóa ổ chưa xác minh; TTL chỉ chặn truy cập, chưa purge | Chỉ dữ liệu giả định; trước khách thật phải chốt TLS, mã hóa lưu trữ, thời hạn/purge và cơ sở xử lý dữ liệu với cố vấn |
| Chưa xác minh | Browser host; docs/09-uat-checklist.md | Không có QA trực quan/responsive tự động của Codex trên Chrome/điện thoại | Khách đã xác nhận luồng thủ công; cần ghi tên thiết bị/trình duyệt và chạy phần kiểm tra còn lại |

Đã sửa trong diff: router bộ câu hỏi gọi service; kiểm tra user active thuộc auth service; repository trả domain object; đóng transaction đọc xác thực trước khi chờ bcrypt/Gemini; source/citation không lấy URL tự do từ model; trạng thái checklist chỉ đổi sau server xác nhận; xóa có bước xác nhận; không còn service health frontend mồ côi từ trang mẫu.

Ưu tiên tiếp theo: (1) nội dung cố vấn duyệt, (2) QA browser và điều kiện dữ liệu thật, (3) CI của SHA mới và UAT đúng phạm vi. Không merge/tag như bản production-ready.

## Security audit — các phát hiện cần ghi nhận

### SEC-01 — Medium có điều kiện — CWE-347, OWASP A06/A07

- Vị trí: backend/requirements.txt (python-jose 3.5.0); core/security.py:decode_access_token; modules/auth/service.py:require_secret.
- Bằng chứng: `jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])`; service từ chối algorithm khác HS256 và secret mẫu/ngắn. DB setup sinh secret ngẫu nhiên riêng, không dùng asymmetric/public key.
- Advisory: [CVE-2026-85394 / GHSA-3qf3-8w2g-rqmx](https://github.com/advisories/GHSA-3qf3-8w2g-rqmx). Audit báo chưa có bản sửa cho 3.5.0.
- Kịch bản: nếu dùng DER public key làm HMAC secret hoặc mở thuật toán không kiểm soát, người có public key có thể giả token. Đây không phải cấu hình hiện tại được kiểm tra.
- Xử lý: giữ HS256 với secret ngẫu nhiên, không mở hỗ trợ asymmetric; theo dõi upstream hoặc xin duyệt thay thư viện nếu cần thuật toán khác. Không đánh dấu dependency audit sạch/ignore advisory.

### SEC-02 — Low trong cấu hình hiện tại — CWE-208, OWASP A06

- Vị trí: transitive ecdsa 0.19.2 của python-jose; core/security.py:create_access_token.
- Bằng chứng: app chỉ sign HMAC HS256, không gọi ECDSA SigningKey/sign_digest, keygen hoặc ECDH.
- Advisory: [CVE-2024-23342 / GHSA-wj6h-64fc-37mp](https://github.com/advisories/GHSA-wj6h-64fc-37mp), chưa có fix theo audit.
- Kịch bản: attacker đo thời gian ECDSA signing có thể thu thông tin khóa; chức năng đó không được app sử dụng.
- Xử lý: không kích hoạt ECDSA, ghi residual và rà lại nếu thay thuật toán. Không bỏ qua advisory để có exit code xanh.

### SEC-03 — High nếu dùng dữ liệu thật, không chấp nhận public — CWE-359, OWASP A04

- Vị trí: modules/chat/service.py:SENSITIVE/PRIVATE_TERMS; ChatPanel.tsx:giới hạn dữ liệu.
- Bằng chứng: regex chặn email/dãy số/từ nhận diện phổ biến, request không nhận assessmentId/history, nhưng không thể nhận diện mọi bí mật/tên riêng trong câu tự do.
- Kịch bản: người dùng bỏ qua giới hạn thử nghiệm và gõ thông tin riêng tư mà regex không nhận ra, nội dung có thể tới dịch vụ AI miễn phí.
- Xử lý hiện tại: chỉ thử có giám sát bằng dữ liệu giả định/câu tổng quát, thông báo nhà cung cấp và không tự đính kèm hồ sơ. Trước public phải thiết kế/kiểm chứng biện pháp dữ liệu hoặc phương án nhà cung cấp phù hợp; checkbox/bộ lọc không phải bằng chứng tuân thủ.

### SEC-04 — Critical/High trong baseline, đã vá — CWE-22/CWE-1395/CWE-502, OWASP A06

- Vị trí: frontend/package.json/pnpm-lock.yaml; baseline Next 16.3.1, Zod 4.4.3, Vite 8.2.1 và Vitest 4.1.10.
- Bằng chứng: docs/audit-frontend.json lưu audit trước vá; có RCE Windows/image/cache và lỗi traversal/memory. Đây là finding theo advisory, không có thử khai thác trên máy người dùng.
- Bản sửa: Next/eslint-config-next 16.4.1, Zod 4.6.6, Vite 8.2.4, Vitest/coverage-v8 4.1.12; duyệt riêng build script unrs-resolver đã đọc. Audit sau vá ghi ở docs/12-verification.md.
- Black dev 26.5.1 cũng đã nâng 26.10.1 cho [GHSA-cg8m-r9f2-5wm2](https://github.com/advisories/GHSA-cg8m-r9f2-5wm2); phạm vi advisory là GitHub Action use_pyproject, repo chưa dùng action đó.

### Tổng hợp bảo mật theo phạm vi

| Nhóm | Kết quả / mức còn lại | Số file/khu vực chính |
|---|---|---|
| A01 Access control | Owner từ token, query gắn owner, GET/PATCH/DELETE foreign trả 404 trong test | 3 module auth/assessments |
| A02 Crypto | bcrypt, secret env, cookie HttpOnly; TLS/mã hóa ổ là gate trước dữ liệu thật | core/config/security + cookie transport |
| A03 Injection | ORM/parameterized query, model output là text; không nhận URL/tool tùy người dùng | 2 repository + chat |
| A04 Design/privacy | High có điều kiện SEC-03, chặn mở public với dữ liệu thật | 2 file chat/UI |
| A05 Config | Origin/CORS cụ thể, body limit, security headers API; không production readiness | core/middleware |
| A06 Dependencies | SEC-01 Medium có điều kiện, SEC-02 Low; scan Python vẫn có advisory | manifest/lock + crypto |
| A07 Session | Access 15 phút, refresh hash/rotate/revoke; access đã sao chép còn tối đa 15 phút sau logout | auth module |
| A09 Logging | Request/user ID gắn context; không log body/key/cookie; kiểm tra secret local không thấy trong file ứng viên commit | core/logging/middleware/exceptions |

## Database

- Bốn bảng với PK UUID, FK on delete cascade, index FK/expiry, unique username/token hash/(assessment,item code), check status hữu hạn.
- Một transaction cho tạo hồ sơ/checklist. PATCH khóa row hồ sơ, xác minh item thuộc đúng hồ sơ/owner trong query. Refresh dùng row lock và rotate; không query trong vòng lặp checklist, không N+1.
- JSONB snapshot có chủ đích để giữ nội dung phiên bản, không phải thay thế bảng nghĩa vụ thuế. Danh sách tối đa 19 mục; không có endpoint list khách không giới hạn.
- Alembic upgrade chạy trên dev và test; alembic check khớp model. Downgrade có định nghĩa nhưng chưa chạy trên DB dev vì sẽ xóa dữ liệu.
- Đã sửa tên check constraints và transaction đọc giữ qua outbound HTTP. Cụm cổng 5543 riêng, không sửa server 5432; role app không superuser/createdb/createrole.

## Frontend và UI

- API chỉ qua services, base URL đọc một nơi; request có timeout và credential; refresh đồng thời chia sẻ promise và retry một lần.
- Label cho input/checkbox/radio/select, focus-visible, skip link, aria-live cho lỗi/trạng thái; không render HTML model, URL nguồn theo allowlist; SVG tự dựng có title.
- UI có nhãn draft, lỗi lưu không báo đã lưu, lỗi chat giữ câu hỏi; xóa có xác nhận, redirect returnTo chỉ chấp nhận path hồ sơ nội bộ.
- Mobile có CSS một cột/ô chọn trạng thái đủ chạm; chưa có kiểm chứng visual/contrast mọi trạng thái hoặc thiết bị cụ thể. Không gọi đó là WCAG certified.

## Performance

Số đo HTTP local: 40 GET hồ sơ nối tiếp, một client, Windows 11, PostgreSQL dev: p95 ban đầu 6,87 ms; đo bản cuối sau sửa transaction đọc 8,57 ms, dưới mục tiêu 200 ms cho đường này. Chat Gemini thật một lượt khoảng 1498,61 ms, báo riêng; không phải p95 chat hay đo tải production.

Năm ưu tiên khi có số đo mới: (1) đo tải đồng thời đúng số người dùng thật; (2) đo auth bcrypt riêng, không giảm độ mạnh chỉ để đạt latency; (3) dùng pool HTTP khi quota/lượt chat tăng; (4) chuyển rate limiter khỏi bộ nhớ nếu chạy nhiều worker; (5) bổ sung DB readiness và purge theo chính sách đã duyệt. Chưa làm tối ưu suy đoán hoặc Redis/microservice.
