# HANDOFF – Tax Clear AI (chuyển giao cho Codex)

> Cập nhật: 2026-10-29. Đọc `AGENTS.md` trước (quy tắc kiến trúc, bảo mật, git). File này chỉ nói **trạng thái hiện tại, việc còn lại và cách chia việc**. Khi mâu thuẫn, `AGENTS.md` thắng về quy tắc code.

## 1. Trạng thái thật

Đã làm và đã chạy kiểm tra (2026-10-29):

| Hạng mục | Kết quả |
|---|---|
| Bộ khung VibeCraft (full-stack, FastAPI + Next.js, 10 AI tool, vi) | Đã dựng, 1 commit local `87cd090` trên nhánh `main` |
| Backend: `pytest` | 3 passed |
| Backend: `ruff check`, `mypy src` | Sạch |
| Frontend: `pnpm lint` | 0 lỗi, còn 2 warning trong `Image.test.tsx` |
| Frontend: `pnpm type-check`, `pnpm test`, `pnpm build` | Pass (94/94 test, build OK) |
| Git hook | Husky (lint-staged + commitlint) đã kích hoạt qua `npm install` |

Chưa làm / chưa biết:

- **Chưa có repo GitHub, chưa push.** Máy không có `gh` và chưa đăng nhập GitHub; không có remote. Cần người dùng tự tạo repo hoặc đăng nhập (`gh auth login`) rồi `git remote add origin <url> && git push -u origin main`.
- **Chưa chạy backend với PostgreSQL thật.** `DATABASE_URL` trong `backend/.env` còn là giá trị mẫu; chưa có migration nào (`backend/alembic` trống phiên bản). Test hiện chỉ chạm module `health`.
- **Chưa kiểm tra workflow CI trên GitHub** (chưa có repo). Cần đặt biến repo: `PROJECT_TYPE=app-fullstack`, `BACKEND_LANG=python`, `FRONTEND_FRAMEWORK=nextjs`.
- **Chưa có tính năng nghiệp vụ nào.** Phạm vi sản phẩm Tax Clear AI chưa được mô tả ở bất kỳ file nào trong repo. Đừng suy ra tính năng; hỏi người dùng hoặc chờ đặc tả.

## 2. Môi trường

- Windows 11, Git Bash/PowerShell. Python 3.14 (venv ở `backend/.venv`), Node 24, pnpm.
- Backend: `cd backend && .venv\Scripts\activate && uvicorn src.main:app --reload`
- Frontend: `cd frontend && pnpm dev` (env ở `frontend/.env.local`, đã gitignore)
- Kiểm tra trước khi báo xong:
  - Backend: `python -m pytest`, `python -m ruff check .`, `python -m mypy src`
  - Frontend: `pnpm lint`, `pnpm type-check`, `pnpm test`, `pnpm build`

## 3. Các thay đổi so với mẫu VibeCraft (đừng hoàn tác)

- `backend/requirements.txt`: `asyncpg` 0.30.0 → 0.32.0 (0.30 không build được wheel trên Python 3.14/Windows).
- `frontend/vitest.config.mts`: thêm alias `@` → `src` (mẫu thiếu, 20 suite không resolve được import).
- `frontend/vitest.setup.ts`: thêm `cleanup()` sau mỗi test và polyfill jsdom (`ResizeObserver`, `scrollIntoView`, pointer capture) cho Radix UI.
- `frontend/eslint.config.mjs`: bỏ khai báo trùng plugin `@typescript-eslint` (đã có trong `eslint-config-next`).
- `Image.tsx`, `ColorPicker.tsx`: bỏ `setState` trong `useEffect`, chuyển sang đồng bộ state lúc render. `AppIcon.tsx`: tắt đúng một rule false positive kèm lý do.

## 4. Lưu ý vận hành

