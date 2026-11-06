import {
  ArrowRight,
  BookOpenText,
  BriefcaseBusiness,
  FileText,
  ListChecks,
  MessagesSquare,
  ShieldCheck,
  UsersRound,
} from 'lucide-react';
import Link from 'next/link';

import { HeroPhoto } from '@/components/features/home/HeroPhoto';
import { AppShell } from '@/components/features/navigation/AppShell';

const START_POINTS = [
  {
    href: '/khao-sat',
    icon: FileText,
    title: 'Trả lời khảo sát',
    text: 'Các câu hỏi ngắn để ghi nhận tình trạng của doanh nghiệp. Câu nào chưa rõ, chọn “không biết” hoặc bỏ trống.',
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
  {
    href: '/cong-dong',
    icon: UsersRound,
    title: 'Cộng đồng hỏi đáp',
    text: 'Tìm tình huống thực tế và chia sẻ câu hỏi với cộng đồng.',
  },
  {
    href: '/chuyen-gia',
    icon: BriefcaseBusiness,
    title: 'Chuyên gia hỗ trợ',
    text: 'Tìm chuyên gia pháp lý, thuế phù hợp và đặt lịch tư vấn.',
  },
  {
    href: '/phap-luat',
    icon: BookOpenText,
    title: 'Tra cứu pháp luật',
    text: 'Tìm thủ tục hiện hành, xem checklist và mở nguồn văn bản gốc.',
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
              Giải thể gọn gàng.
              <br />
              <span>An tâm sang trang.</span>
            </h1>
            <p className="hero-description">
              Tax Clear giúp doanh nghiệp từng hoạt động muốn giải thể ghi nhận tình trạng, sắp xếp
              giấy tờ và chuẩn bị cho buổi làm việc với chuyên viên.
            </p>
            <Link className="button button-primary button-large" href="/khao-sat">
              Bắt đầu chuẩn bị hồ sơ <ArrowRight size={18} />
            </Link>
            <p className="hero-note">
              <ShieldCheck size={16} /> Không cần tải giấy tờ hay nhập số thuế
            </p>
          </div>
          <div className="hero-visual">
            <HeroPhoto />
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
