# Kế hoạch deploy lên Vercel

Ngày lập: 2026-10-31. Trạng thái: **kế hoạch, chưa thực hiện**. Chưa tạo project Vercel, chưa có DB cloud, chưa deploy. Deploy là việc công khai ra ngoài, cần trưởng nhóm duyệt từng cổng bên dưới.

Nguồn đã đối chiếu ngày 2026-10-31 (giới hạn có thể đổi, kiểm lại trước khi làm): [FastAPI trên Vercel](https://vercel.com/docs/frameworks/backend/fastapi), [Python runtime](https://vercel.com/docs/functions/runtimes/python), [Vercel Services](https://vercel.com/kb/guide/python-backend-on-vercel), [giới hạn Functions](https://vercel.com/docs/functions/limitations), [Fair Use (Hobby)](https://vercel.com/docs/limits/fair-use-guidelines), [giá Gemini API](https://ai.google.dev/gemini-api/docs/pricing), [điều khoản Gemini API](https://ai.google.dev/gemini-api/terms).

## 1. Quyết định cần chốt trước (Cổng D0)

| # | Câu hỏi | Vì sao phải chốt | Đề xuất |
|---|---|---|---|
| D0.1 | Ai sẽ dùng bản deploy: chỉ nhóm + vài người thử nội bộ, hay mở cho khách thật? | Quyết định mức bảo mật, gói Vercel/Gemini và các cổng pháp lý ở mục 6 | Bắt đầu bằng **demo nội bộ có đăng nhập**, chưa mở khách thật |
| D0.2 | Gói Vercel | Hobby (miễn phí) chỉ cho dùng **cá nhân, phi thương mại**; Vercel định nghĩa thương mại rộng (bất kỳ ai tham gia làm dự án được lợi tài chính) và có thể tạm dừng deployment vi phạm | Hobby chỉ cho demo nội bộ/cuộc thi; chuyển Pro (trả phí) trước khi dùng cho mục đích kinh doanh hoặc thu phí |
| D0.3 | Gói Gemini | Tầng miễn phí: Google được dùng câu hỏi/câu trả lời để cải tiến sản phẩm và người duyệt có thể đọc. Tầng trả phí thì không | Giữ miễn phí cho demo với câu hỏi tổng quát; trước khi có người dùng thật phải chuyển tầng trả phí (ngân sách hiện là 0 đồng) |
| D0.4 | Tên miền | Cookie, CORS và kiểm tra Origin gắn với một origin cố định | Dùng `*.vercel.app` cho demo; tên miền riêng khi ra mắt |
| D0.5 | Vùng đặt máy chủ và DB | Người dùng ở Việt Nam; dữ liệu khảo sát nằm ở đâu là câu hỏi pháp lý | Singapore cho cả Vercel Function và Postgres; nhờ cố vấn xác nhận yêu cầu lưu trữ dữ liệu |

## 2. Kiến trúc đề xuất

```
Trình duyệt ──► Vercel project "tax-clear-web" (Next.js)
                  │  /api/v1/*  ──rewrite──►  Vercel project "tax-clear-api" (FastAPI, 1 Function, Singapore)
                  │                                   │
                  │                                   ├─► Postgres managed (Neon/Supabase, Singapore, có pooler)
                  │                                   └─► Gemini API
```

- **Cùng origin qua rewrite:** frontend gọi `/api/v1/...` trên chính tên miền của nó; Next.js chuyển tiếp sang backend. Lý do: backend đặt cookie `SameSite=Strict` và chặn request ghi có Origin khác `FRONTEND_ORIGIN`. Hai tên miền `*.vercel.app` khác nhau bị coi là khác site nên gọi thẳng sẽ mất cookie.
- **Phương án chọn:** hai project Vercel + `rewrites()` trong `next.config.ts` (tính năng ổn định, dễ debug từng phần).
- **Phương án thay thế:** một project dùng [Vercel Services](https://vercel.com/kb/guide/python-backend-on-vercel) (`vercel.json` khai báo cả hai service, backend không lộ ra ngoài). Gọn hơn nhưng đang **beta**; cân nhắc lại khi hết beta.
- **Không** dùng workflow `push-main.yml` (build/push Docker image) cho Vercel; Vercel tự build qua GitHub integration. Workflow PR Check giữ nguyên làm cổng chất lượng.

## 3. Việc code cần làm trước khi deploy (nhánh `chore/vercel-deploy`)

| ID | Việc | File chạm | Cần duyệt riêng? |
|---|---|---|---|
| C1 | Khai báo entrypoint FastAPI cho Vercel: `[tool.vercel] entrypoint = "src.main:app"` (hoặc file `index.py` mỏng import `app`), thêm `.python-version` (đang chạy local 3.14; Vercel hỗ trợ 3.12–3.14) | `backend/pyproject.toml`, `backend/.python-version` | Có (sửa pyproject) |
| C2 | Engine DB hợp với serverless: `NullPool` hoặc pool nhỏ; tắt prepared statement cache của asyncpg (`statement_cache_size=0`) khi đi qua pooler kiểu PgBouncer | `backend/src/core/database.py` | Không |
| C3 | Lấy IP thật sau proxy cho rate limit (chỉ tin header do Vercel đặt, không tin `X-Forwarded-For` tùy ý) | `backend/src/core/middleware.py` | Không |
| C4 | Rate limit và hạn mức chat ngày đang lưu **trong bộ nhớ một process**. Trên serverless mỗi instance đếm riêng nên giới hạn đăng nhập 5 lần/phút gần như vô hiệu. Chuyển bộ đếm sang Postgres (bảng nhỏ) hoặc Redis managed | `core/middleware.py`, `chat/service.py`, migration mới | **Có** (migration hoặc dependency mới) |
| C5 | `rewrites()` chuyển `/api/v1/:path*` sang `BACKEND_URL`; `NEXT_PUBLIC_API_URL` để rỗng ở production để gọi cùng origin | `frontend/next.config.ts`, `frontend/.env.example` | Không |
| C6 | Thêm `BACKEND_URL` vào `.env.example`, cập nhật runbook | `frontend/.env.example`, `docs/11-runbook.md` | Có (đổi cấu trúc env) |
| C7 | Trang chính sách dữ liệu và điều khoản dùng thử (nội dung do cố vấn duyệt) | `frontend/src/app/...` | Nội dung cần cố vấn |
| C8 | Chạy purge định kỳ: GitHub Actions theo lịch gọi `python -m src.modules.assessments.purge --apply` vào DB cloud (secret trong GitHub), hoặc Vercel Cron gọi endpoint nội bộ có secret | `.github/workflows/`, có thể thêm endpoint | **Có** (sửa CI) |

Mỗi việc theo quy trình AGENTS mục 17: test trước, chạy đủ kiểm tra backend/frontend, CI xanh rồi mới deploy preview.

## 4. Thiết lập hạ tầng (Cổng D1, sau khi C1–C6 xanh)

1. **Postgres:** tạo DB managed ở Singapore (Neon hoặc Supabase qua Vercel Marketplace; kiểm tra gói miễn phí và giới hạn kết nối lúc tạo). Tạo role ứng dụng không phải superuser như DB local. Lấy chuỗi kết nối có pooler cho app, chuỗi trực tiếp cho migration.
2. **Migration:** chạy `alembic upgrade head` từ máy trưởng nhóm hoặc job CI vào DB cloud, **không** chạy lúc Function khởi động. Sau đó `alembic check`.
3. **Tài khoản demo:** chạy `python -m src.modules.auth.bootstrap` với env trỏ DB cloud. Mật khẩu mới, mạnh, khác bản local. Nhiều người thử thì mỗi người một tài khoản (hiện chưa có đăng ký; cần script cấp tài khoản).
4. **Project `tax-clear-api`:** Root Directory `backend`, framework FastAPI, vùng Function Singapore. Biến môi trường (Production và Preview tách riêng):

   | Biến | Giá trị |
   |---|---|
   | `ENVIRONMENT` | `production` (bật cookie `Secure` và HSTS) |
   | `DATABASE_URL` | chuỗi pooler của DB cloud |
   | `JWT_SECRET_KEY` | chuỗi ngẫu nhiên ≥32 ký tự, mới |
   | `JWT_ALGORITHM`, `JWT_ACCESS_EXPIRE_MINUTES` | `HS256`, `15` |
   | `FRONTEND_ORIGIN` | `https://<tên-web>.vercel.app` (hoặc tên miền riêng) |
   | `BOOTSTRAP_USERNAME`, `BOOTSTRAP_PASSWORD` | chỉ cần khi chạy bootstrap |
   | `GEMINI_API_KEY`, `GEMINI_MODEL` | key của tầng đã chốt ở D0.3; `gemini-3.5-flash-lite` |

5. **Project `tax-clear-web`:** Root Directory `frontend`, framework Next.js, pnpm. Biến: `BACKEND_URL=https://<tên-api>.vercel.app`, `NEXT_PUBLIC_API_URL=` (rỗng).
6. **Preview:** preview của frontend mặc định trỏ backend production. Hoặc cho preview dùng DB riêng (Neon branch) và backend preview riêng, hoặc tắt preview backend. Không để preview ghi vào DB production.

## 5. Kiểm tra trước khi công bố link (Cổng D2)

- [ ] Đăng nhập → khảo sát → lưu → tải lại → đổi trạng thái → mở lại từ Hồ sơ của tôi → xóa, trên Chrome máy tính và điện thoại.
- [ ] Cookie có `Secure`, `HttpOnly`, `SameSite=Strict`; request ghi từ origin khác bị 403.
- [ ] Đăng nhập sai liên tục bị 429 **qua nhiều instance** (sau C4).
- [ ] Chat: câu hỏi hướng dẫn, câu hỏi luật (có trích dẫn "chưa rà soát"), câu chứa số định danh bị chặn, câu hỏi tiền phạt chuyển chuyên viên.
- [ ] Log Vercel không chứa body, cookie, câu hỏi chat hay key.
- [ ] Đo p95 của `GET /assessments/{id}` từ Việt Nam (cold start và warm) và ghi lại; mục tiêu 200 ms áp dụng cho request warm.
- [ ] Thử rollback: Vercel Instant Rollback về deployment trước; migration phải tương thích ngược ít nhất một phiên bản.

## 6. Cổng trước khi cho người dùng thật (Cổng D3)

Các mục này không giải quyết được bằng code và đang mở trong `docs/10-defects.md`:

- **D11/D19 – nội dung pháp lý:** checklist, quy tắc và 25 đoạn trích luật chưa được cố vấn rà soát; hiệu lực chưa xác minh. Nguồn luật tự ngừng dùng sau 30/11/2026 nếu chưa có công cụ đồng bộ.
- **D13 – dữ liệu thật:** chính sách lưu trữ/xóa, mã hóa, vùng lưu trữ, nghĩa vụ bảo vệ dữ liệu cá nhân theo pháp luật Việt Nam: cần cố vấn pháp lý xác nhận, nhóm kỹ thuật không tự kết luận.
- **Gói dịch vụ:** Vercel Hobby không dùng cho mục đích thương mại; Gemini miễn phí không phù hợp dữ liệu người dùng thật (D0.2, D0.3).
- **UAT có chữ ký** theo `docs/09-uat-checklist.md` trên bản deploy.

## 7. Thứ tự thực hiện và ước lượng

| Bước | Nội dung | Ước lượng | Ai |
|---|---|---|---|
| 1 | Chốt D0.1–D0.5 | ngoài lịch | Trưởng nhóm |
| 2 | C1–C3, C5–C6 + test | ~0,5 ngày | Agent/TV-A, TV-B |
| 3 | C4 rate limit dùng chung (sau duyệt) | ~0,5 ngày | Agent/TV-A |
| 4 | Hạ tầng D1 + migration + bootstrap | ~2 giờ | Trưởng nhóm (giữ secret) |
| 5 | Deploy preview, chạy checklist D2 | ~2 giờ | Trưởng nhóm + TV-B |
| 6 | Production cho demo nội bộ | ~0,5 giờ | Trưởng nhóm |
| 7 | C7, C8 và cổng D3 trước khi mở người dùng thật | phụ thuộc cố vấn | Trưởng nhóm + cố vấn |

Ước lượng là của nhóm kỹ thuật, chưa tính thời gian chờ tạo tài khoản dịch vụ hoặc duyệt nội dung.
