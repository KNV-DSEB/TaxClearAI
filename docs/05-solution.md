# Giải pháp tối thiểu và hợp đồng API — Cổng 1 đã duyệt

Ngày: 2026-10-30. Đã triển khai S1/S2 và được khách chấp nhận bản thử nội bộ; chưa phát hành. Không thay stack. Sau cập nhật bảo mật được duyệt: FastAPI 0.141.1, SQLAlchemy 2.0.52, Next.js 16.4.1, React 19.2.8, python-jose 3.5.0; bcrypt có sẵn dùng trực tiếp do Passlib/bcrypt 5 không tương thích. httpx 0.28.1 có sẵn, không thêm SDK AI.

## Quyết định cần duyệt

| Quyết định | Phương án 1 | Phương án 2 | Khuyến nghị và lý do |
|---|---|---|---|
| DB | PostgreSQL local bằng công cụ hiện có | PostgreSQL managed | Local, đúng stack, không chi phí dịch vụ; nếu chưa có Postgres/Docker cần khách xử lý hoặc duyệt cài riêng |
| Auth | Một tài khoản thử cấp trước, đăng nhập JWT access 15 phút + refresh 7 ngày, không tự đăng ký | Nhà cung cấp danh tính ngoài | Tài khoản thử trước, không thêm tích hợp; gắn owner mỗi hồ sơ, chưa xây RBAC. Không coi tài khoản dùng chung là phân quyền nhiều khách |
| Hosting | Local frontend + backend, bind loopback | Hosting công khai có HTTPS và DB ngoài | Local đã được khách chọn; deploy thật cần duyệt riêng |
| AI | Gemini REST qua httpx có sẵn | Thêm Google SDK | REST, giảm dependency; key phía backend, model chọn theo quota tài khoản, không cố định tên model chưa xác minh |
| Nội dung | Tập JSON có phiên bản và nguồn do cố vấn duyệt | CMS/vector DB/crawler | Tập nhỏ theo module, không xây hệ cập nhật luật; chỉ dùng nguồn có sẵn đã duyệt |

## Cấu trúc và luồng dữ liệu

- Backend: `modules/auth/` (đăng nhập/refresh/logout), `modules/assessments/` (câu hỏi, tổng hợp, checklist, hồ sơ), `modules/chat/` (kiểm soát câu hỏi, gọi Gemini, kiểm tra nguồn). Mỗi module có router/service/repository/schemas/dependencies theo nhu cầu; không tạo repository rỗng chỉ để đủ file. Chat không lưu DB nên không có repository DB nếu chưa cần.
- `models/`: chỉ định nghĩa bảng. `core/`: cấu hình, DB session, JWT/cookie, logger, giới hạn lưu lượng và middleware; chỉ trưởng nhóm sửa. Service dùng domain objects từ repository, không query ORM. dependencies tạo service/repository và cấp principal; router không import DB session.
- Frontend: `/dang-nhap`, `/khao-sat`, `/ho-so/[id]`; components/features tương ứng. Chat nằm ở trang hồ sơ nhưng không nhận dữ liệu hồ sơ làm prompt. Dùng service auth/assessments/chat, tất cả qua api.client; API base URL chỉ đọc tại đây.
- Không làm trang quản trị, danh sách nhiều hồ sơ hoặc trang chuyên gia. Một màn kết quả đủ tổng hợp/checklist/chat, hiển thị rõ chờ duyệt.
- Luồng: UI → service frontend → API router → service nghiệp vụ → repository → PostgreSQL. Riêng chat: UI → chat service → kiểm tra dữ liệu/phạm vi → nguồn duyệt từ assessments service → Gemini adapter → kiểm tra đầu ra → trả UI. Chat không query hồ sơ.

## Dữ liệu tối thiểu

| Bảng | Cột chính và ràng buộc |
|---|---|
| users | id UUID, username unique, password_hash, is_active; không cần email/điện thoại |
| refresh_sessions | id UUID, user_id FK, token_hash unique, expires_at, revoked_at; token thô chỉ trong cookie |
| assessments | id UUID, owner_id FK, answers JSONB có schema cố định, content_version, summary_snapshot JSONB, created_at, expires_at, updated_at |
| checklist_items | id UUID, assessment_id FK, item_code, label_snapshot, review_status, status, updated_at; unique(assessment_id,item_code) |

