# Hướng giao diện S1

Chủ đề: bàn chuẩn bị giấy tờ trước buổi khảo sát, dành cho người đại diện doanh nghiệp chưa rõ tình trạng. Màn hình giúp ghi nhận và sắp xếp; không tạo cảm giác đã thẩm định pháp lý.

Token: mực #183E42; hành động #18786B; nền #F4F7F7; giấy #FFFFFF; chữ phụ #647575; cảnh báo lỗi #943334. Chữ hệ thống Segoe UI hỗ trợ tiếng Việt, heading đậm vừa, không tải font ngoài; bảng số dùng tabular khi cần. Một màu nhấn xanh dùng cho hành động và đã có, trạng thái còn thiếu/cần xác minh luôn có chữ.

```
Logo             Giới thiệu | Chuẩn bị hồ sơ       Bản thử nghiệm
Lời mời chuẩn bị + CTA                  Minh họa giấy tờ
Ghi nhận                  Sắp xếp                  Tiếp tục
Nhãn nội dung chờ cố vấn duyệt

Khảo sát: lời hướng dẫn bên trái | từng câu và lựa chọn bên phải
Kết quả: checklist cập nhật      | thông tin cần làm rõ + quản lý hồ sơ
```

Điểm nhận diện là chồng giấy chuyển thành checklist; SVG minh họa tự dựng, không giả ảnh hồ sơ thật. Mobile xếp một cột, trạng thái giấy tờ thành hàng riêng dễ chạm. Không motion trang trí, không số liệu uy tín hoặc khách hàng tự tạo. ui-design-review và frontend cần rà trên bản render trước khi gọi S1 xong.
