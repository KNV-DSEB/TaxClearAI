# Chatbot pháp lý — Tax Clear AI

## Luồng xử lý

1. Ẩn danh thông tin nhận diện và áp dụng guardrail.
2. Truy xuất nguyên văn từ kho luật chung. Chỉ dùng nguồn nhà nước công bố, nằm trong allowlist, còn hiệu lực, chưa quá hạn cập nhật và có hash hợp lệ.
3. Nếu không có nguồn dùng được, trả mẫu “Chưa có căn cứ pháp lý phù hợp” và không gọi LLM.
4. LLM trả JSON có citation. Validator đối chiếu citation, trích dẫn, thời hạn, số điều/khoản và số tiền với nội dung nguồn.
5. Nếu kiểm chứng thất bại, trả mẫu an toàn, mode 3, cần chuyên gia. Tối đa hai lần gọi LLM.
6. Phản hồi kèm metadata nguồn, ngày đồng bộ cũ nhất và cảnh báo nếu văn bản có sửa đổi hoặc tình trạng hiệu lực chưa rõ.

## Đồng bộ luật

Chạy từ thư mục `backend`:

```powershell
.\.venv\Scripts\python.exe -m src.modules.chatbot.sync_law_text
.\.venv\Scripts\python.exe -m src.modules.chatbot.validate_law_library --strict
```

Khuyến nghị chạy hằng tuần, Thứ Hai lúc 03:00 bằng cron:

```cron
0 3 * * 1 cd /path/to/TaxClearAI/backend && .venv/bin/python -m src.modules.chatbot.sync_law_text >> /var/log/taxclear-law-sync.log 2>&1
```

Kiểm tra báo cáo đồng bộ và validate sau mỗi lần chạy. `src/modules/chatbot/data/law_text.json` là kho luật chung; legal_library đọc từ kho này theo `document_number`, không sao chép metadata.

PDF quét có thể dùng OCR dự phòng. Cần cài Tesseract OCR cùng traineddata tiếng Việt; bật `LAW_OCR_ENABLED=true`. Khi chạy đồng bộ trên máy Windows, ví dụ nếu traineddata nằm ở `C:\Users\<user>\tessdata_fast`:

```powershell
$env:LAW_OCR_ENABLED='true'
$env:LAW_OCR_TESSERACT_CMD='C:\Program Files\Tesseract-OCR\tesseract.exe'
$env:LAW_OCR_TESSDATA_DIR="$env:USERPROFILE\tessdata_fast"
.\.venv\Scripts\python.exe -m src.modules.chatbot.sync_law_text
```

OCR chỉ được dùng khi điểm tin cậy trung bình đạt ngưỡng; PDF không đạt ngưỡng sẽ bị bỏ qua và nêu trong báo cáo.

## Cấu hình

| Biến | Mặc định | Ý nghĩa |
| --- | --- | --- |
| `LAW_SOURCE_ALLOWLIST` | `congbao.chinhphu.vn,g7.cdnchinhphu.vn,vanban.chinhphu.vn,datafiles.chinhphu.vn,vbpl.vn,xaydungchinhsach.chinhphu.vn,hue.gov.vn` | Domain nguồn nhà nước được phép. |
| `LAW_MAX_AGE_DAYS` | `30` | Tuổi tối đa của lần lấy nguồn gần nhất. |
| `LAW_OCR_ENABLED` | `false` | Bật OCR dự phòng cho PDF quét; yêu cầu Tesseract và traineddata. |
| `LAW_OCR_TESSERACT_CMD` | `tesseract` | Đường dẫn hoặc tên lệnh Tesseract. |
| `LAW_OCR_LANGUAGE` | `vie` | Mã ngôn ngữ OCR cần có traineddata tương ứng. |
| `LAW_OCR_TESSDATA_DIR` | để trống | Thư mục traineddata nếu không nằm ở vị trí mặc định. |
| `LAW_OCR_MIN_CONFIDENCE` | `85` | Điểm tin cậy OCR trung bình tối thiểu; thấp hơn sẽ loại PDF. |
| `CHATBOT_TOP_K` | `6` | Số nguồn tối đa được truy xuất. |
| `CHATBOT_MIN_RETRIEVAL_SCORE` | `1` | Điểm từ khóa tối thiểu. |
| `CHATBOT_LLM_PROVIDER` | `gemini` | `gemini`, `anthropic` hoặc `mock`. |
| `CHATBOT_MOCK_MODE` | `false` | Bật mock cho phát triển cục bộ. |
| `GEMINI_API_KEY`, `ANTHROPIC_API_KEY` | chưa đặt | Khóa provider tương ứng. |

## Giới hạn

Nội dung có thể chậm cập nhật so với thay đổi mới nhất. Trang nguồn đổi cấu trúc hoặc robots.txt chặn tải có thể khiến văn bản bị bỏ qua. OCR có thể nhận dạng sai; nội dung dưới ngưỡng tin cậy bị loại. Tách điều/khoản từ nguồn có thể lỗi nên mọi mục không chắc chắn bị loại khỏi tập dùng được. Dữ liệu tự động không thay thế tư vấn chuyên môn.
