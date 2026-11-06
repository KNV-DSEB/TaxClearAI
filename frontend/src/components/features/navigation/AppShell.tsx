'use client';

import {
  ArrowUpRight,
  BookOpenText,
  BriefcaseBusiness,
  FileText,
  FolderOpen,
  House,
  Menu,
  Tags,
  UsersRound,
  X,
} from 'lucide-react';
import Link from 'next/link';
import { useEffect, useRef, useState } from 'react';

import { BrandLogo } from '../brand/BrandLogo';

import { UserMenu } from './UserMenu';

type Section = 'home' | 'cases' | 'survey' | 'chat' | 'community' | 'experts' | 'legal' | 'pricing' | '';

const NAVIGATION_ITEMS = [
  { href: '/', section: 'home', label: 'Trang chủ', icon: House },
  { href: '/khao-sat', section: 'survey', label: 'Chuẩn bị hồ sơ', icon: FileText },
  { href: '/ho-so', section: 'cases', label: 'Hồ sơ của tôi', icon: FolderOpen },
  { href: '/cong-dong', section: 'community', label: 'Cộng đồng', icon: UsersRound },
  { href: '/chuyen-gia', section: 'experts', label: 'Chuyên gia', icon: BriefcaseBusiness },
  { href: '/phap-luat', section: 'legal', label: 'Thư viện pháp luật', icon: BookOpenText },
  { href: '/bang-gia', section: 'pricing', label: 'Bảng giá', icon: Tags },
] as const;

export function AppShell({
  children,
  active = '',
}: {
  children: React.ReactNode;
  active?: Section;
}) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const toggleRef = useRef<HTMLButtonElement>(null);
  const mobileNavigationRef = useRef<HTMLElement>(null);
  const current = (section: Section) => (active === section ? 'page' : undefined);

  useEffect(() => {
    if (!mobileMenuOpen) return;
    mobileNavigationRef.current?.querySelector('a')?.focus();

    function handleEscape(event: KeyboardEvent): void {
      if (event.key === 'Escape') {
        setMobileMenuOpen(false);
        toggleRef.current?.focus();
      }
    }

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [mobileMenuOpen]);
  return (
    <div className="app-canvas">
      <a className="skip-link" href="#main-content">
        Đến nội dung chính
      </a>
      <header className="site-header">
        <Link href="/" className="brand" aria-label="Tax Clear — Trang chủ">
          <BrandLogo height={44} />
        </Link>
        <nav className="desktop-navigation" aria-label="Điều hướng chính">
          {NAVIGATION_ITEMS.map(({ href, section, label, icon: Icon }) => (
            <Link href={href} aria-current={current(section)} key={href}>
              <Icon size={15} /> {label}
              {section === 'survey' && <ArrowUpRight size={14} />}
            </Link>
          ))}
        </nav>
        <div
          aria-hidden={!mobileMenuOpen}
          className={`mobile-navigation-layer ${mobileMenuOpen ? 'is-open' : ''}`}
        >
          <button
            aria-label="Đóng menu"
            className="mobile-navigation-backdrop"
            onClick={() => {
              setMobileMenuOpen(false);
              toggleRef.current?.focus();
            }}
            tabIndex={mobileMenuOpen ? 0 : -1}
            type="button"
          />
          <nav
            aria-label="Điều hướng di động"
            className="mobile-navigation-drawer"
            id="mobile-navigation"
            ref={mobileNavigationRef}
          >
            {NAVIGATION_ITEMS.map(({ href, section, label, icon: Icon }) => (
              <Link
                aria-current={current(section)}
                className="mobile-navigation-link"
                href={href}
                key={href}
                onClick={() => {
                  setMobileMenuOpen(false);
                  toggleRef.current?.focus();
                }}
                tabIndex={mobileMenuOpen ? 0 : -1}
              >
                <Icon aria-hidden="true" size={20} />
                <span>{label}</span>
              </Link>
            ))}
          </nav>
        </div>
        <UserMenu />
        <button
          aria-controls="mobile-navigation"
          aria-expanded={mobileMenuOpen}
          aria-label={mobileMenuOpen ? 'Đóng menu điều hướng' : 'Mở menu điều hướng'}
          className="mobile-navigation-toggle"
          onClick={() => setMobileMenuOpen((isOpen) => !isOpen)}
          ref={toggleRef}
          type="button"
        >
          <Menu
            className={`mobile-menu-icon ${mobileMenuOpen ? 'is-hidden' : ''}`}
            aria-hidden="true"
            size={24}
          />
          <X
            className={`mobile-menu-icon ${mobileMenuOpen ? '' : 'is-hidden'}`}
            aria-hidden="true"
            size={24}
          />
        </button>
      </header>
      {children}
      <footer className="site-footer">
        <span>Tax Clear · Bản thử nghiệm · Chỉ dùng dữ liệu giả định.</span>
        <Link href="/huong-dan">Hướng dẫn sử dụng</Link>
      </footer>
    </div>
  );
}
