# Runbook local — S1, chưa phát hành

## Phạm vi

Windows, FastAPI backend và Next.js frontend, PostgreSQL riêng đã dựng từ bộ cài 18 sẵn có. Chỉ dữ liệu giả định, không mở LAN/public. CI code SHA 3e0e1a5 đã xanh, xem docs/12; chưa có tag release. Không phải hướng dẫn deploy production.

## Môi trường

- backend/.env (gitignored): DATABASE_URL tới tax_clear_ai_dev tại 127.0.0.1:5543, TEST_DATABASE_URL tới tax_clear_ai_test, JWT_SECRET_KEY ngẫu nhiên tối thiểu 32 ký tự, JWT_ALGORITHM=HS256, access 15 phút, FRONTEND_ORIGIN=http://localhost:3000, BOOTSTRAP_USERNAME và BOOTSTRAP_PASSWORD. Không đưa giá trị bí mật vào tài liệu.
- GEMINI_API_KEY đã được khách thêm vào .env; không đưa key ra chat/log/commit. GEMINI_MODEL có thể đặt gemini-3.5-flash-lite, khi trống adapter dùng đúng model này đã đối chiếu tầng miễn phí. S2 đã gọi thật thành công; không bật billing/dịch vụ trả phí. Khởi động lại backend sau khi đổi env vì settings được cache.
- frontend/.env.local: NEXT_PUBLIC_API_URL=http://localhost:8000. Đây là nơi chứa giá trị; src/services/api.client.ts là nơi duy nhất đọc base URL.
- Dữ liệu cụm DB: backend/.local/postgres; credential quản trị chỉ tại backend/.local/admin.env, cả thư mục bị gitignore. Ứng dụng dùng role tax_clear_app không superuser/createdb/createrole.

## Chạy trên máy đã chuẩn bị

Backend, cwd backend:

```powershell
.venv/Scripts/python.exe -m alembic upgrade head
.venv/Scripts/python.exe -m src.modules.auth.bootstrap
.venv/Scripts/python.exe -m uvicorn src.main:app --host 127.0.0.1 --port 8000
```

Bootstrap chỉ thêm username nếu chưa có; không đổi password tài khoản hiện hữu. Thay BOOTSTRAP_PASSWORD sau bootstrap không tự đổi mật khẩu DB.

Frontend, cwd frontend:

```powershell
node C:/Users/Admin/AppData/Roaming/npm/node_modules/pnpm/bin/pnpm.mjs run build
node C:/Users/Admin/AppData/Roaming/npm/node_modules/pnpm/bin/pnpm.mjs run start -- --hostname 127.0.0.1 --port 3000
```

Đường dẫn pnpm này là công cụ thật trên máy hiện tại; máy khác dùng pnpm tương ứng đã cài. npm run cũng chạy cùng scripts nhưng phải báo rõ khi sử dụng. Không sửa scripts hoặc bỏ kiểm tra để né lỗi môi trường.

Mở http://localhost:3000. Chỉ domain localhost khớp CORS/Origin/cookie của bản thử. Mật khẩu demo xem biến BOOTSTRAP_PASSWORD ở backend/.env, không lưu trong browser/password manager tự động.

Nếu DB đang dừng:

```powershell
& 'C:/Program Files/PostgreSQL/18/bin/pg_ctl.exe' -D 'D:/STARTUP/Tax Clear AI/backend/.local/postgres' -l 'D:/STARTUP/Tax Clear AI/backend/.local/postgres.log' -o '-p 5543 -h 127.0.0.1' -w start
```

Server 5432 trên máy không thuộc cụm dự án, không stop/reset. dev_database.py chỉ dùng để khởi tạo cụm mới, không ghi đè DB đã có. Chế độ recover-initialization chỉ dành cụm mới bị gián đoạn, không dùng để đặt lại credential của cụm có dữ liệu người dùng.

## Kiểm tra và log

- Backend: python của .venv chạy pytest, ruff check ., mypy src; coverage run -m pytest và coverage report -m. Migration DB test sử dụng TEST_DATABASE_URL trong môi trường process riêng; không chuyển .env dev sang DB test lâu dài.
- Frontend: lint, type-check, test, build qua pnpm. test:cov đo coverage riêng. Hai warning Image.test.tsx đã có từ bàn giao; ghi thật kết quả.
- API GET /health chỉ chứng minh process sống, không phải DB readiness. Auth/khảo sát phải được smoke test để xác nhận DB.
- Log DB: backend/.local/postgres.log; log API ở terminal khởi chạy, request-ID ở response. Không log payload, mật khẩu, cookie, URL DB hoặc nội dung chat. Không gửi nguyên log chưa rà cho người ngoài.
- Audit Python: python -m pip_audit -r requirements.txt --cache-dir .local/audit-cache; báo cáo có thể vẫn đỏ vì advisory chưa có fix, xem docs/10. Audit frontend dùng registry npm chính thức vì mirror hiện không có endpoint audit.

## Dữ liệu, rollback, cổng phát hành

- Hồ sơ hết hạn truy cập sau 7 ngày; owner xóa hồ sơ đang hiệu lực từ UI với xác nhận. Chưa có purge định kỳ, nên hết hạn không có nghĩa dữ liệu đã bị xóa khỏi ổ đĩa; cần hoàn thiện vận hành lưu/xóa trước dữ liệu thật.
- Cookie access tồn tại tối đa 15 phút sau logout nếu ai đã sao chép token; refresh bị revoke, UI xóa cookie. Không mở production với tài khoản demo dùng chung.
- Dừng đúng process frontend/backend do phiên này khởi chạy trước rollback code; không kill tất cả node/python/PostgreSQL trên máy. Rollback ưu tiên trở về commit trước bằng nhánh/worktree và phục hồi backup, không reset/xóa dữ liệu hiện có.
- Migration downgrade `alembic downgrade base` sẽ xóa bốn bảng và dữ liệu: chỉ thực hiện trên DB test disposable hoặc sau khi khách duyệt riêng và có backup được kiểm chứng. Chưa chạy downgrade trên DB dev.
- Chưa tag/deploy. S1/S2 đã được khách chấp nhận nội bộ; Gemini thật đã xác minh. Còn cần nguồn cố vấn duyệt, QA responsive/trình duyệt cụ thể, quyết định residual bảo mật, CI SHA mới và UAT MVP dùng thật trước tag v0.1.0.
