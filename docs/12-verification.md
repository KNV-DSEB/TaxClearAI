# Bằng chứng kiểm tra — bản thử nội bộ local

Ngày: 2026-10-30. Khách đã xác nhận S1 và S2 phù hợp bản thử nội bộ; chưa ký MVP pháp lý dùng hồ sơ thật. Không dùng kết quả local hoặc run CI cũ để tuyên bố SHA mới CI xanh.

## Lệnh và kết quả đã có

| Workspace | Lệnh / kiểm tra | Kết quả |
|---|---|---|
| backend | .venv/Scripts/python.exe -m ruff check . | All checks passed |
| backend | .venv/Scripts/python.exe -m ruff format --check src tests | 54 files already formatted |
| backend | .venv/Scripts/python.exe -m mypy src | Success, 43 source files |
| backend | .venv/Scripts/python.exe -m coverage run -m pytest | 30 passed; gồm PostgreSQL integration thật; unit Gemini dùng MockTransport |
| backend | .venv/Scripts/python.exe -m coverage report --skip-covered | 92%, 796 statements/60 missed; không phải coverage browser |
| backend | alembic upgrade head trên dev/test; alembic check | Revision 20261030_01 chạy được, No new upgrade operations detected |
| backend | pip check | No broken requirements found |
| frontend | pnpm lint/type-check/test/build, runner pnpm.mjs 12.16.1 | Xanh, 133 tests/26 suites; lint 0 error và 2 warning Image.test.tsx có sẵn |
| frontend | pnpm test:cov lần cuối | 82,14% statements, 83,27% lines, 83,09% functions, 81,31% branches |
| repo | node/js-yaml parse workflow + cấu trúc job; git diff --check | YAML parse được; Python/frontend nằm trong needs của Quality Gate; diff không lỗi khoảng trắng, có warning LF/CRLF |
| repo | kiểm tra 379 file ứng viên với secret đang dùng trong env | Không thấy giá trị bí mật local trong các file ứng viên; không thay full Gitleaks history scan |

pnpm command thật trên máy: `node C:/Users/Admin/AppData/Roaming/npm/node_modules/pnpm/bin/pnpm.mjs`. Ban đầu Corepack/pnpm.cjs thiếu file; đã thử lại rồi tìm pnpm.mjs có sẵn. Một số kiểm tra đầu dùng npm run cùng scripts; kết quả cuối chạy đúng pnpm. Không cài package manager mới.

## Smoke HTTP thật và performance

- Frontend GET /, /dang-nhap, /khao-sat đã trả 200 và html lang=vi.
- Login → POST assessment → PATCH checklist → GET lại giữ trạng thái trên DB tax_clear_ai_dev. Dữ liệu giả định, không có hồ sơ người thật.
- 40 GET hồ sơ nối tiếp, một client local Windows 11/PostgreSQL: p95 trước sửa transaction đọc 6,87 ms; đo lại bản cuối 8,57 ms, dưới 200 ms cho đường này. Không suy ra tải production hoặc tất cả endpoint đều đạt.
- Chat thật qua adapter: providerUsed=true, answered, citation product-guide, 468 ký tự ở một lần thử.
- Chat thật qua HTTP endpoint: status 200, providerUsed=true, source product-guide, khoảng 1498,61 ms một lần. Không gọi unit test mock là Gemini thật.

## Các lần đỏ đã xử lý hoặc còn giới hạn

- Test viết trước code đỏ do module chưa tồn tại; sau triển khai xanh. Hai test wizard đỏ do selector trùng h2/legend, sửa bằng role heading và chạy lại xanh, không bỏ test.
- Ruff/mypy ban đầu đỏ trong code mới, đã sửa; Alembic mismatch tên constraint đã sửa. Bootstrap lỗi Passlib/bcrypt 5 đã sửa adapter, thêm test byte limit.
- Update pnpm đã thay dependency nhưng báo ignored build unrs-resolver; đã đọc script, duyệt riêng package này và chạy thành công; không bật mọi build scripts.
- Audit root npm trên mirror thất bại vì endpoint không hỗ trợ; chuyển registry npm chính thức, 0 vulnerability. Frontend audit trước vá có Critical/High; đã cập nhật, audit sau vá 0 advisory.
- Audit Python -r requirements.txt trước vá báo python-jose/ecdsa chưa có fix và Black cũ. Đã cài Black 26.10.1; run audit -r sau vá chưa hoàn tất trước daemon restart. Audit installed environment trong sandbox cũng không hoàn tất, đã dừng đúng process và thử lại ngoài sandbox có timeout tổng 60 giây. Kết quả nêu thêm pip 25.2 có bản vá; đã nâng pip 26.2 và pip check sạch, rồi audit lại vì có thay đổi mới.
- Audit installed environment cuối: exit 1, 3 finding records ở 2 package; dedupe còn 2 advisory duy nhất python-jose PYSEC-2026-4298 và ecdsa PYSEC-2026-1325, chưa có fix. Báo cáo tại docs/audit-python-after.json; không dùng ignore hoặc gọi audit Python sạch.
- Audit frontend sau vá lưu tại docs/audit-frontend-after.json: info/low/moderate/high/critical đều 0; root npm audit 0 advisory. docs/audit-frontend.json là báo cáo trước vá có chủ đích giữ lại.
- Computer Use ban đầu dừng vì không xác định URL; sau recovery discovery vẫn báo browser host unavailable. Không dùng công cụ UI khác để vượt chặn. E2E thủ công theo xác nhận khách có; browser E2E tự động, responsive/thiết bị cụ thể chưa xác minh.

## Còn trước phát hành

Nguồn luật/cây quyết định/checklist do cố vấn duyệt; điều kiện dữ liệu thật (TTL/purge/TLS/mã hóa/riêng tư); QA browser/thiết bị; residual bảo mật được quyết định; CI GitHub SHA mới; ký UAT đúng phạm vi. Chưa tag v0.1.0, chưa deploy.

Coverage frontend là report V8 theo cấu hình hiện tại, không phải chứng minh mọi route/tệp chưa được import đều được kiểm thử. AssessmentLoader và QA trực quan cần kiểm tra riêng; không tắt test hoặc đổi phạm vi coverage để tăng số. Các test bổ sung là ca lỗi phiên/mạng, redirect, nguồn độc hại và sai năm từ yêu cầu thực tế.

Các commit backend/frontend đã tạo: 3a030e6, 2798625. Danh sách file cụ thể xem docs/changed-files.txt sau khi chốt. Không đưa env, dữ liệu DB hoặc debug.log ngoài phạm vi vào commit.
