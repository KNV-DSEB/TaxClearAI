# Brief MVP — Tax Clear AI

Ngày: 2026-10-30. Trạng thái: khách xác nhận Cổng 0 trong chat bằng “Đúng”. Chờ duyệt kế hoạch/giải pháp ở Cổng 1 trước khi viết code sản phẩm.

## Vấn đề và người dùng

Khách hàng mô tả doanh nghiệp và hộ kinh doanh gặp khó khăn khi xác định thứ tự thủ tục, tập hợp giấy tờ và xử lý tồn đọng. Hiện khách liên hệ qua Zalo, điện thoại hoặc gặp trực tiếp; sau đó chuyên viên phân tích hồ sơ và báo giá. Chưa có bằng chứng định lượng về nhu cầu, chi phí hoặc thời gian tiết kiệm.

Nhóm ưu tiên trong phiên này: doanh nghiệp từng hoạt động, hiện muốn giải thể (B2). Lựa chọn trực tiếp này thay ưu tiên HKD trong bản ý tưởng dài hạn. Người dùng đầu tiên: chủ/người đại diện doanh nghiệp tự điền, chuẩn bị thông tin để chuyên viên khảo sát.

## Một việc cốt lõi

Trả lời câu hỏi → xem tổng hợp tình trạng và checklist chuẩn bị khảo sát → đánh dấu đã có/còn thiếu/cần xác minh → lưu và mở lại. Chỉ đề xuất lộ trình pháp lý khi nội dung, nguồn và điều kiện áp dụng đã được cố vấn duyệt. Không gọi kết quả sàng lọc là kết luận pháp lý.

## Must

- Bộ 8–12 câu chính, có câu phụ theo tình trạng và lựa chọn chưa biết; quy tắc do cố vấn duyệt.
- Tổng hợp câu trả lời và checklist theo tình trạng; phân biệt rõ nội dung mẫu/chờ duyệt và nội dung đã duyệt.
- Cập nhật ba trạng thái hồ sơ; lưu qua API vào PostgreSQL và mở lại được bằng giao diện, có kiểm soát truy cập cần thiết.
- Chat AI thật dùng Gemini Developer API tầng miễn phí, câu hỏi tự do trong phạm vi giải thích tổng quát; dẫn nguồn đã duyệt, nêu thiếu căn cứ khi không có nguồn, không tính thuế/phạt hoặc quyết định cách xử lý hồ sơ cụ thể.
- Tiếng Việt; giao diện trên máy tính và điện thoại; thử Chrome và trình duyệt điện thoại khách dùng (tên trình duyệt chưa biết).
- Dữ liệu giả định và hình minh họa có nhãn rõ ràng; hình ảnh phải phục vụ việc hiểu luồng/hồ sơ.

## Should

- Bản in tổng hợp để trao đổi với chuyên viên.

## Won't trong hai ngày

| Ngoài phạm vi | Lý do |
|---|---|
| Tính/ước lượng thuế, phạt, giá dịch vụ; cam kết thời gian pháp lý | Chưa có căn cứ được duyệt; không thuộc vai trò AI |
| Upload CCCD, sao kê, chứng từ; OCR | Chưa cần để thử luồng chuẩn bị hồ sơ; tăng rủi ro dữ liệu |
| Thanh toán, gói thuê bao, sàn và xác thực chuyên gia | Chưa cần cho một việc cốt lõi |
| HKD, doanh nghiệp chưa hoạt động, chuyển đổi/chuyển nhượng, lập hộ mới | Ngoài B2 đã chọn |
| Thư viện luật toàn diện, tự cập nhật luật, cộng đồng | Vượt phạm vi hai ngày; chỉ dùng tập nguồn tối thiểu được duyệt |
| Deploy công khai, hosting hoặc API trả phí | Chưa được duyệt; thử local, ngân sách dịch vụ ngoài 0 đồng |

## Thành công và nghiệm thu

- Khách hàng chạy một tình huống B2 từ giao diện qua API/DB, thấy tổng hợp và checklist; thay đổi trạng thái, tải lại trang và thấy dữ liệu đã lưu.
- Ca có thông tin chưa biết được giữ nguyên, không tự suy diễn; dấu hiệu cần chuyên gia được thể hiện theo quy tắc đã duyệt.
- Chat có ít nhất một lượt gọi Gemini thật thành công với dữ liệu thử an toàn; không có key thì ghi chưa xác minh, mock không đáp ứng Must.
- Thiếu nguồn, yêu cầu tính tiền hoặc hết hạn mức AI được xử lý rõ ràng; không dựng trả lời giả thành AI thật.
- Khách hàng chạy thử cuối mỗi lát và ghi phản hồi; chỉ gọi MVP dùng được sau UAT. Chưa có người dùng thật thì ghi đúng là thử local.

## Điều kiện và cổng

Khung thời gian: hai ngày × tám giờ; ngày/giờ cụ thể và khả năng có dữ liệu cố vấn chưa biết. Tính khả thi khi thêm chat thật sẽ được đánh giá ở Pha 1, có đệm tích hợp 20%; không tự kéo dài hoặc bỏ QA.

Cổng 0 đã được khách xác nhận “Đúng” khi trả lời yêu cầu duyệt. Đã chuyển sang lập kế hoạch lát, giải pháp và bảng việc; Cổng 1 cần khách duyệt trước build.
