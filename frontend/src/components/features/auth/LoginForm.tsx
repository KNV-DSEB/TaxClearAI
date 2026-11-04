'use client';

import { ArrowRight, Sparkles } from 'lucide-react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useState } from 'react';

import { authService } from '@/services/auth.service';

import { AnimatedMark } from '../brand/AnimatedMark';

function nextDestination(): string {
  const destination = new URLSearchParams(window.location.search).get('returnTo') ?? '';
  return /^\/ho-so(\/[a-f0-9-]{36})?$/.test(destination) ? destination : '/ho-so';
}

export function LoginForm() {
  const router = useRouter();
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  async function run(action: () => Promise<unknown>, fallback: string): Promise<void> {
    setBusy(true);
    setError('');
    try {
      await action();
      router.replace(nextDestination());
    } catch (error) {
      setError(error instanceof Error ? error.message : fallback);
    } finally {
      setBusy(false);
    }
  }

  function submit(event: React.FormEvent<HTMLFormElement>): void {
    event.preventDefault();
    const values = new FormData(event.currentTarget);
    void run(
      () => authService.login(String(values.get('username')), String(values.get('password'))),
      'Chưa đăng nhập được. Vui lòng thử lại.',
    );
  }

  return (
    <div className="login-layout">
      <section className="login-intro">
        <AnimatedMark size={76} />
        <h1>
          Giữ phần chuẩn bị
          <br />
          của bạn ở một nơi.
        </h1>
        <p>Dùng thử ngay không cần tài khoản, hoặc đăng nhập bằng tài khoản nhóm đã cấp.</p>
        <Link href="/">
          Tìm hiểu cách chuẩn bị <ArrowRight size={16} />
        </Link>
      </section>
      <div className="card login-form">
        <h2>Dùng thử ngay</h2>
        <p className="muted">
          Mỗi lượt dùng thử có tài khoản tạm riêng; hồ sơ của bạn không ai khác xem được. Chỉ dùng
          thông tin giả định.
        </p>
        <button
          className="button button-primary"
          type="button"
          disabled={busy}
          onClick={() => {
            void run(() => authService.guest(), 'Chưa mở được phiên dùng thử. Vui lòng thử lại.');
          }}
        >
          <Sparkles size={17} /> {busy ? 'Đang mở…' : 'Dùng thử không cần tài khoản'}
        </button>
        <form className="login-account" onSubmit={submit}>
          <h3>Đã có tài khoản</h3>
          <label htmlFor="username">Tên đăng nhập</label>
          <input
            id="username"
            name="username"
            autoComplete="username"
            required
            maxLength={100}
            spellCheck={false}
          />
          <label htmlFor="password">Mật khẩu</label>
          <input
            id="password"
            name="password"
            type="password"
            autoComplete="current-password"
            required
            maxLength={72}
          />
          <button className="button button-outline" type="submit" disabled={busy}>
            {busy ? 'Đang đăng nhập…' : 'Đăng nhập'}
            {!busy && <ArrowRight size={17} />}
          </button>
        </form>
        {error && (
          <p className="error-message" role="alert">
            {error}
          </p>
        )}
      </div>
    </div>
  );
}
