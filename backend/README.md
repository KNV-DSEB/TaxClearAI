# Tax Clear AI - Backend API

Tax Clear AI là nền tảng trợ lý thông minh hỗ trợ hộ kinh doanh cá thể và doanh nghiệp thực hiện các thủ tục giải thể, chấm dứt hoạt động, đóng mã số thuế hoặc chuyển đổi mô hình kinh doanh đúng quy định pháp luật Việt Nam. Hệ thống kết hợp phân loại hồ sơ, thư viện văn bản pháp lý chính thức, lộ trình thủ tục từng bước, chatbot tra cứu căn cứ luật kiểm chứng nguyên văn (fail-closed, không bịa luật, không tính tiền thuế hay tư vấn né thuế) và kết nối chuyên gia tư vấn.

---

## 1. Cấu trúc và Tính năng Backend (Các Module & Endpoints)

Kiến trúc backend tuân thủ mô hình phân tầng chuẩn FastAPI (`router` → `service` → `repository`) với các module chức năng chính:

1. **Kiểm tra trạng thái hệ thống (`health`)**
   - `GET /health`: Kiểm tra sức khỏe hệ thống và trạng thái hoạt động của API.
2. **Khảo sát & phân loại tình trạng pháp lý (`legal_survey`)**
   - `GET /survey/questions`: Lấy danh sách câu hỏi khảo sát phân loại tình huống pháp lý.
   - `POST /survey/classify`: Phân loại nhóm đối tượng, mức độ rủi ro và khuyến nghị hướng xử lý (hỗ trợ phân tích dự phòng qua AI nếu cấu hình).
   - `POST /survey/chat-context`: Tạo ngữ cảnh tóm tắt khảo sát để chuyển tiếp sang chatbot.
3. **Thư viện pháp lý tra cứu chuẩn (`legal_library`)**
   - `POST /legal-library/search`: Tra cứu văn bản quy phạm pháp luật, căn cứ điều khoản cụ thể, tình trạng hiệu lực và trạng thái đồng bộ nguyên văn.
4. **Danh mục giấy tờ hồ sơ (`document_checklist`)**
   - `POST /documents/checklist`: Rà soát và tạo danh mục tài liệu, biểu mẫu tương ứng với thủ tục và tình trạng của đối tượng.
5. **Lộ trình thủ tục từng bước (`procedure_roadmap`)**
   - `POST /procedures/roadmap`: Sinh lộ trình thực hiện thủ tục chi tiết theo từng bước, thẩm quyền xử lý và căn cứ pháp lý.
   - `POST /procedures/compare`: So sánh các phương án thủ tục (ví dụ: tạm ngừng kinh doanh vs. giải thể chấm dứt hoạt động).
6. **Theo dõi tiến độ (`process_tracker`)**
   - `POST /process-tracker/track`: Đánh giá trạng thái hoàn thành của từng bước và xác định hành động cần thực hiện tiếp theo.
7. **Hồ sơ vụ việc & Kế hoạch chuyển đổi (`case_brief` & `conversion_planner`)**
   - `POST /case-brief/generate`: Tổng hợp hồ sơ tình huống chi tiết của vụ việc từ dữ liệu khảo sát và các bước đã qua.
   - `POST /conversion-plans/parallel`: Lập kế hoạch hành động song song cho các trường hợp chuyển đổi phức tạp (ví dụ: chuyển từ HKD lên doanh nghiệp đồng thời đóng MST cũ).
8. **Chatbot hỗ trợ pháp lý an toàn (`chatbot`)**
   - `POST /chatbot/ask`: Trả lời câu hỏi pháp lý dựa trên kho luật đã kiểm chứng (fail-closed guardrails, kiểm soát trích dẫn nguyên văn, tự động ẩn danh thông tin cá nhân PII, từ chối tính thuế/phạt hoặc né thuế).
9. **Danh bạ chuyên gia (`expert_directory`)**
   - `GET /experts`: Liệt kê danh sách chuyên gia tư vấn thuế và luật doanh nghiệp.
   - `GET /experts/{expert_id}`: Xem thông tin chi tiết của một chuyên gia cụ thể.
   - `POST /experts/{expert_id}/requests`: Chuẩn bị phiếu yêu cầu kết nối chuyên gia từ hồ sơ vụ việc.

---

## 2. Cài đặt môi trường

