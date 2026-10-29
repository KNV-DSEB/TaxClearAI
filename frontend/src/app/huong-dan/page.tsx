import Link from 'next/link';

import { AppShell } from '@/components/features/navigation/AppShell';

export default function GuidePage() {
  return (
    <AppShell>
      <main id="main-content" className="content-main">
        <article className="surface guide-article">
          <span className="section-kicker">Hướng dẫn sử dụng bản thử</span>
          <h1>Chuẩn bị hồ sơ, từng bước.</h1>
          <p className="guide-notice">
            Đây là tài liệu sử dụng Tax Clear AI, không phải văn bản pháp luật. Nội dung hồ sơ đang
            chờ cố vấn xác nhận.
          </p>
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
          <p>
            Checklist là danh mục gợi ý để khảo sát, chưa phải danh sách pháp lý bắt buộc. Đổi trạng
            thái, đợi thông báo đã lưu và tải lại trang để kiểm tra.
          </p>
          <h2>Mở lại và quản lý</h2>
          <p>
            Giữ đường dẫn trang hồ sơ. Sau đăng nhập, bạn có thể mở lại để bổ sung. Hồ sơ hết hạn
            truy cập sau 7 ngày; bản thử chưa tự xóa dữ liệu khỏi ổ đĩa. Bạn có thể xóa hồ sơ đang
            hiệu lực sau bước xác nhận.
          </p>
          <h2>Hỏi trợ lý bằng câu hỏi tổng quát</h2>
          <p>
            Chat không ghi nhớ câu trước và không tự gửi hồ sơ đã lưu. Google nhận câu hỏi để tạo
            phản hồi. Chỉ dùng dữ liệu giả định; không nhập tên, mã số thuế, căn cước, tài khoản
            hoặc chứng từ. Trợ lý không tính thuế/phạt hay kết luận hồ sơ; khi thiếu nguồn pháp luật
            đã duyệt, hãy trao đổi với chuyên viên.
          </p>
          <p className="small muted">
            Hướng dẫn này chỉ giải thích cách sử dụng bản thử. Nội dung nghiệp vụ cần được cố vấn
            xác nhận trước khi áp dụng cho hồ sơ thật.
          </p>
          <Link className="button button-primary" href="/khao-sat">
            Mở bộ câu hỏi
          </Link>
        </article>
      </main>
    </AppShell>
  );
}
