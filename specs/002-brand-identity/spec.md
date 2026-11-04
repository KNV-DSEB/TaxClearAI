# Spec 002 — Logo và bộ nhận diện thương hiệu

Trạng thái: **Clarified** (2026-11-04). Chủ sở hữu: trưởng nhóm.

## Vì sao
Sản phẩm đang dùng tạm biểu tượng "Files" của thư viện icon làm logo: không riêng, không kể được câu chuyện, không dùng được cho favicon, hồ sơ dự thi hay mạng xã hội. Cần một bộ nhận diện riêng, nhất quán giữa web, tài liệu và ấn phẩm.

## Người dùng và bối cảnh
- Chủ/người đại diện doanh nghiệp từng hoạt động muốn giải thể; đang rối vì giấy tờ, kê khai, thông báo thuế.
- Họ gặp thương hiệu ở: tab trình duyệt (favicon), đầu trang web, bản in tổng hợp mang tới chuyên viên, ảnh đại diện/banner mạng xã hội, slide giới thiệu.

## Câu trả lời Clarify
| Câu hỏi | Quyết định |
|---|---|
| Tên | Giữ **Tax Clear AI**; bản rất nhỏ có thể chỉ dùng biểu tượng |
| Tính cách | **Điềm tĩnh, đáng tin**: gỡ rối, sáng tỏ, chắc chắn nhưng không khô cứng |
| Màu | **Giữ teal/mint**, tinh chỉnh và kiểm tra tương phản |
| Phạm vi | Bộ logo đầy đủ · Trang hướng dẫn thương hiệu · Áp vào web · Logo động và ấn phẩm |

## Yêu cầu
- **FR-1** Biểu tượng (mark) riêng, kể ý "gỡ rối → rõ ràng", không dùng khiên/cán cân/cột trụ mặc định của ngành.
- **FR-2** Wordmark "Tax Clear AI" bằng chữ chuyển thành đường vector (không phụ thuộc font khi dùng).
- **FR-3** Lockup ngang, lockup dọc, bản chỉ biểu tượng; mỗi bản có màu, một màu tối, một màu sáng (đảo).
- **FR-4** Favicon (SVG + 16/32/48 px), icon ứng dụng 180/192/512 px, ảnh Open Graph 1200×630.
- **FR-5** Trang hướng dẫn thương hiệu: câu chuyện logo, khoảng an toàn, kích thước tối thiểu, dùng đúng/sai, màu, chữ, giọng văn.
- **FR-6** Áp vào web: header, favicon, trang đăng nhập, bản in, metadata.
- **FR-7** Logo động (SVG/CSS, tôn trọng `prefers-reduced-motion`) và bộ ấn phẩm: ảnh đại diện, banner Facebook/LinkedIn, slide bìa 16:9.

## Tiêu chí nghiệm thu
- Biểu tượng nhận ra được ở 16 px; bản một màu không mất ý.
- Chữ đạt 4.5:1, biểu tượng 3:1 trên nền đặt cạnh nó, ở cả nền sáng và tối.
- Mọi file logo là SVG vector gốc + PNG xuất từ đó; không có font phụ thuộc trong SVG.
- Web dùng logo mới ở mọi nơi logo cũ xuất hiện; test, lint, build xanh.
- Không vi phạm Constitution mục I (không ngụ ý được nhà nước duyệt, không dùng biểu tượng nhà nước).

## Ngoài phạm vi
Đăng ký nhãn hiệu; đổi tên; tạo ảnh bằng AI trả phí; in ấn vật lý.
