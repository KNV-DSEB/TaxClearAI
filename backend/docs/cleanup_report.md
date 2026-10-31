# Báo cáo kiểm tra dọn code backend

Ngày kiểm tra: 2026-10-31
Nhánh: `chore/dead-code-cleanup`
Công tắc: `DELETE_SCAFFOLDING = no`

## Đã xóa

| File/hàm/dependency | Lý do | Cách kiểm chứng | Commit |
| --- | --- | --- | --- |
| Không có | Không có ứng viên nào đủ tiêu chí an toàn để xóa trong lượt này. | Baseline xanh; `ruff` sạch; đối chiếu tham chiếu toàn source/test/docs/config; giữ các mục public hoặc thuộc nhóm bị loại trừ. | Không có |

## Giữ lại dù có vẻ chưa dùng

| Mục | Lý do giữ |
| --- | --- |
| `src/core/security.py`, `src/core/database.py`, `src/models/base.py`, `alembic/`, `alembic.ini` | Thuộc nhóm khung DB/ORM/đăng nhập/migration. `DELETE_SCAFFOLDING=no`; không xóa. `database.py` được `models/base.py` nối tới. |
| Các dependency `sqlalchemy`, `asyncpg`, `alembic`, `python-jose`, `passlib`, `python-multipart`, `types-python-jose`, `types-passlib` | Thuộc nhóm khung chưa dùng được yêu cầu giữ nguyên. Việc gỡ dependency còn cần môi trường sạch để cài lại và chạy test. |
| `src/modules/conversion_planner/repository.py::get_model_label` | Chỉ thấy định nghĩa khi grep chéo, nhưng là phương thức public của repository; quy trình yêu cầu chỉ đề xuất, không tự xóa public service/repository API. |
| Cache `.pytest-tmp/` có sẵn trong workspace | Không được Git track và không xác định được toàn bộ nội dung có phải do lượt này tạo; không xóa file có sẵn của người dùng. |

## Đề xuất, chưa làm

| Mục | Đề xuất / rủi ro |
| --- | --- |
| `get_model_label` | Có thể cân nhắc xóa sau khi chủ dự án xác nhận đây không phải interface dùng bởi caller bên ngoài hoặc tích hợp tương lai. |
| DB/ORM/đăng nhập/migration và dependencies liên quan | Chỉ dọn khi đổi `DELETE_SCAFFOLDING=yes`; trước đó cần grep lại, xóa code rồi cấu hình/dependency, cài `requirements.txt` trong venv sạch và chạy đủ kiểm tra. Rủi ro nếu gỡ nhầm là làm hỏng giai đoạn tiếp theo có DB/tài khoản. |
| `vulture` | Không có executable/module trong môi trường `.venv`, nên chưa có kết quả từ scanner này. Cài công cụ trong môi trường dev/CI rồi chạy `vulture src --min-confidence 60` để bổ sung lượt quét. |
| Thay đổi ở các file đang dirty trước lượt dọn | Worktree có nhiều file modified/untracked từ công việc trước. Không tạo commit dọn dẹp nào vì không có mục code đủ điều kiện để xóa; giữ nguyên các thay đổi đó. |

## Kết quả trước và sau

| Chỉ số | Trước dọn (baseline) | Sau dọn |
| --- | ---: | ---: |
| Test | 492 pass | 492 pass |
| `ruff check .` | Pass | Pass |
| `ruff check . --select F401,F841,F811,ERA001` | Pass | Pass |
| `black --check .` | Pass, 125 file không cần format | Pass, 125 file không cần format |
| `mypy src` | Pass, 78 source files | Pass, 78 source files |
| Số dòng `src/**/*.py` | 6,809 | 6,809 |
| Kích thước backend, bỏ `.venv`, cache và `.pytest-tmp` | 529,909 bytes | 534,218 bytes |

Không có code/file bị xóa nên số dòng code giữ nguyên. Báo cáo này là file duy nhất được thêm bởi lượt dọn; kích thước tăng 4,309 bytes do báo cáo.

## Những điểm chưa xác minh / giới hạn

- Không chạy được `vulture` vì công cụ chưa có trong môi trường; các kết luận dead-code dựa trên ruff và grep thủ công.
- `git ls-files` không tìm thấy `.pyc`, cache Python hoặc `.venv` bị track. Có `alembic/versions/.gitkeep`, đây là khung migration được giữ nguyên.
- `get_model_label` không có tham chiếu trong `src/`, `tests/`, `docs/`, cấu hình hoặc manifest đã quét; khả năng caller ngoài repo sử dụng chưa thể xác định.
- Baseline được chạy trên worktree hiện tại, vốn đã có nhiều thay đổi chưa commit từ trước lượt này. Vì vậy kết quả không đại diện riêng cho HEAD sạch `main`.
- Không xóa file nào; không phát sinh thay đổi hành vi hay endpoint.
