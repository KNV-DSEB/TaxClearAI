# Phạm vi sử dụng AI

## AI làm gì và không làm gì

| AI được dùng ở đâu | AI không làm gì |
| --- | --- |
| Phân loại tình huống: đọc câu trả lời khảo sát đã che phần tự khai, đối chiếu với kết quả rules và đưa gợi ý phân khúc; đồng thời nhận diện thêm dấu hiệu rủi ro trong câu hỏi chatbot. | Không thay đổi phân khúc do rules xác định. Người dùng xác nhận khi có khác biệt hoặc thiếu thông tin. AI guardrail chatbot chỉ được nâng lên nhãn rủi ro; `khong` có nghĩa là không phát hiện thêm, không xóa cảnh báo regex. |
| Giải thích pháp luật tổng quát bằng LLM, dựa trên đoạn nguồn đủ điều kiện do retriever trả về và kèm citation. | Không quyết định thay người dùng, không tính hoặc ước lượng tiền thuế/phạt/phí, không đề xuất chiến lược xử lý rủi ro và không hướng dẫn né thuế. |

## Luồng xử lý

**Khảo sát:** rules xác định phân khúc và cờ rủi ro → AI gợi ý phân khúc/dấu hiệu bổ sung nếu được bật → hệ thống đối soát hai kết quả, giữ phân khúc của rules và yêu cầu xác nhận khi cần → người dùng xác nhận → frontend có thể lấy roadmap theo phân khúc và mục tiêu.

**Chatbot:** che định danh → guardrail regex/rủi ro → truy xuất đoạn nguyên văn từ nguồn nhà nước đã đối chiếu tự động → nếu không có nguồn dùng được, trả mẫu cố định mà không gọi LLM → LLM trả JSON có citation → validator đối chiếu citation, trích dẫn, thời hạn, số Điều/Khoản, số tiền và nội dung an toàn → trả câu trả lời kèm metadata nguồn và ngày đồng bộ, hoặc mẫu an toàn/chuyển chuyên gia. Nguồn bị loại nếu thiếu nguyên văn, ngoài allowlist, không còn hiệu lực, quá hạn hoặc sai hash. Các tình huống rủi ro nghiêm trọng do khảo sát truyền vào sẽ dừng trước retrieval và LLM. Gemini và Anthropic đều che lại system prompt và user prompt tại ranh giới provider.

## Khi nào AI dừng và chuyển chuyên gia

Phân khúc không tự quyết định mọi kết quả chatbot. `needs_expert` trong khảo sát được đặt theo logic bên dưới; các cờ rủi ro truyền sang chatbot có thể làm chatbot dừng sớm ở mọi phân khúc.

| Nhóm | Logic khảo sát thực tế | Dấu hiệu làm cần chuyên gia |
| --- | --- | --- |
| A1 | HKD chưa đăng ký, hoặc chưa rõ trạng thái đăng ký. HKD chưa đăng ký và đang hoạt động được xác định với confidence cao hơn. | A1 tự thân không bật `needs_expert`. Bật khi có nghĩa vụ tồn, chênh lệch, thông báo kiểm tra thuế, hóa đơn tồn, nợ BHXH, ngừng lâu trên 3 năm, đăng ký trước 2012, hoặc cờ liên quan khác theo service. |
| A2 | HKD đã đăng ký nhưng khai thuế `not_filed`. | A2 tự thân không bật `needs_expert`; các nghĩa vụ tồn, thông báo thuế, chênh lệch hoặc cờ rủi ro khảo sát khác sẽ bật. |
| A3 | HKD đã kê khai một phần/đầy đủ nhưng có chênh lệch được nhận diện, hoặc trường hợp HKD đăng ký mà rules xếp vào nhóm gần nhất do mô hình 5 nhóm không có nhóm chính xác hơn. | Mọi A3 đều được đánh dấu cần chuyên gia; các cờ như chênh lệch, thông báo thuế, hóa đơn/nợ tồn cũng kích hoạt. |
| B1 | DN khai chưa từng có doanh thu. | B1 cần chuyên gia nếu khai có tài sản/hàng tồn kho, có nghĩa vụ tồn, chênh lệch, thông báo thuế hoặc cờ rủi ro khác. Nếu không có các cờ đó, segment một mình không buộc `needs_expert`. |
| B2 | DN đã hoạt động rồi bỏ/ngừng, hoặc DN chưa phát sinh doanh thu nhưng không thuộc điều kiện B1 trong rules. | Mọi B2 đều được đánh dấu cần chuyên gia; nghĩa vụ chưa rõ, nợ, chênh lệch hoặc thông báo thuế càng cần rà soát. |

