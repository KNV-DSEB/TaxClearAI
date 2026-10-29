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
