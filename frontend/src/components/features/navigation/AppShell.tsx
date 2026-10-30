import { ArrowUpRight, Files } from 'lucide-react';
import Link from 'next/link';

export function AppShell({
  children,
  active = '',
}: {
  children: React.ReactNode;
  active?: 'survey' | 'home' | '';
}) {
  return (
    <>
      <a className="skip-link" href="#main-content">
        Đến nội dung chính
      </a>
      <header className="site-header">
        <Link href="/" className="brand" aria-label="Tax Clear AI — Trang chủ">
          <span className="brand-icon">
            <Files size={24} strokeWidth={1.7} />
          </span>
          <span>
            Tax Clear<span className="brand-ai"> AI</span>
          </span>
        </Link>
        <nav aria-label="Điều hướng chính">
          <Link href="/" aria-current={active === 'home' ? 'page' : undefined}>
            Giới thiệu
          </Link>
          <Link href="/khao-sat" aria-current={active === 'survey' ? 'page' : undefined}>
            Chuẩn bị hồ sơ <ArrowUpRight size={15} />
          </Link>
        </nav>
        <span className="trial-label">
          <span /> Bản thử nghiệm
        </span>
      </header>
      {children}
      <footer className="site-footer">
        <span>Tax Clear AI · Chuẩn bị rõ ràng, từng bước một.</span>
      </footer>
    </>
  );
}
