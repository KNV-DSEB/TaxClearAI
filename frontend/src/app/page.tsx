import { ArrowRight, Check, FileCheck2, ListChecks, RotateCcw } from 'lucide-react';
import Link from 'next/link';

import { DocumentIllustration } from '@/components/features/assessments/DocumentIllustration';
import { AppShell } from '@/components/features/navigation/AppShell';

export default function HomePage() {
  return (
    <AppShell active="home">
      <main id="main-content" className="home-main">
        <section className="hero">
          <div className="hero-copy">
            <span className="section-kicker">Dành cho doanh nghiệp muốn giải thể</span>
            <h1>
              Gỡ rối hồ sơ.
              <br />
              <span>Biết bước chuẩn bị tiếp theo.</span>
            </h1>
            <p className="hero-description">
              Giấy tờ rải rác, tình trạng kê khai chưa rõ? Bắt đầu bằng một bộ câu hỏi để tổng hợp
              thông tin và chuẩn bị cho buổi khảo sát với chuyên viên.
            </p>
            <Link className="button button-primary" href="/khao-sat">
              Bắt đầu chuẩn bị hồ sơ <ArrowRight size={18} />
            </Link>
            <p className="hero-note">
              <Check size={16} /> Chưa cần tải giấy tờ hay nhập số tiền thuế
            </p>
          </div>
          <div className="hero-visual">
            <DocumentIllustration />
            <span className="illustration-caption">Hình minh họa sắp xếp hồ sơ</span>
          </div>
        </section>
        <section className="journey" aria-labelledby="journey-heading">
          <div className="section-intro">
            <h2 id="journey-heading">Một hồ sơ rõ ràng hơn, từ đâu?</h2>
            <p>Đi từ thông tin bạn biết đến những điều cần xác minh.</p>
          </div>
          <ol className="journey-steps">
            <li>
              <span className="step-symbol">
                <ListChecks size={22} />
              </span>
              <div>
                <span className="step-caption">Bước 1 · Ghi nhận</span>
                <h3>Trả lời về tình trạng hiện tại</h3>
                <p>11 câu hỏi. Chưa biết câu nào, cứ ghi nhận đúng như vậy.</p>
              </div>
            </li>
            <li>
              <span className="step-symbol">
                <FileCheck2 size={22} />
              </span>
              <div>
                <span className="step-caption">Bước 2 · Sắp xếp</span>
                <h3>Xem danh mục cần khảo sát</h3>
                <p>Phân biệt giấy tờ đã có, còn thiếu và cần chuyên viên xác minh.</p>
              </div>
            </li>
            <li>
              <span className="step-symbol">
                <RotateCcw size={22} />
              </span>
              <div>
                <span className="step-caption">Bước 3 · Tiếp tục</span>
                <h3>Lưu lại để bổ sung sau</h3>
                <p>Mở lại hồ sơ và cập nhật khi bạn tìm thêm được giấy tờ.</p>
              </div>
            </li>
          </ol>
        </section>
        <aside className="disclosure">
          <strong>Đang thử nghiệm cùng bạn.</strong>
          <p>
            Nội dung khảo sát và danh mục hồ sơ đang chờ cố vấn xác nhận. Kết quả chưa thay thế
            hướng dẫn từ cơ quan tiếp nhận hoặc tư vấn chuyên môn.
          </p>
        </aside>
      </main>
    </AppShell>
  );
}