Ở chatbot, cờ khảo sát `co_thong_bao_thue`, `co_sai_lech_so_lieu`, `co_no`, `co_hoa_don_ton` và `co_bhxh_no` được ánh xạ thành nhãn dừng tương ứng. Ngoài ra regex/AI guardrail có thể dừng vì né thuế, yêu cầu chọn hướng thay người dùng, hỏi số tiền, tình huống phức tạp hoặc ngoài phạm vi. Câu hỏi “có bị phạt không” được trả lời nguyên tắc chung chỉ khi có nguồn đủ điều kiện, luôn yêu cầu chuyên gia xem xét hồ sơ cụ thể.

## Đoạn mô tả cho bài nộp

**Công nghệ:** AI được dùng ở hai việc. Một là phân loại tình huống: hệ thống quy tắc xác định nhóm từ câu trả lời khảo sát; khi được bật, AI đọc các lựa chọn khảo sát và phần tự khai đã che định danh để đối chiếu, đưa gợi ý và nhận diện dấu hiệu rủi ro trong câu hỏi. Kết quả rules vẫn là phân khúc chính; khi AI và rules khác nhau hoặc còn thiếu thông tin, người dùng được yêu cầu xác nhận. Ở chatbot, AI guardrail chỉ được nâng mức rủi ro, không thể xóa cảnh báo do quy tắc phát hiện. Hai là giải thích nội dung pháp luật tổng quát bằng ngôn ngữ dễ hiểu, dựa trên nguồn nhà nước công bố được đối chiếu tự động, kèm citation và metadata lấy nguồn. Hệ thống không trả lời khi thiếu căn cứ dùng được. AI không quyết định thay người dùng, không tính hoặc ước lượng thuế/phạt/phí, không đề xuất chiến lược xử lý rủi ro và không hướng dẫn né thuế. Backend hiện không có cơ sở dữ liệu, đăng nhập hoặc lưu tiến độ. Tin nhắn và prompt được che định danh trước khi gửi provider; log vẫn lưu đoạn câu hỏi đã che (tối đa 200 ký tự), bước hiện tại đã che (tối đa 120 ký tự) và bản tóm tắt yêu cầu chuyên gia đã lọc định danh (tối đa 500 ký tự). Phân quyền, mã hóa lưu trữ và giới hạn thời gian lưu dữ liệu là hạng mục giai đoạn sau.

**Ranh giới trách nhiệm:** AI chỉ đưa giải thích tổng quát dựa trên nguồn đủ điều kiện và nêu citation. Trường hợp cần áp dụng vào hồ sơ cụ thể, đặc biệt có thông báo thuế, chênh lệch số liệu hoặc nghĩa vụ còn tồn, cần chuyên gia rà soát. Nền tảng không thay thế tư vấn chuyên môn. Điều khoản sử dụng cần được luật sư rà soát để quy định rõ trách nhiệm khi thông tin pháp luật được cập nhật chậm hoặc sai.

## Vận hành provider

Khi `ENVIRONMENT=production` và `AI_PROVIDER_DATA_TERMS_ACK=false` (mặc định), backend ghi cảnh báo lúc khởi động nhưng vẫn chạy. Người vận hành chỉ bật xác nhận này sau khi đã kiểm tra gói provider và điều khoản xử lý dữ liệu phù hợp với cách triển khai; hướng dẫn và giới hạn hiện tại nằm trong [docs/chatbot.md](chatbot.md#quyền-riêng-tư). Không ghi khóa API vào log hoặc Git.
