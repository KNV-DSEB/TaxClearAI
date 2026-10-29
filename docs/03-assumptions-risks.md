# Giả định, rủi ro và câu hỏi mở

Ngày: 2026-10-30. Cổng 0 đã được khách xác nhận “Đúng”; Cổng 1 chưa được duyệt.

## Quyết định khách đã xác nhận trong chat

- Ưu tiên doanh nghiệp từng hoạt động muốn giải thể (B2), dù ý tưởng dài hạn ưu tiên HKD.
- Đồng ý mặc định Vòng 2: chủ doanh nghiệp tự điền; 8–12 câu chính; chỉ câu trả lời/trạng thái hồ sơ; quy tắc cố vấn; tiếng Việt, máy tính/điện thoại; nghiệm thu local.
- Vòng 3: Must luồng khảo sát–tổng hợp–checklist–lưu/mở lại; bổ sung chat AI thật. Bản in là Should; chưa làm thanh toán, upload, sàn chuyên gia hoặc nhóm khác.
- Chấp nhận dữ liệu thử có nhãn trong lúc chờ cố vấn; khách nghiệm thu chức năng, cố vấn duyệt chuyên môn; thử local PostgreSQL; ngân sách dịch vụ ngoài 0 đồng.
- Nhà cung cấp AI: Google Gemini, tầng miễn phí. Chưa xác minh tài khoản, key, mô hình hoặc quota thực tế.

## Rủi ro và người phụ trách

| ID | Điều chưa biết/rủi ro | Xử lý hoặc điều kiện | Phụ trách |
|---|---|---|---|
| R01 | Tên cố vấn, thời điểm có dữ liệu, quyền sử dụng dữ liệu chưa biết | Xin bộ câu hỏi, điều kiện phân nhánh, checklist và nguồn; nội dung chưa duyệt chỉ dùng minh họa có nhãn | Trưởng nhóm + cố vấn do khách chỉ định |
| R02 | Nội dung khách gửi có tên cơ quan, trình tự, biểu mẫu, phí và thời hạn chưa kiểm chứng | Không chuyển thành kết luận pháp lý; xác nhận theo địa bàn và thời điểm trước khi hướng dẫn thật | Cố vấn |
| R03 | Địa bàn thử nghiệm chưa biết | Chưa tuyên bố quy trình đúng cho toàn quốc hoặc địa phương cụ thể | Trưởng nhóm |
| R04 | Ngày/giờ bắt đầu–kết thúc hai ngày chưa biết | Khung hai ngày × tám giờ là giả định, chưa phải lịch cam kết | Trưởng nhóm |
| R05 | Chưa có tên người dùng thật/thời điểm chạy thử | Khách chạy từng lát; chưa có người dùng thật thì báo đúng thử local, chưa chứng minh nhu cầu | Trưởng nhóm |
| R06 | Gemini free có hạn mức theo mô hình/dự án; chưa có key/quota xác minh | Kiểm tra trong AI Studio trước build tích hợp; không cam kết lượt hoặc tự chuyển sang trả phí | Trưởng nhóm + TV-A |
| R07 | Google dùng nội dung dịch vụ miễn phí để cải thiện sản phẩm và có thể có người rà soát | Không gửi thông tin cá nhân, bí mật hoặc nhạy cảm; chat thử bằng dữ liệu giả định/câu hỏi tổng quát, không tự đính kèm hồ sơ | Trưởng nhóm + TV-A + người rà bảo mật |
| R08 | Nhập chat tự do có thể chứa dữ liệu nhạy cảm hoặc yêu cầu giả nguồn | Pha 1 chốt biện pháp chặn/giảm dữ liệu, nguồn cho phép và kiểm tra đầu ra; chưa cam kết bộ lọc hoàn hảo | TV-A + người rà bảo mật |
| R09 | Chat thật tăng phạm vi trong hai ngày | Pha 1 ước lượng có đệm 20%, cắt Should trước; nếu vẫn không vừa, xin quyết định phạm vi/lịch, giữ QA | Trưởng nhóm |
| R10 | Chưa xác minh PostgreSQL, migration, CI và môi trường hiện tại | Kiểm tra theo từng bước sau cổng phù hợp; không suy ra từ kết quả bàn giao cũ | Trưởng nhóm |
| R11 | Chưa chốt quyền truy cập, thời hạn lưu/xóa và nghĩa vụ dữ liệu cá nhân | Pha 1 thiết kế tối thiểu và nhờ cố vấn xác nhận; chưa nhận chứng từ hoặc mở công khai | Trưởng nhóm + cố vấn |
| R12 | Trình duyệt điện thoại cụ thể, nội dung hình ảnh và quyền dùng ảnh chưa biết | Chốt trước UAT; minh họa có nhãn, không dùng giấy tờ thật chưa được phép | Trưởng nhóm + TV-B |

## Danh mục đầu vào do khách cung cấp

Chỉ là tài liệu khảo sát, chưa phải danh mục bắt buộc pháp lý:

1. Đăng ký kinh doanh.
2. Căn cước người đại diện (chỉ ghi trạng thái có/thiếu, không thu bản chụp).
3. Danh sách cổ đông và chủ sở hữu hưởng lợi.
4. Điều lệ công ty.
5. Quy chế tài chính nội bộ.
6. Sao kê tài khoản cá nhân chủ sở hữu/giám đốc (không thu nội dung).
7. Hóa đơn GTGT đầu vào, hợp đồng và biên bản giao nhận.
8. Bảng kê mua hàng theo mẫu áp dụng từng thời kỳ (tên/mốc mẫu khách nêu cần cố vấn xác nhận).
9. Hóa đơn GTGT đầu ra, hợp đồng và biên bản giao nhận.
10. Sổ phụ ngân hàng doanh nghiệp.
11. Sổ tài khoản loại 1–9.
12. Sổ chi tiết 131–331–341–338 nếu có.
13. Sổ kho, thẻ kho, nhập–xuất–tồn.
14. Bảng tổng hợp 131–331–341–338–112 nếu phù hợp.
15. Tờ khai GTGT.
16. Báo cáo tài chính.
17. Tờ khai quyết toán TNDN.
18. Tờ khai quyết toán TNCN.
19. Bảng kê mua/bán theo kỳ, tổng hợp theo năm.

Chủ đề khảo sát khách nêu: thời điểm thành lập, phát sinh doanh thu, thời kỳ thiếu kê khai, mức đầy đủ chứng từ, tình trạng kê khai, lao động/BHXH, tài sản/tồn kho, công nợ. Chưa chốt câu chữ hoặc quy tắc chẩn đoán. Không thu số tiền/số tài khoản khi chưa cần thiết.

## Nguồn kỹ thuật kiểm tra ngày 2026-10-30

- [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing): có tầng miễn phí cho một số mô hình, quyền truy cập có giới hạn. Chưa chọn model ID; cần đối chiếu tài khoản thực tế.
- [Rate limits](https://ai.google.dev/gemini-api/docs/rate-limits): giới hạn tùy mô hình và dự án; xem hạn mức trong AI Studio, không gán số cố định từ trí nhớ.
- [Gemini API Terms — Unpaid Services](https://ai.google.dev/gemini-api/terms): Google có thể xử lý đầu vào/đầu ra để cải thiện sản phẩm và cho người rà soát; yêu cầu không gửi thông tin nhạy cảm, bí mật hoặc cá nhân vào dịch vụ miễn phí.

Đây là nguồn kỹ thuật nhà cung cấp, không phải nguồn luật thuế. Chưa có văn bản thuế chính thức hoặc bộ nguồn được cố vấn duyệt trong phiên này.
