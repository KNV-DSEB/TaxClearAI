# Khách chạy thử S1

Trạng thái: chưa ký. Chỉ dùng dữ liệu giả định, không nhập hồ sơ khách thật.

1. Mở http://localhost:3000, chọn Bắt đầu chuẩn bị hồ sơ. Dùng đúng localhost để khớp cấu hình local; 127.0.0.1 là origin khác.
2. Đăng nhập username `demo`. Mật khẩu được sinh ngẫu nhiên ở `BOOTSTRAP_PASSWORD` trong backend/.env trên máy; không gửi hoặc chụp lại vào chat/Git.
3. Chọn doanh nghiệp, chuẩn bị giải thể, đã từng phát sinh doanh thu. Các năm có thể để trống nếu chưa biết; không chọn năm doanh thu trước thành lập.
4. Đi hết 11 câu. Quay lại một câu để kiểm tra lựa chọn được giữ. Chỉ chọn Lưu và xem hồ sơ ở cuối.
5. Kiểm tra thông tin đã biết/chưa biết, danh mục giấy tờ và nhãn chờ cố vấn xác nhận. Không có số thuế/phạt/báo giá hoặc kết luận pháp lý.
6. Đổi một mục thành Đã có; đợi thông báo đã lưu; tải lại trang. Mục đó phải giữ trạng thái. Thử Còn thiếu và Cần xác minh.
7. Lưu đường dẫn trang kết quả để mở lại. Đăng xuất, mở lại đường dẫn và đăng nhập; phải về đúng hồ sơ đó.
8. Tạo khảo sát mới chọn hộ kinh doanh/nhu cầu khác; phải thông báo ngoài phạm vi, không áp dụng checklist doanh nghiệp B2.
9. Kiểm tra bàn phím Tab/Enter, nhãn input, nút lỗi/chờ; thử trên Chrome và điện thoại, ghi tên trình duyệt và kích thước thực tế. Local bind loopback nên điện thoại vật lý chưa truy cập được; chưa mở LAN nếu chưa chốt quyền/dữ liệu.
10. Chỉ nếu muốn xóa dữ liệu thử: chọn Xóa hồ sơ thử này, kiểm tra có bước xác nhận. Không thử xóa dữ liệu thật.

Phản hồi cần ghi: bước đã làm; điều khó hiểu; giấy tờ/câu hỏi cần đổi; kết quả tải lại; lỗi và cách tái hiện. Ghi tại docs/07-feedback-log.md sau khi khách thực sự trả lời.

Chấp nhận S1: khách xác nhận luồng chuẩn bị khảo sát phù hợp hoặc yêu cầu sửa cụ thể. Đây chưa phải ký UAT toàn MVP vì chat, nguồn luật duyệt, browser E2E và release vẫn còn phía sau.