Yêu cầu môi trường: **Python >= 3.12**

```bash
# Di chuyển vào thư mục backend
cd backend

# Khởi tạo môi trường ảo Python
python -m venv .venv

# Kích hoạt môi trường ảo
# Trên Windows PowerShell:
.venv\Scripts\Activate.ps1
# Trên Linux/macOS:
source .venv/bin/activate

# Cài đặt các gói phụ thuộc
pip install -r requirements.txt

# Tạo file cấu hình môi trường từ mẫu
cp .env.example .env
```

---

## 3. Khởi chạy ứng dụng

Khởi chạy server phát triển với Uvicorn:

```bash
uvicorn src.main:app --reload --port 8000
```

- API Docs (Swagger UI): `http://127.0.0.1:8000/docs`
- OpenAPI Specification JSON: `http://127.0.0.1:8000/openapi.json`
- Health check: `http://127.0.0.1:8000/health`

---

## 4. Đồng bộ kho luật nhà nước (`sync_law_text`)

Tax Clear AI sử dụng cơ chế đồng bộ tự động trích xuất các điều khoản quy phạm pháp luật trực tiếp từ các cổng thông tin chính thức của Nhà nước (`congbao.chinhphu.vn`, `vbpl.vn`, ...).

Chạy lệnh đồng bộ:
```bash
python -m src.modules.chatbot.sync_law_text
```

### Vì sao phải chạy đồng bộ định kỳ?
Chính sách an toàn nguồn luật (`source_policy.py`) quy định: các căn cứ pháp lý đã đồng bộ vượt quá thời hạn **`LAW_MAX_AGE_DAYS`** (mặc định 30 ngày) sẽ bị coi là quá hạn và tự động bị loại khỏi danh sách nguồn được dùng (`is_usable_source() == False`). Khi đó, chatbot sẽ kích hoạt chế độ an toàn *fail-closed* và từ chối sinh trả lời nếu không còn nguồn hợp lệ. Do đó, người vận hành cần thiết lập cron job / scheduled task chạy lệnh đồng bộ định kỳ (ví dụ: hàng tuần).

---

## 5. Kiểm thử & Kiểm tra chất lượng mã nguồn

Chạy toàn bộ bộ kiểm tra tự động và bộ linter/type-checker:

```bash
# Chạy kiểm thử tự động (pytest)
pytest -q -p no:cacheprovider

# Kiểm tra quy chuẩn mã nguồn (Ruff linter)
ruff check .

# Kiểm tra định dạng mã nguồn (Black code formatter)
black --check .

# Kiểm tra kiểu dữ liệu tĩnh (Mypy type checker)
mypy src
```

---

## 6. Biến môi trường (`.env`)