Index owner_id/assessment_id/expiry theo truy vấn; không thêm bảng doanh thu, nghĩa vụ thuế, tài liệu upload hoặc chat. Tạo hồ sơ/checklist trong một transaction; rollback cả hai nếu thất bại. GET không ghi DB. Không tự sửa nội dung lịch sử khi đổi phiên bản; lưu snapshot. Trạng thái cập nhật theo lần ghi cuối cho một người dùng, trả lại bản ghi chuẩn từ server.

Nội dung phiên bản nằm trong `modules/assessments/content/`: câu hỏi, danh mục 19 loại giấy tờ và quy tắc chọn; mỗi nguồn có id, title, officialUrl, reviewedBy, reviewedAt, applicability, effectiveStatus (unknown/current/expired), contentStatus (draft/approved). Chỉ approved có căn cứ mới được chat dùng cho giải thích pháp lý. Tên cố vấn/hiệu lực không được tạo giả. Không mặc định danh mục 19 mục là bắt buộc.

## Hợp đồng API v1

Nguồn hợp đồng lúc lập kế hoạch: bảng này. Sau khi hiện thực, Pydantic sinh `/openapi.json` là nguồn chuẩn; trưởng nhóm đối chiếu bảng này và B sinh `types/api.types.ts` từ schema thật, không đoán trường.

JSON camelCase. Thành công dùng `{ "data": ... }`, lỗi RFC 7807 `{type,title,status,detail,instance}` và Content-Type application/problem+json, thông điệp tiếng Việt. Mọi endpoint nghiệp vụ yêu cầu principal; chỉ login công khai và có rate limit. Không thay contract health hiện có.

| Method/path (tiền tố /api/v1) | Request | Response và quyền |
|---|---|---|
| POST /auth/sessions | {username,password} | 201 + Location /api/v1/auth/sessions/current; data: {user:{id,username},expiresAt}; set cookie access/refresh |
| POST /auth/refreshes | cookie refresh, body rỗng | 200 data:{expiresAt}; rotate token; không tiết lộ token trong JSON |
| DELETE /auth/sessions/current | cookie | 204, revoke refresh và xóa cookie |
| GET /questionnaires/b2 | không | 200 data:Questionnaire; nội dung có phiên bản |
| POST /assessments | {questionnaireVersion,answers:Answers} | 201 + Location /api/v1/assessments/{id}; data:Assessment |
| GET /assessments/{id} | UUID | 200 data:Assessment của owner; thiếu/không sở hữu/hết hạn đều 404 |
| PATCH /assessments/{id}/checklist-items/{itemId} | {status} | 200 data:ChecklistItem; truy vấn gắn owner và item thuộc hồ sơ |
| DELETE /assessments/{id} | UUID | 204, xóa chính xác hồ sơ của owner và checklist; chức năng xóa dữ liệu này cần duyệt tại Cổng 1, không xóa dữ liệu hiện có trong bước lập kế hoạch |
| POST /chat/messages | {message,disclosureAccepted:true} | 200 data:ChatReply; không nhận assessmentId hoặc hồ sơ |

Không có endpoint list trong MVP nên không có danh sách không giới hạn. Nếu sau này thêm list phải default 20/max 100. Enum/options trong questionnaire tối đa theo bộ 11 câu, checklist snapshot tối đa 19 mục, không phải list toàn bộ khách.

### Schema chốt cho A/B

