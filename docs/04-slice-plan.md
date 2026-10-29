# Kế hoạch MVP — Cổng 1 đã duyệt

Ngày lập: 2026-10-30. Giờ bên dưới tính từ khi bắt đầu ngày làm việc, không phải lịch đã hẹn. Ngày thực hiện cụ thể chưa biết. Mỗi ngày 8 giờ, ba người có thể làm song song theo quyền sở hữu; không coi 16 giờ là thời gian một người tự hoàn thành mọi việc.

Cập nhật: khách duyệt Cổng 1 và đổi phân công sang Codex tự thực hiện. S1 và S2 đã được khách thử, xác nhận phù hợp bản thử nội bộ; xem docs/07. Chưa ký MVP dùng dữ liệu thật, chưa có nguồn pháp lý cố vấn duyệt. QA/CI và giới hạn còn lại xem docs/10–12.

## Nhu cầu

Người dùng chính: chủ/người đại diện doanh nghiệp từng hoạt động muốn giải thể (B2). Hiện nhắn Zalo/gọi/gặp chuyên viên để phân tích hồ sơ rồi báo giá. Một việc MVP cần giải quyết: chuẩn bị thông tin và checklist để khảo sát, biết đã có gì/cần xác minh gì và tiếp tục được lần sau. Khó khăn, mức tiết kiệm và nhu cầu trả tiền chưa có số đo.

## S1 — skateboard — ngày 1, giờ 0–4

- Ai: khách hàng trong phiên đóng vai người đại diện; mời người dùng thật nếu khách có, không bịa danh tính.
- Việc: đăng nhập tài khoản thử → trả lời 11 câu chính → xem tổng hợp và checklist → đổi trạng thái một mục → tải lại thấy dữ liệu đã lưu PostgreSQL. Đây là một luồng xuyên UI–API–DB, không chờ xây xong từng lớp.
- Dữ liệu: bộ mẫu từ chủ đề/danh mục khách đã gửi; từng mục ghi chờ cố vấn xác nhận. Cố vấn duyệt nội dung thủ công trong tài liệu, chưa cần màn quản trị.
- Xong: US-01/02/03 và phần sử dụng US-05 có test chấp nhận tương ứng; DB thật lưu được; người khác không đọc/sửa được hồ sơ; kiểm tra backend/frontend đạt; khách chạy và phản hồi trước S2.
- Demo: cuối giờ 4. Người thử/thu phản hồi: khách hàng/trưởng nhóm; cần khách xác nhận có mặt trước khi bắt đầu. Nếu chưa hẹn được, vẫn có thể chuẩn bị môi trường nhưng chưa đánh dấu lát hoàn tất.

## S2 — bicycle, giả thuyết sau phản hồi S1 — ngày 1, giờ 4–8

- Ai: cùng người dùng S1; không mở thêm nhóm khách.
- Việc: từ kết quả chuẩn bị hồ sơ mở chat, hỏi tự do câu tổng quát không chứa dữ liệu riêng; nhận giải thích Gemini thật với nguồn được duyệt. Không tự gửi hồ sơ sang chat.
- Giả thuyết: giải thích tổng quát giúp người dùng hiểu mục cần chuẩn bị mà không cần AI xử lý nghĩa vụ cụ thể. Kiểm chứng bằng khách chỉ ra bước tiếp theo và nội dung còn khó hiểu; không tự đặt tỷ lệ thành công.
- Xong: US-04 xanh, có lượt gọi thật bằng key miễn phí, ca thiếu nguồn/quota/lỗi/dữ liệu nhạy cảm có xử lý, nguồn trả về thuộc tập duyệt; khách chạy và phản hồi. Mock không thay nghiệm thu Gemini thật.
- Demo cuối giờ 8, nếu S1 đã có phản hồi. Chưa có nguồn duyệt: chỉ demo chat giải thích nội dung sử dụng web công khai do nhóm duyệt, không tuyên bố giải thích luật đã kiểm chứng; Must về pháp lý vẫn chưa hoàn tất.

## Ngày 2 — QC, tích hợp và bàn giao

| Khoảng thời gian | Kết quả cần có |
|---|---|
| Giờ 0–2 | Rà diff, bảo mật, UI; tích hợp API–DB và E2E luồng chính; docs/08-test-plan.md, docs/10-defects.md |
| Giờ 2–3 | Khách UAT theo docs/09-uat-checklist.md, kiểm tra điện thoại/Chrome, phản hồi và xác nhận nội dung từ cố vấn |
| Giờ 3–4 | Runbook, rollback, kiểm tra CI thật nếu có quyền GitHub, báo số đo đường nóng và tổng hợp lỗi |
| Giờ 4–4:48 | Chốt bản release candidate, kiểm tra điều kiện tag, kết quả UAT; bản in Should chỉ làm nếu các Must và QA đã đạt |
| Giờ 4:48–8 | Đệm sửa lỗi/tích hợp 3 giờ 12 phút = 20% của tổng 16 giờ; chưa dùng thì bàn giao sớm |

Tổng: 12 giờ 48 phút có kế hoạch + 3 giờ 12 phút đệm. Lập test chấp nhận trước code trong mỗi lát, rà soát/chạy kiểm tra ngay trong lát; ngày 2 là QC mở rộng, không phải lần đầu chạy test. Thời gian chờ khách/cố vấn/key ngoài lịch chưa được tính là đã đáp ứng.

## Điều kiện khả thi và điểm dừng

- Trước S1: duyệt Cổng 1/API, PostgreSQL khả dụng, bí mật dev được cấp qua môi trường, khách hẹn demo. Các thay đổi migration/env trong docs/05 cần được duyệt rõ theo AGENTS.md mục 11.
- Trước S2: key Gemini free và model có quota, nguồn duyệt và biện pháp dữ liệu đã kiểm chứng. Không tự bật billing, tự cài dependency hoặc bỏ bảo mật để kịp giờ.
- Nếu thiếu nguồn cố vấn hoặc người dùng thật: chỉ bàn giao bản thử local có nhãn; chưa đạt mục tiêu MVP hướng dẫn pháp lý dùng thật. Nếu thiếu key/quota: chat Must chưa đạt, chưa gọi MVP hoàn chỉnh.
- Nếu quá sức chứa: bỏ bản in Should và hình trang trí; nếu vẫn không vừa, báo ngay để khách chọn giảm phạm vi hoặc đổi lịch. Giữ QA/UAT, không âm thầm kéo dài.
- Chặn phát hành khi Critical/Major trên luồng cốt lõi, kiểm tra bắt buộc đỏ, chat thật chưa xác minh hoặc UAT chưa ký. CI chưa chạy được thì báo chờ CI, chưa tag bản phát hành đạt chuẩn.

## Không làm lúc này

Tính tiền thuế/phạt hoặc báo giá; nhận chứng từ/CCCD/sao kê; thanh toán/sàn chuyên gia; thư viện luật toàn diện; HKD/chuyển đổi/lập hộ mới; microservice/vector DB; deploy công khai. Lý do: không cần cho một việc chuẩn bị khảo sát B2, thiếu cơ sở pháp lý hoặc tăng rủi ro/chi phí. Theo docs/01-brief.md, không mở rộng tự phát từ bản ý tưởng.

Sau từng demo, ghi docs/07-feedback-log.md: đã dùng, bỏ qua, khó khăn, yêu cầu thêm; quyết định sửa lát hiện tại hay sang S2. Thay đổi phạm vi phải cập nhật kế hoạch và xin khách quyết định.