- `CLAUDE.md`, `GEMINI.md`, `.windsurfrules`, `.rules`, `.github/copilot-instructions.md` là **bản sao** của `AGENTS.md` (Windows không có symlink). Sửa `AGENTS.md` rồi chạy lại `symlink-setup.sh` (script nằm trong clone `D:\STARTUP\2026-vibecraft\scripts\`).
- Dùng Husky, **không** chạy `pre-commit install` (nó từ chối vì `core.hooksPath` đã được đặt). Commit phải theo Conventional Commits.
- Clone VibeCraft nằm ngoài dự án: `D:\STARTUP\2026-vibecraft`. Không đưa vào repo.
- Git identity local hiện là `Nguyen Vinh Khanh <11230549@st.neu.edu.vn>`; người dùng có thể muốn đổi trước khi push.

## 5. Chia việc cho 3 người (trưởng nhóm + 2 thành viên)

Nguyên tắc chống giẫm chân: **mỗi người sở hữu một tập thư mục, không ai sửa thư mục của người khác**; file dùng chung chỉ trưởng nhóm sửa; hợp đồng API chốt trước khi code song song. Nhánh theo `feature/<ticket>-mô-tả`, PR vào `main`, không push thẳng `main`.

Chưa biết tên thành viên và phạm vi sản phẩm, nên dùng nhãn **Trưởng nhóm / TV-A (backend) / TV-B (frontend)**. Chỉ định tên thật sau.

| Người | Sở hữu (chỉ người này sửa) | Việc ngay (không phụ thuộc nghiệp vụ) |
|---|---|---|
| **Trưởng nhóm** | `backend/src/core/`, `backend/src/models/`, `backend/alembic/`, `.github/`, `docker*`, `AGENTS.md`, `docs/`, `HANDOFF.md`, mọi file cấu hình gốc | Tạo repo GitHub + push, đặt biến CI; chốt đặc tả sản phẩm; dựng Postgres + migration đầu; auth/JWT trong `core`; viết hợp đồng API (OpenAPI) cho 2 TV |
| **TV-A (backend)** | `backend/src/modules/<feature>/` và `backend/tests/` của feature mình nhận | Mỗi feature một thư mục module (`router/service/repository/schemas`), theo đúng lớp MVC trong `AGENTS.md`; test đơn vị + tích hợp |
| **TV-B (frontend)** | `frontend/src/` (trừ `components/common/` do trưởng nhóm duyệt) | Trang và `components/features/<feature>/`; mọi gọi API qua `services/*.service.ts`; đọc hợp đồng API của trưởng nhóm, mock tới khi backend sẵn |

Điểm dễ va chạm và cách tránh:

1. `backend/src/main.py` (đăng ký router): chỉ trưởng nhóm sửa; TV-A xin thêm một dòng `include_router` qua PR nhỏ riêng.
2. Migration Alembic: một người tạo tại một thời điểm (trưởng nhóm), tránh nhiều "head".
3. `package.json`, `requirements.txt`, lockfile: thêm dependency cần trưởng nhóm duyệt (`AGENTS.md` mục 11).
4. Kiểu dữ liệu API: nguồn duy nhất là OpenAPI của backend; `frontend/src/types/api.types.ts` cập nhật theo, không đoán field.

## 6. Việc đề nghị cho Codex làm tiếp, theo thứ tự

1. Hỏi người dùng: URL repo GitHub (hoặc xin họ chạy `gh auth login`), rồi push `main` và đặt 3 biến CI. Xem CI chạy xanh; nếu đỏ, báo log thật.
2. Hỏi người dùng đặc tả sản phẩm Tax Clear AI (người dùng, luồng chính, dữ liệu). Không tự bịa.
3. Dựng Postgres local (Docker), điền `backend/.env`, chạy `alembic upgrade head`, xác nhận `/health` hoạt động với DB thật.
4. Viết `docs/api-contract.md` hoặc xuất OpenAPI để TV-A và TV-B làm song song.
5. Giữ nguyên quy trình trong `AGENTS.md` mục 17: giải thích thiết kế, chạy kiểm tra, báo đúng đầu ra, không nói "xong" khi chưa chạy.

## 7. Cập nhật phiên BA — 2026-10-30

- Đã đọc quy tắc, bàn giao, cấu trúc repo và lịch sử Git. Lần kiểm tra đầu phiên thấy nhánh `main`, commit `74afc88` thêm bàn giao sau `87cd090`; remote đã có `https://github.com/KNV-DSEB/TaxClearAI.git`. Thông tin chưa có remote ở trên là lịch sử; chưa xác minh push/CI. Git có warning quyền đọc global ignore, không có thay đổi được báo ở lần kiểm tra trước khi ghi tài liệu.
- Phạm vi mới: ưu tiên B2 (doanh nghiệp từng hoạt động muốn giải thể); chủ/người đại diện tự trả lời 8–12 câu chính, nhận tổng hợp/checklist, cập nhật trạng thái và lưu/mở lại. Không upload chứng từ, không tính thuế/phạt/báo giá. Bản ý tưởng HKD là hướng dài hạn.
- Khách bổ sung chat AI thật thành Must, chọn Google Gemini tầng miễn phí, ngân sách dịch vụ ngoài 0 đồng. Chưa có key/model/quota xác minh; không tự bật billing. Theo điều khoản Google, không đưa dữ liệu cá nhân/bí mật/nhạy cảm vào dịch vụ miễn phí; phần chat chỉ thử bằng câu hỏi tổng quát và dữ liệu giả định.
- Đã ghi dự thảo `docs/01-brief.md`, `docs/02-requirements.md`, `docs/03-assumptions-risks.md`. Chưa có xác nhận Cổng 0 “đúng, bắt đầu”; chưa lập giải pháp Pha 1, chưa code sản phẩm, chưa thay môi trường/dependency/migration.
- Chưa biết: lịch hai ngày cụ thể, địa bàn, tên/thời điểm dữ liệu cố vấn, người dùng thật chạy thử, trình duyệt điện thoại. Khách nghiệm thu local, cố vấn duyệt chuyên môn; chỉ dùng nội dung chưa duyệt với nhãn mẫu.
- Chưa chạy lại test/lint/build backend/frontend trong phiên BA; kết quả ở mục 1 là từ phiên bàn giao cũ. Kiểm tra tài liệu bằng `git diff --check` và đọc lại file; kết quả thực tế báo trong chat.
- Bước kế tiếp: khách duyệt ba tài liệu BA và xác nhận Cổng 0, sau đó tạo kế hoạch lát, giải pháp/API và task board cho Cổng 1. Giữ nguyên mục 3 và quyền sở hữu mục 5.

## 8. Cập nhật Pha 1 — sau xác nhận “Đúng”

- Khách trả lời “Đúng” vào yêu cầu duyệt Cổng 0; đã ghi nhận là chấp thuận BA, không yêu cầu lặp lại đúng cụm từ. Cổng 1 vẫn chờ duyệt.
- Đã tạo docs/04-slice-plan.md, docs/05-solution.md, docs/06-task-board.md; cập nhật trạng thái ba tài liệu BA. Chưa viết code sản phẩm hoặc chạy build/test, chưa tạo nhánh/commit/push/tag.
- Đề xuất S1 nửa ngày khảo sát–checklist–lưu/mở lại có auth; S2 nửa ngày chat Gemini thật sau phản hồi S1; ngày 2 QC/UAT/runbook/CI, đệm 3 giờ 12 phút (20%). Khả thi có điều kiện, chưa cam kết ngày cụ thể.
- Giải pháp giữ stack thật (FastAPI 0.141.1, Next.js 16.3.1/React 19.2.8); httpx có sẵn, chưa cần thêm SDK. Bốn bảng, ba module auth/assessments/chat, account thử cấp trước, JWT/refresh theo AGENTS; API/schema cụ thể ở docs/05.
- Cổng 1 cần duyệt cả phạm vi migration mới, biến Gemini/model/mật khẩu bootstrap và cấu hình JWT/cookie/CORS, thời hạn hồ sơ thử 7 ngày và quyền xóa chính hồ sơ thử. Chưa có ủy quyền cài package/đổi scripts/sửa CI/deploy/chi tiền.
- Nguồn cố vấn, key/quota, Postgres, lịch demo/người dùng thật chưa được xác minh. Không coi nội dung mẫu là hướng dẫn luật được duyệt hoặc mock là chat thật. Tài khoản demo dùng dữ liệu thử, chưa dùng chung cho nhiều khách thật.
- Bước kế tiếp: khách duyệt ba tài liệu Pha 1 tại Cổng 1, chốt điều kiện cần thiết, rồi test chấp nhận trước code S1; không bắt đầu S2 trước phản hồi S1.

## 9. Kết quả triển khai S1/S2 và QC — 2026-10-30

- Khách đã duyệt Cổng 1, yêu cầu Codex tự thực hiện toàn bộ và chưa giao A/B; đã duyệt migration/env/auth/TTL/xóa hồ sơ thử. Sau đó duyệt nâng dependency/cài công cụ audit/coverage và sửa CI theo docs/ci-proposal.md/.patch. Không có duyệt deploy, push main, dịch vụ trả phí hoặc dữ liệu thật.
- S1: 11 câu khảo sát B2 → tổng hợp/checklist 19 mục gợi ý có nhãn draft → cập nhật/lưu/mở lại PostgreSQL. Khách xác nhận “Đã thử, luồng phù hợp để làm S2”.
- S2: Gemini REST thật qua httpx, chỉ model gemini-3.5-flash-lite đã đối chiếu tầng miễn phí; key do khách thêm vào backend/.env, không in/log/commit. Có nguồn product-guide tại /huong-dan; nguồn luật chưa được cố vấn duyệt thì thiếu căn cứ, không dựng luật. Chặn dấu hiệu PII phổ biến/câu hỏi tính tiền, không gửi hồ sơ hoặc history sang AI. Khách xác nhận “Đã thử S2, phù hợp bản thử nội bộ”. Chưa coi là UAT MVP pháp lý dùng thật.
- DB native PostgreSQL 18 riêng tại 127.0.0.1:5543, backend/.local/postgres; tax_clear_ai_dev và tax_clear_ai_test; role app không superuser/createdb/createrole. Server 5432 có sẵn không bị sửa. Secret ở .env và .local/admin.env bị gitignore. Migration 20261030_01 chạy dev/test; Alembic check khớp schema. Test finally dọn đúng user/dữ liệu do test tạo, không truncate/drop DB dev.
- Backend cuối: ruff check sạch, ruff format --check 54 files, mypy 43 source files sạch, pytest 30 passed, coverage 92%, pip check sạch. Frontend cuối: lint 0 error/2 warning cũ Image.test.tsx, type-check/build xanh, 133 tests; V8 83,27% lines/82,14% statements/81,31% branches/83,09% functions theo cấu hình hiện tại.
- Đã giữ nguyên các sửa mục 3: asyncpg 0.32.0, alias/polyfill Vitest, sửa eslint/plugin và các component common; không chỉnh fan-out AGENTS. Trang mẫu thay bằng UI B2 có minh họa SVG, service health frontend mồ côi đã gỡ cùng thay đổi.
- Bản vá đã duyệt: Next/eslint-config-next 16.4.1, Zod 4.6.6, Vite 8.2.4, Vitest/coverage-v8 4.1.12; pnpm-workspace.yaml chỉ cho build unrs-resolver đã rà. Python-jose 3.5.0, Black 26.10.1, bcrypt 5.0.0 có sẵn dùng trực tiếp do Passlib không tương thích, pip-audit 2.10.1/coverage 7.17.0; pip của venv nâng 26.2. Không đổi stack hoặc scripts.
- Audit frontend sau vá/root npm: 0 advisory. Audit Python môi trường đã cài: 3 finding records ở 2 package, dedupe 2 advisory chưa có fix (python-jose PYSEC-2026-4298, ecdsa PYSEC-2026-1325). HS256 secret ngẫu nhiên riêng/không ECDSA signing giảm phạm vi ảnh hưởng hiện tại; không báo audit Python sạch. Báo cáo, residual và giới hạn tại docs/review-s1-s2.md, docs/10-defects.md, docs/12-verification.md.
- Smoke HTTP thật đã qua login/create/PATCH/reopen. Đo cuối 40 GET hồ sơ serial local p95 8,57 ms; Gemini HTTP 200 providerUsed=true, product-guide, một lượt khoảng 1498,61 ms. Không suy ra production load hoặc p95 chat.
- Computer Use dừng do URL Chrome không đủ chắc chắn; sau daemon recovery discovery vẫn báo browser host unavailable. Không dùng công cụ UI khác để vượt chặn. Khách xác nhận E2E thủ công; browser E2E tự động, QA responsive/thiết bị cụ thể chưa được Codex xác minh.
- Daemon đã restart giữa phiên, khiến server local dừng; đã kiểm tra trạng thái và khởi động lại. PowerShell Stop-Process bị lỗi nội bộ khi nạp bản cuối; đã xác minh/dừng đúng PID own bằng Python rồi start lại, không đổi cổng. Hiện chạy backend localhost:8000, frontend localhost:3000, chỉ bind loopback; dùng localhost cho Origin/CORS.
- Nhánh local feature/s1-assessment-checklist. Đã có commit backend 3a030e6 và frontend 2798625, giữ git hooks. Commit CI/docs và việc push/CI SHA mới cập nhật tiếp; chưa tag hoặc deploy. Remote đọc được; GitHub API public đọc được run cũ, không dùng chúng làm bằng chứng code mới xanh. Chưa có gh/cached GitHub write credential được xác minh.
- Có debug.log untracked ngoài phạm vi sau khi daemon phục hồi; giữ nguyên, không stage/xóa. Không đưa .env/.local, DB hoặc key vào commit. Tiếp tục từ working tree hiện có, không reset/hoàn tác công việc này.
- Việc còn lại: chốt commit CI/docs, thử push nhánh feature bằng auth hiện có và kiểm tra run đúng SHA; nếu thiếu auth, khách đăng nhập hoặc push từ máy, không tự cài gh/đoán tài khoản. Trước phát hành thật còn cần nguồn/cây quyết định/checklist cố vấn duyệt, điều kiện dữ liệu thật/purge/mã hóa/TLS, QA browser/thiết bị và Cổng 3 đúng phạm vi. Tài liệu docs/01–12 và OpenAPI đã có.

## 10. Chốt Git/CI và bàn giao cuối phiên

- Đã chốt và push nhánh `feature/s1-assessment-checklist` lên origin, không force/push/merge main. Không cần cài gh hoặc đổi tài khoản. Commit `3a030e6` backend, `2798625` frontend, `2f51577` CI, `3e0e1a5` tài liệu; giữ nguyên hook, không no-verify.
- CI đúng SHA `3e0e1a569bb67607bc12b32b11141c8bb3ce1d1f`: https://github.com/KNV-DSEB/TaxClearAI/actions/runs/40959496981 đã completed/success. Backend Python Quality, Frontend Quality, Secret Scanning, Semgrep job và Quality Gate success; TS backend skipped vì dự án Python. Đây không phải tuyên bố audit dependency Python sạch.
- Commit theo sau có thể chỉ ghi kết quả này trong tài liệu; nguồn backend/frontend và workflow không đổi. Run mới nhất của nhánh xem trên GitHub Actions; không lặp lại phát triển S1/S2 đã được khách chấp nhận.
- Kết quả cuối local: backend 30 test/92% coverage, frontend 133 test, V8 lines 83,27%/branches 81,31%; lint/type-check/build đạt, 2 warning FE cũ còn nguyên. DB/API/Gemini thật đã smoke test. Danh sách 93 file thay đổi tại docs/changed-files.txt; kiểm tra secret local và staging không thấy key/password đang dùng. debug.log vẫn ngoài phạm vi, không stage hoặc xóa.
- Chỉ bàn giao bản thử nội bộ chạy local tại http://localhost:3000. Còn cần cố vấn duyệt nội dung pháp luật và điều kiện áp dụng checklist, vận hành dữ liệu thật (purge/TLS/mã hóa/riêng tư), QA thiết bị/trình duyệt cụ thể và ký UAT dùng thật. Không tag/deploy hoặc coi đây là tư vấn thuế hoàn chỉnh.

## 11. Chốt câu chữ web và việc giao tiếp — 2026-10-30

- Theo yêu cầu khách, đã gỡ các nhãn “chờ cố vấn xác nhận/duyệt” và thông báo tương tự khỏi trang chủ, khảo sát, checklist, chat và hướng dẫn. Đã đổi câu trả lời chat thiếu nguồn sang câu trung tính; tên giấy tờ purchase_schedules cũ trong hồ sơ đã lưu cũng được hiển thị bằng nhãn mới. Metadata nội bộ `draft` vẫn giữ nguyên; không thay bằng tuyên bố nội dung pháp lý đã được duyệt. Giữ lại thông tin đồng ý gửi câu hỏi cho Google, giới hạn dữ liệu và không tính thuế.
- Backend sau chỉnh: `ruff check .` đạt; `mypy src` đạt (43 file); `pytest` 30 passed, 9 warnings từ Starlette/test cache. Frontend sau chỉnh và dọn CSS: 134 tests passed; lint 0 lỗi, còn 2 cảnh báo cũ tại `src/components/common/Image/Image.test.tsx`; type-check và Next build đạt. Lần test đầu gặp `ENOSPC` do ổ C hết dung lượng; chuyển TEMP/TMP sang ổ D thì bộ kiểm tra hoàn tất.
- Commit `c10ac3aaba4d26567628d6de727ce4d265dad857` đã push; GitHub Actions run `41007667573` hoàn tất/success: [CI](https://github.com/KNV-DSEB/TaxClearAI/actions/runs/41007667573). Backend Python Quality, Frontend Quality, Secret Scanning, Semgrep và Quality Gate đều success; Backend TS Quality skipped vì dự án Python.
- **Teammate A — backend/security:** nhận từ nhánh `feature/s1-assessment-checklist`; xử lý hai advisory Python còn mở (python-jose và ecdsa) theo báo cáo `docs/audit-python-after.json`, không bỏ qua cảnh báo; rà việc hết hạn 7 ngày chưa tự xóa dữ liệu và đề xuất purge/retention, TLS, mã hóa, log và CORS production. Không bật production/deploy.
- **Teammate B — frontend/QA:** chạy lại trình duyệt thật trên desktop và mobile, responsive/accessibility cơ bản; xác minh đăng nhập, khảo sát, checklist (kể cả hồ sơ tạo trước thay đổi nhãn), chat và các nhánh lỗi. Ghi kết quả vào `docs/07-feedback-log.md`, `docs/08-test-plan.md`, `docs/09-uat-checklist.md` và `docs/10-defects.md`; không đánh dấu UAT đạt khi khách chưa ký.
- **Trưởng nhóm + cố vấn:** cung cấp nguồn pháp luật chính thức, ngày hiệu lực và nội dung checklist/cây quyết định đã rà soát; xác nhận phạm vi xử lý dữ liệu thật, điều khoản và người ký UAT. Không có các đầu vào này thì bản hiện tại chỉ là bản thử nội bộ, không dùng làm hướng dẫn pháp lý cho hồ sơ thật.
- Việc Codex trong phiên đã chốt: commit thay đổi câu chữ `c10ac3a`, push nhánh feature và xác nhận CI đúng SHA. `debug.log` được giữ ngoài commit; thư mục tạm kiểm thử đã dọn. Bước tiếp theo là các mục giao Teammate A/B và trưởng nhóm/cố vấn ở trên. Không push `main`, tag hoặc deploy.
