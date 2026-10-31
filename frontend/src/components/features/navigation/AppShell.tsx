import { ArrowUpRight, Files, House } from 'lucide-react';
import Link from 'next/link';

import { UserMenu } from './UserMenu';

type Section = 'home' | 'cases' | 'survey' | 'chat' | '';

export function AppShell({
  children,
  active = '',
}: {
  children: React.ReactNode;
  active?: Section;
}) {
  const current = (section: Section) => (active === section ? 'page' : undefined);
  return (
    <div className="app-canvas">
      <a className="skip-link" href="#main-content">
        Đến nội dung chính
      </a>
      <header className="site-header">
        <Link href="/" className="brand" aria-label="Tax Clear AI — Trang chủ">
          <span className="brand-icon">
            <Files size={20} strokeWidth={1.8} />
          </span>
          <span>
            Tax Clear<span className="brand-ai"> AI</span>
          </span>
        </Link>
        <nav aria-label="Điều hướng chính">
          <Link href="/" aria-current={current('home')}>
            <House size={15} /> Trang chủ
          </Link>
          <Link href="/ho-so" aria-current={current('cases')}>
            Hồ sơ của tôi
          </Link>
          <Link href="/khao-sat" aria-current={current('survey')}>
            Chuẩn bị hồ sơ <ArrowUpRight size={14} />
          </Link>
        </nav>
        <UserMenu />
      </header>
      {children}
      <footer className="site-footer">
        <span>Tax Clear AI · Bản thử nghiệm · Chỉ dùng dữ liệu giả định.</span>
        <Link href="/huong-dan">Hướng dẫn sử dụng</Link>
      </footer>
    </div>
  );
}