| Tên biến | Kiểu dữ liệu | Mặc định | Mô tả |
| :--- | :--- | :--- | :--- |
| `APP_TITLE` | `str` | `Tax Clear AI` | Tên chính thức hiển thị của ứng dụng và tiêu đề Swagger/OpenAPI |
| `ENVIRONMENT` | `str` | `development` | Môi trường triển khai (`development`, `staging`, `production`) |
| `PORT` | `int` | `8000` | Cổng HTTP lắng nghe của dịch vụ |
| `DATABASE_URL` | `str \| None` | `None` | URL kết nối cơ sở dữ liệu (PostgreSQL/asyncpg nếu kích hoạt persistence) |
| `JWT_SECRET_KEY` | `str` | `change-me` | Khóa bí mật ký JWT (ngoài `development` bắt buộc phải đổi) |
| `JWT_ALGORITHM` | `str` | `HS256` | Thuật toán mã hóa JWT |
| `JWT_ACCESS_EXPIRE_MINUTES` | `int` | `15` | Thời gian hết hạn của token truy cập (phút) |
| `API_RATE_LIMIT_PER_MINUTE` | `int` | `60` | Giới hạn số lượng request API thông thường mỗi phút trên mỗi IP |
| `CHATBOT_RATE_LIMIT_PER_MINUTE`| `int` | `20` | Giới hạn số lượng yêu cầu chatbot mỗi phút trên mỗi IP |
| `CHATBOT_LLM_PROVIDER` | `str` | `gemini` | Nhà cung cấp mô hình LLM (`gemini`, `anthropic`, `mock`) |
| `GEMINI_API_KEY` | `str \| None` | `None` | API Key truy cập Google Gemini API |
| `ANTHROPIC_API_KEY` | `str \| None` | `None` | API Key truy cập Anthropic Claude API |
| `MODEL_GUARDRAIL` | `str` | `gemini-2.5-flash-lite`| Tên mô hình đảm bảo kiểm duyệt an toàn và phân loại |
| `MODEL_ANSWER` | `str` | `gemini-2.5-flash` | Tên mô hình tổng hợp câu trả lời theo ngữ cảnh luật |
| `MODEL_CLASSIFIER` | `str \| None` | `None` | Tên mô hình phân loại rủi ro (nếu để trống dùng MODEL_GUARDRAIL) |
| `SURVEY_AI_ENABLED` | `bool` | `true` | Bật/tắt hỗ trợ phân loại tình huống khảo sát bằng AI |
| `CHATBOT_TOP_K` | `int` | `6` | Số lượng đoạn trích văn bản luật tối đa thu thập |
| `CHATBOT_MIN_RETRIEVAL_SCORE` | `int` | `1` | Điểm khớp từ khóa tối thiểu để trích xuất căn cứ |
| `CHATBOT_MOCK_MODE` | `bool` | `false` | Bật chế độ giả lập phản hồi chatbot khi kiểm thử |
| `CHATBOT_FAILSAFE` | `str` | `khong_chac_chan` | Hành vi mặc định khi bộ phân loại không đưa ra kết luận |
| `CHATBOT_GUARDRAIL_CACHE_SIZE` | `int` | `512` | Kích thước bộ nhớ đệm cache kết quả guardrail |
| `LAW_SOURCE_ALLOWLIST` | `str` | (danh sách domain nhà nước) | Danh sách tên miền nguồn luật chính thức được phép tải về |
| `LAW_MAX_AGE_DAYS` | `int` | `30` | Thời hạn tối đa chấp nhận nguồn luật đã đồng bộ (ngày) |
| `LAW_OCR_ENABLED` | `bool` | `false` | Cho phép sử dụng OCR để đọc tệp scan văn bản pháp lý |
| `LAW_OCR_TESSERACT_CMD` | `str` | `tesseract` | Lệnh hoặc đường dẫn thực thi Tesseract OCR |
| `LAW_OCR_LANGUAGE` | `str` | `vie` | Ngôn ngữ nhận diện OCR (tiếng Việt) |
| `LAW_OCR_MIN_CONFIDENCE` | `float` | `85.0` | Ngưỡng tin cậy tối thiểu của kết quả OCR (%) |
| `AI_PROVIDER_DATA_TERMS_ACK` | `bool` | `false` | Xác nhận điều khoản bảo vệ dữ liệu với bên cung cấp AI trên production |

---

## 7. Giới hạn phiên bản MVP (Thực tế triển khai)

- **Lưu trữ dữ liệu (Persistence):** Hệ thống ở giai đoạn MVP hoạt động theo kiến trúc in-memory / stateless cho phần lớn các tác vụ khảo sát và lộ trình; chưa kích hoạt cơ sở dữ liệu quan hệ lưu vết người dùng hoặc lưu tiến trình lâu dài giữa các phiên làm việc.
- **Danh bạ chuyên gia:** Hồ sơ chuyên gia trong `expert_directory` là dữ liệu mẫu minh họa cấu trúc; cần quy trình xác thực chứng chỉ hành nghề và ký thỏa thuận hợp tác thực tế trước khi áp dụng thương mại.
- **Tự động đồng bộ văn bản luật:** Quá trình trích xuất tự động từ PDF/HTML công báo Nhà nước có thể gặp độ trễ hoặc bỏ qua một số điều khoản nếu văn bản nguồn có định dạng bảng biểu phức tạp hoặc chất lượng scan OCR chưa đạt ngưỡng tin cậy.
- **Tình trạng hiệu lực văn bản:** Do cổng công báo không công bố API truy vấn tình trạng văn bản máy đọc được, hiệu lực của nhiều văn bản tự đồng bộ tạm thời được ghi nhận là `"khong_ro"`. Với các trường hợp này, chatbot vẫn cung cấp trích dẫn nội dung nhưng **bắt buộc kèm cảnh báo** và yêu cầu người dùng xác nhận lại với chuyên gia (`needs_expert = true`).
