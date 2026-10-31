import Link from 'next/link';

import { AppShell } from '@/components/features/navigation/AppShell';

export default function GuidePage() {
  return (
    <AppShell>
      <main id="main-content" className="content-main">
        <article className="surface guide-article">
          <span className="section-kicker">Hướng dẫn sử dụng</span>
          <h1>Chuẩn bị hồ sơ, từng bước.</h1>
          <h2>Ghi nhận đúng điều bạn biết</h2>
          <p>
            Đăng nhập bằng tài khoản được nhóm cấp và đi qua 11 câu hỏi. Nếu chưa biết, chọn Chưa
            biết hoặc để trống năm. Chọn Lưu và xem hồ sơ ở cuối để lưu phần chuẩn bị.
          </p>
          <h2>Ba trạng thái giấy tờ</h2>
          <ul>
            <li>
              <strong>Đã có:</strong> bạn đang giữ giấy tờ đó; chưa có nghĩa giấy tờ hợp lệ hoặc
              nghĩa vụ đã hoàn tất.
            </li>
            <li>
              <strong>Còn thiếu:</strong> bạn chưa tìm thấy giấy tờ.
            </li>
            <li>
              <strong>Cần xác minh:</strong> bạn hoặc chuyên viên cần kiểm tra thêm.
            </li>
          </ul>
          <p>Đổi trạng thái, đợi thông báo đã lưu và tải lại trang để kiểm tra.</p>
          <h2>Mở lại và quản lý</h2>
          <p>
            Sau khi đăng nhập, trang Hồ sơ của tôi liệt kê các hồ sơ đã lưu để bạn mở lại và bổ
            sung. Hồ sơ hết hạn truy cập sau 7 ngày nhưng vẫn hiện trong danh sách để bạn xóa. Mọi
            hồ sơ đều xóa được sau bước xác nhận.
          </p>
          <h2>Hỏi trợ lý bằng câu hỏi tổng quát</h2>
          <p>
            Chat không ghi nhớ câu trước và không tự gửi hồ sơ đã lưu. Google nhận câu hỏi để tạo
            phản hồi. Chỉ dùng dữ liệu giả định; không nhập tên, mã số thuế, căn cước, tài khoản
            hoặc chứng từ. Trợ lý không tính thuế/phạt hay kết luận hồ sơ.
          </p>
          <h2>Câu trả lời có trích văn bản pháp luật</h2>
          <p>
            Với câu hỏi về thủ tục giải thể hoặc chấm dứt mã số thuế, trợ lý trích nguyên văn một số
            điều khoản lấy từ cổng văn bản của Nhà nước và ghi ngày lấy văn bản. Các đoạn trích này
            chưa được chuyên gia rà soát và chưa xác minh còn hiệu lực hay đã bị sửa đổi. Hãy dùng
            để tìm hiểu, sau đó xác minh với chuyên viên trước khi áp dụng cho hồ sơ thật.
          </p>
          <Link className="button button-primary" href="/khao-sat">
            Mở bộ câu hỏi
          </Link>
        </article>
      </main>
    </AppShell>
  );
}
