import { ArrowRight, FileText, ListChecks, MessagesSquare, ShieldCheck } from 'lucide-react';
import Link from 'next/link';

import { HeroIllustration } from '@/components/features/home/HeroIllustration';
import { AppShell } from '@/components/features/navigation/AppShell';

const START_POINTS = [
  {
    href: '/khao-sat',
    icon: FileText,
    title: 'Trả lời khảo sát',
    text: '11 câu hỏi ngắn để ghi nhận tình trạng doanh nghiệp.',
  },
  {
    href: '/ho-so',
    icon: ListChecks,
    title: 'Xem checklist',
    text: 'Theo dõi giấy tờ đã có, còn thiếu và cần chuyên viên xác minh.',
  },
  {
    href: '/hoi-dap',
    icon: MessagesSquare,
    title: 'Hỏi đáp cùng AI',
    text: 'Giải thích tổng quát, kèm trích dẫn văn bản pháp luật.',
  },
];

export default function HomePage() {
  return (
    <AppShell active="home">
      <main id="main-content" className="page home-page">
        <section className="hero">
          <div className="hero-copy">
            <span className="pill">Trợ lý thủ tục giải thể &amp; thuế</span>
            <h1>
              Gỡ rối hồ sơ.
              <br />
              <span>Biết bước chuẩn bị tiếp theo.</span>
            </h1>
            <p className="hero-description">
              Tax Clear AI giúp doanh nghiệp từng hoạt động muốn giải thể ghi nhận tình trạng, sắp
              xếp giấy tờ và chuẩn bị cho buổi làm việc với chuyên viên.
            </p>
            <Link className="button button-primary button-large" href="/khao-sat">
              Bắt đầu chuẩn bị hồ sơ <ArrowRight size={18} />
            </Link>
            <p className="hero-note">
              <ShieldCheck size={16} /> Không cần tải giấy tờ hay nhập số thuế
            </p>
          </div>
          <div className="hero-visual">
            <HeroIllustration />
          </div>
        </section>
        <section className="start-section" aria-labelledby="start-heading">
          <h2 id="start-heading">Bạn có thể bắt đầu với:</h2>
          <ul className="start-cards">
            {START_POINTS.map(({ href, icon: Icon, title, text }) => (
              <li key={href}>
                <Link className="card start-card" href={href}>
                  <span className="icon-tile">
                    <Icon size={22} />
                  </span>
                  <span className="start-card-copy">
                    <strong>{title}</strong>
                    <span>{text}</span>
                  </span>
                  <ArrowRight className="start-card-arrow" size={18} />
                </Link>
              </li>
            ))}
          </ul>
        </section>
      </main>
    </AppShell>
  );
}
