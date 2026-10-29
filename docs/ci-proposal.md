# Sửa CI — khách đã duyệt và đã áp dụng

File: `.github/workflows/pr-check.yml`. Khách đã duyệt trong chat; đã áp dụng, parse YAML và xác nhận các job bắt buộc có mặt. Không sửa scripts package, không deploy và không push main. docs/ci-proposal.patch giữ lại đề xuất trên baseline để truy vết, không áp dụng lại khi workflow đã đổi. CI GitHub của SHA mới phải được xác minh riêng.

## Vấn đề có bằng chứng từ workflow hiện tại

- Python test dùng SQLite/aiosqlite dù app chỉ có asyncpg/PostgreSQL và JSONB; không có TEST_DATABASE_URL cho test tích hợp mới.
- Gọi pytest --cov nhưng requirements không có pytest-cov; đã có coverage được khách cho phép cài.
- Quality Gate chỉ đợi secrets-scan/SAST, không chặn khi job Python/frontend thất bại. Các job phụ thuộc vars có thể bị skip nếu repo chưa cấu hình.
- pnpm 9 trong workflow không khớp pnpm 12.16.1 đã tạo lockfile hiện tại; Node/Python CI khác môi trường local.
- API URL mặc định đang là cổng frontend 3000 thay vì backend 8000.

## Thay đổi cụ thể xin duyệt

1. Thêm trigger push trên feature/**, fix/**, chore/** để chạy CI nhánh thử mà không tạo PR hoặc chạm main.
2. Giữ actions pin SHA và secret scanning/SAST hiện có. Python/frontend của repo này luôn chạy; không phụ thuộc biến PROJECT_TYPE/BACKEND_LANG chưa biết trạng thái. Không thêm dịch vụ ngoài hoặc bật tính năng tính phí.
3. Python job dùng Python 3.14, PostgreSQL 18 ephemeral trên 127.0.0.1:5432, DB tax_clear_ai_test. Password DB sinh từ run_id/run_attempt cho môi trường runner dùng một lần, không phải credential thật; JWT secret sinh ngẫu nhiên trong job và được mask. Không dùng secret local hoặc Gemini key trên CI.
4. Chạy migration trên DB test; ruff check ., ruff format --check src/ tests/, mypy src/, coverage run -m pytest; coverage report --fail-under=80 và coverage xml. Unit chat dùng MockTransport, không gọi Gemini thật trên CI.
5. Frontend dùng Node 24/pnpm 12.16.1; frozen lockfile; lint, type-check, test:cov, build với API URL localhost:8000. Script native chỉ cho unrs-resolver đã rà trong pnpm-workspace.yaml, không bật mọi script.
6. Quality Gate cần secrets-scan, backend-python-quality, frontend-quality; thất bại hoặc skip các job bắt buộc phải chặn gate. Job SAST vẫn là báo cáo như cấu hình trước, không gọi đó là đã qua pentest.

Không sửa push-main.yml hoặc scheduled-security.yml trong bước này. CI thực sự xanh chỉ được ghi khi có run GitHub thành công. Đọc remote đã thành công; quyền push/Actions vẫn cần xác minh bằng thao tác thật. Chưa tạo PR, chưa gửi thông điệp cho người khác.