- `Questionnaire`: {id:"b2",version:string,contentStatus:"draft"|"approved",questions:Question[]}. `Question`: {id:string,label:string,kind:"year"|"choice",required:boolean,options:{value:string,label:string}[]}; chỉ choice có options, thứ tự cố định trong mảng.
- `Answers`: đúng 11 trường: `businessType` (company/household/unknown), `goal` (dissolution/other/unknown), `establishedYear` (integer 1900..năm hiện tại hoặc null), `revenueStatus` (yes/no/unknown), `revenueStartedYear` (cùng kiểu năm), `filingStatus` (complete/incomplete/never/unknown), `recordsStatus` (complete/partial/missing/unknown), `taxNoticeStatus` (yes/no/unknown), `laborInsuranceStatus` (none/obligations/unknown), `assetsInventoryStatus` (yes/no/unknown), `receivablesPayablesStatus` (yes/no/unknown). Required keys, null của năm mang nghĩa chưa biết hoặc không áp dụng theo revenueStatus. Backend cấm field lạ, kiểm tra mốc doanh thu không trước thành lập khi biết cả hai; revenueStatus=no thì revenueStartedYear phải null. Chưa phát sinh doanh thu thuộc phạm vi cần xác nhận trước khi coi là B2. Câu chữ và hệ quả nghiệp vụ chờ cố vấn duyệt; không suy từ enum sang nghĩa vụ thuế.
- `Assessment`: {id,questionnaireVersion,contentStatus,answers,summary,checklist,createdAt,updatedAt,expiresAt}. `summary`: {scope:"b2"|"out_of_scope"|"needs_confirmation",knownFacts:string[],unknownFacts:string[],reviewReasons:string[],notice:string}. UUID và thời gian RFC3339 UTC là string. Cờ chuyển chuyên gia chỉ là sàng lọc theo quy tắc đã duyệt; không phải thẩm định pháp lý.
- `ChecklistItem`: {id,code,label,status:"available"|"missing"|"needs_verification",reviewStatus:"draft"|"approved",note:string|null}. Mặc định needs_verification; không tự xác nhận giấy tờ đã có. Ngoài B2: checklist rỗng và notice giới hạn.
- `ChatReply`: {reply,disposition:"answered"|"insufficient_sources"|"expert_review"|"blocked_input",citations:Citation[],providerUsed:boolean}. `Citation`: {sourceId,title,url,reviewedAt}. providerUsed chỉ true khi Gemini thực sự được gọi; khi false không hiển thị như trả lời Gemini. Không đưa URL từ văn bản model vào UI nếu không khớp nguồn duyệt.
- `message`: 1–1500 ký tự sau trim, yêu cầu JSON tối đa 8 KiB; không nhận history, file hoặc HTML. Câu hỏi sau độc lập ở MVP; nhãn UI nói rõ chưa ghi nhớ hội thoại. `disclosureAccepted` không thay cơ sở pháp lý cho việc gửi dữ liệu riêng.
- Lỗi: 401 thiếu/hết phiên; 403 origin/CSRF không hợp lệ; 404 không có quyền/hết hạn; 409 phiên bản câu hỏi đã đổi; 422 input sai; 413 quá lớn; 429 giới hạn ứng dụng/quota Gemini, Retry-After khi biết; 503 thiếu key/model hoặc Gemini không khả dụng, 504 timeout. Chi tiết không chứa raw provider output, key hay nội dung hồ sơ.

## Auth, dữ liệu và Gemini

