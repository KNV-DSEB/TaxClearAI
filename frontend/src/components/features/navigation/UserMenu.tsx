'use client';

import { ChevronDown, LogOut, MessageCircle, UserRound } from 'lucide-react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useEffect, useRef, useState } from 'react';

import { authService } from '@/services/auth.service';

function initials(username: string): string {
  const parts = username.split(/[\s._-]+/).filter(Boolean);
  const letters = parts.length > 1 ? parts[0][0] + parts[1][0] : username.slice(0, 2);
  return letters.toUpperCase();
}

export function UserMenu() {
  const router = useRouter();
  const [username, setUsername] = useState<string | null>(null);
  const [checked, setChecked] = useState(false);
  const [open, setOpen] = useState(false);
  const [error, setError] = useState('');
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const controller = new AbortController();
    authService
      .current(controller.signal)
      .then((user) => setUsername(user.username))
      .catch(() => setUsername(null))
      .finally(() => {
        if (!controller.signal.aborted) setChecked(true);
      });
    return () => controller.abort();
  }, []);

  useEffect(() => {
    if (!open) return;
    function close(event: MouseEvent | KeyboardEvent): void {
      if (
        event instanceof KeyboardEvent
          ? event.key === 'Escape'
          : !menuRef.current?.contains(event.target as Node)
      )
        setOpen(false);
    }
    document.addEventListener('mousedown', close);
    document.addEventListener('keydown', close);
    return () => {
      document.removeEventListener('mousedown', close);
      document.removeEventListener('keydown', close);
    };
  }, [open]);

  async function logout(): Promise<void> {
    setError('');
    try {
      await authService.logout();
      setUsername(null);
      setOpen(false);
      router.replace('/dang-nhap');
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Chưa đăng xuất được. Vui lòng thử lại.');
    }
  }

  if (!checked) return <span className="user-menu-placeholder" aria-hidden="true" />;
  if (!username)
    return (
      <Link className="button button-secondary button-small" href="/dang-nhap">
        <UserRound size={15} /> Đăng nhập
      </Link>
    );

  return (
    <div className="user-menu" ref={menuRef}>
      <button
        className="user-trigger"
        aria-haspopup="menu"
        aria-expanded={open}
        aria-label={`Tài khoản ${username}`}
        onClick={() => setOpen(!open)}
      >
        <span className="avatar">{initials(username)}</span>
        <ChevronDown size={15} />
      </button>
      {open && (
        <div className="user-dropdown" role="menu">
          <p className="user-name">{username}</p>
          <Link role="menuitem" href="/ho-so" onClick={() => setOpen(false)}>
            <UserRound size={15} /> Hồ sơ của tôi
          </Link>
          <Link role="menuitem" href="/hoi-dap" onClick={() => setOpen(false)}>
            <MessageCircle size={15} /> Hỏi đáp cùng AI
          </Link>
          <button
            role="menuitem"
            onClick={() => {
              void logout();
            }}
          >
            <LogOut size={15} /> Đăng xuất
          </button>
          {error && (
            <p role="alert" className="error-message">
              {error}
            </p>
          )}
        </div>
      )}
    </div>
  );
}
