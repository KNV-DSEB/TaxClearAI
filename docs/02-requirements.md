# Yêu cầu và tiêu chí nghiệm thu

Ngày: 2026-10-30. Phạm vi BA được khách xác nhận Cổng 0 bằng “Đúng”; chờ Cổng 1 trước build. Người dùng chính: chủ/người đại diện doanh nghiệp B2 muốn chuẩn bị khảo sát giải thể. Các quy tắc nghiệp vụ và nội dung pháp lý chưa được cố vấn duyệt.

## US-01 — Must — Trả lời khảo sát

Là người đại diện doanh nghiệp, tôi muốn trả lời 8–12 câu chính để ghi nhận tình trạng mà không phải tự kết luận pháp lý.

- Given bộ câu hỏi đã được duyệt hoặc được gắn nhãn mẫu, When mở khảo sát, Then thấy nhãn nội dung, câu hỏi tiếng Việt và lựa chọn chưa biết khi phù hợp.
- Given câu trả lời chưa hợp lệ/thiếu bắt buộc, When gửi, Then nhận lỗi dễ hiểu và không lưu bản hoàn tất sai hình dạng.
- Given câu trả lời chưa biết, When xem tổng hợp, Then thông tin đó vẫn là chưa biết, không bị đổi thành không có nghĩa vụ.
- Given khách thuộc nhóm ngoài B2, When khảo sát xác định ngoài phạm vi, Then thấy giới hạn hỗ trợ, không nhận một kết luận áp dụng B2.

## US-02 — Must — Tổng hợp và checklist

Là người đại diện, tôi muốn biết thông tin và giấy tờ cần chuẩn bị cho chuyên viên khảo sát.

- Given bộ câu trả lời đã lưu, When xem kết quả, Then thấy câu trả lời và checklist theo quy tắc tương ứng, không tính tiền thuế/phạt hay báo giá.
- Given danh mục hồ sơ khách cung cấp, When tạo checklist, Then chỉ mục có điều kiện áp dụng đã duyệt mới được coi là yêu cầu; nội dung chưa duyệt được gắn nhãn, không khẳng định mọi giấy tờ là bắt buộc.
- Given có bước hướng dẫn pháp lý đã duyệt, When hiển thị, Then có nguồn chính thức, phạm vi áp dụng và thông tin rà soát; thiếu các yếu tố này thì hiển thị chờ xác nhận.
- Given dấu hiệu tồn đọng cần chuyên gia theo quy tắc đã duyệt, When xem tổng hợp, Then thấy đề nghị chuyên gia xem xét; không tự đánh giá mức vi phạm hoặc cách né tránh.

## US-03 — Must — Lưu và tiếp tục

Là người đại diện, tôi muốn cập nhật checklist và mở lại để tiếp tục chuẩn bị.

- Given một mục checklist, When chọn đã có/còn thiếu/cần xác minh, Then trạng thái được lưu qua API vào DB.
- Given phiên có quyền truy cập hồ sơ, When tải lại/mở lại, Then nhận đúng câu trả lời và trạng thái đã lưu.
- Given người khác không có quyền, When truy cập hồ sơ, Then không đọc hoặc sửa được dữ liệu.
- Given DB/API lỗi, When lưu, Then thấy lưu chưa thành công và có thể thử lại; UI không báo đã lưu giả.

## US-04 — Must — Chat Gemini thật

Là người dùng, tôi muốn nhập câu hỏi tự do để được giải thích tổng quát có căn cứ.

- Given key hợp lệ, mô hình có quota miễn phí và nội dung nguồn đã duyệt, When gửi câu hỏi thử không chứa thông tin cá nhân/bí mật, Then hệ thống gọi Gemini thật và trả giải thích tiếng Việt cùng nguồn thuộc tập đã duyệt.
- Given chưa có nguồn phù hợp/nguồn chưa duyệt, When hỏi về pháp lý, Then hệ thống nêu chưa đủ căn cứ và đề nghị chuyên gia; không tự tạo luật, hiệu lực hoặc đường dẫn.
- Given hỏi số thuế/phạt hoặc chiến lược xử lý cụ thể, When gửi, Then không nhận con số hoặc kết luận thay chuyên gia.
- Given chat dùng tầng miễn phí, When mở chat, Then có thông tin rõ về giới hạn dữ liệu và cách Google xử lý nội dung; chỉ thử bằng câu hỏi tổng quát/dữ liệu giả định.
- Given hồ sơ đã lưu, When chat, Then không tự gửi nội dung hồ sơ cho Gemini. Cơ chế ngăn dữ liệu nhạy cảm trong nhập tự do phải được thiết kế và rà soát ở Pha 1; cảnh báo đơn thuần không chứng minh đã bảo vệ dữ liệu.
- Given thiếu key, timeout, hết quota hoặc nhà cung cấp lỗi, When gửi câu hỏi, Then thấy trạng thái không khả dụng phù hợp; không chuyển sang dịch vụ trả phí hoặc giả lập câu trả lời thành Gemini thật.
- Given người dùng yêu cầu bỏ quy tắc/giả nguồn, When chat, Then yêu cầu đó không được dùng để vượt phạm vi nội dung được phép.

## US-05 — Must — Sử dụng và phản hồi

- Given máy tính hoặc điện thoại đã thống nhất, When chạy luồng chính, Then câu hỏi, checklist và chat đọc và thao tác được; có nhãn, trạng thái lỗi và điều khiển bàn phím cơ bản.
- Given nội dung minh họa/dữ liệu giả định, When hiển thị, Then nhận biết được đó là minh họa, không có hồ sơ khách thật hoặc số liệu bịa được trình bày như bằng chứng.
- Given một lát chạy được, When khách chạy thử, Then ghi kết quả và phản hồi trước khi quyết định lát kế tiếp.

## US-06 — Should — Bản in tổng hợp

- Given một hồ sơ có quyền truy cập, When in tổng hợp, Then có câu trả lời, trạng thái checklist và nhãn nguồn/chờ duyệt; không làm lộ key hoặc thông tin nội bộ.

## Ràng buộc chung

- Tuân thủ AGENTS.md: Router → Service → Repository → Model; mọi gọi mạng frontend qua services.
- API nội bộ có mục tiêu p95 < 200 ms theo AGENTS.md. Độ trễ Gemini phải đo và báo riêng; chưa có cam kết chat đạt 200 ms.
- Không commit secret, không log nội dung hồ sơ/chat nhạy cảm; key chỉ phía backend, chưa thêm env/dependency/migration trước khi được duyệt theo quy tắc repo.
- Các kiểm tra backend/frontend, tích hợp API–DB, E2E luồng chính, rà soát bảo mật và UAT phải thực hiện khi build; tài liệu này chưa phải bằng chứng kiểm thử.
- Chưa chốt cơ chế truy cập, thời hạn lưu/xóa và schema/API; các lựa chọn thuộc Pha 1, không được xem là đã triển khai.