- Một tài khoản demo được cấp trước bằng username không định danh và mật khẩu mạnh qua env, DB chỉ lưu hash; chưa làm đăng ký/quên mật khẩu. Khi có nhiều khách thật phải cấp tài khoản riêng, không dùng chung dữ liệu demo.
- Access JWT 15 phút, refresh ngẫu nhiên 7 ngày lưu hash/rotate/revoke. Cookie HttpOnly, SameSite=Strict, giới hạn path phù hợp; Secure bắt buộc ngoài localhost. Kiểm tra Origin cho request ghi, CORS chỉ origin frontend đã cấu hình, không wildcard. Logout thu hồi refresh; access tồn tại tối đa 15 phút, thông báo giới hạn này trong runbook.
- Trước xử lý nghiệp vụ xác thực, mọi query gắn owner từ principal. Không tin ownerId từ client. Dùng ORM/parameterized query. Validation ở Pydantic/router; service xử lý nghiệp vụ. Không log body, chat, cookie hoặc raw lỗi Gemini; correlation ID xuyên request.
- Đề xuất thời hạn hồ sơ thử 7 ngày, xóa thủ công bởi owner hoặc purge theo expires_at qua lệnh vận hành có dry-run; chưa chạy purge/xóa tự động dữ liệu hiện có. Chat không lưu DB, không gửi hồ sơ/cookie/userId sang Gemini.
- PostgreSQL local bind loopback; không công bố đã mã hóa DB ở mức ứng dụng. Đối với dữ liệu thử dùng ổ đĩa đã mã hóa nếu có (chưa xác minh); chỉ nhận dữ liệu thật khi chốt và kiểm chứng bảo vệ lưu trữ/truyền. Production cần TLS, ổ/DB mã hóa và rà soát nghĩa vụ dữ liệu riêng.
- Chat free chỉ dùng thông tin công khai/câu hỏi giả định. Trước gửi: cảnh báo rõ, kiểm tra độ dài, từ chối dấu hiệu email/điện thoại/CCCD/MST/số tài khoản hoặc nội dung hồ sơ nhận diện được. Bộ lọc không bảo đảm phát hiện mọi bí mật trong ngôn ngữ tự do: chỉ thử có giám sát; không mở cho dữ liệu thật chỉ vì có checkbox/bộ lọc.
- Chặn bằng quy tắc câu yêu cầu tính tiền/chiến lược hồ sơ cụ thể; không cho model tự quyết định quyền truy cập hay thực thi công cụ. Nguồn lấy từ tập duyệt, giới hạn prompt, không tải URL tùy người dùng. Validate schema trả lời/citation IDs; nguồn không hợp lệ hoặc thiếu căn cứ thì trả insufficient_sources thay vì hiển thị kết luận. Không coi citation hợp lệ là bằng chứng mọi phát biểu đúng; cố vấn phải thử nội dung.
- REST adapter dùng httpx async có sẵn, key gửi header phía backend; timeout tổng 20 giây, giới hạn output 1024 token để trả JSON trọn vẹn; mô hình miễn phí được đối chiếu bảng giá là gemini-3.5-flash-lite. Chưa cần streaming. Retry một lần với lỗi tạm thời khi còn thời gian chờ; quota ngày không tự retry liên tục, không đổi key để né hạn mức. Không tự bật billing hoặc thay model có phí.
- Rate limit bản local đã triển khai: login 5 lần/phút/IP; trần API chung 120 lần/phút/IP; chat thêm 3 lần/phút/owner và 20 lần/ngày UTC toàn process. Khác đề xuất ban đầu 60/phút/owner cho API chung: chỉ chat cần phân biệt owner trong bản thử một tài khoản; chưa tuyên bố đã kiểm chứng chống lạm dụng production. Nếu quota Google thấp hơn, trả lỗi hạn mức, không tăng quota/billing. Đây là trần ứng dụng, không phải quota Google hay mục tiêu kinh doanh. Một process local giữ bộ đếm bộ nhớ, chưa thêm Redis.

Chat hiện chỉ có nguồn product-guide tại /huong-dan; Citation bổ sung kind=product/legal để không nhầm tài liệu sử dụng với luật. Không có nguồn pháp lý approved thì trả insufficient_sources, không tự tìm hoặc dựng luật. Xác nhận nguồn product là xác nhận luồng dùng thử, không phải cố vấn duyệt pháp luật. S2 đã được khách chấp nhận ở phạm vi nội bộ này.

## Phạm vi phê duyệt triển khai tại Cổng 1

Cần khách duyệt cụ thể cùng giải pháp: migration mới cho bốn bảng trên; biến Gemini API key/model và mật khẩu bootstrap trong backend .env.example không chứa giá trị, config kiểm tra không dùng JWT secret mẫu; sửa cookie/CORS và giá trị API base URL hiện có; chức năng xóa hồ sơ thử và thời hạn 7 ngày. Chưa đề nghị đổi scripts, thêm package, sửa CI, deploy hoặc chi tiền; những việc phát sinh đó xin duyệt riêng. Không gửi key trong chat, không ghi key vào tài liệu/commit.

## Kiểm chứng bắt buộc khi build

- Test chấp nhận viết trước, unit mock Gemini, integration PostgreSQL thật với DB test riêng (không drop DB dùng chung), ít nhất một E2E browser luồng chính. Chưa có runner browser trong package; ưu tiên công cụ trình duyệt hiện có, lưu kết quả tái lập; cần dependency tự động hóa mới thì xin duyệt trước.
- Backend: `python -m pytest`, `python -m ruff check .`, `python -m mypy src`, dùng Python của backend/.venv. Frontend: `pnpm lint`, `pnpm type-check`, `pnpm test`, `pnpm build`. Lint hiện có --fix nên chỉ chạy qua codeagent và kiểm tra diff sau chạy, không tự sửa scripts.
- Tự rà code-review mỗi lát; security-audit cho auth/dữ liệu/chat, database khi đổi schema; ui-design trước markup, frontend/ui-design-review sau UI. Release dùng các skill backend/security-audit/performance đúng phạm vi.
- Đo API nội bộ riêng với mục tiêu p95 <200 ms và ghi số mẫu/môi trường; Gemini latency/quota báo riêng. Không tối ưu không có số đo, không cache câu trả lời riêng tư.
