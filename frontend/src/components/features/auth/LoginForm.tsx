'use client';

import { ArrowRight, LockKeyhole } from 'lucide-react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useState } from 'react';

import { authService } from '@/services/auth.service';

export function LoginForm() {
  const router = useRouter();
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  async function submit(event: React.FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setBusy(true);
    setError('');
    const values = new FormData(event.currentTarget);
    try {
      await authService.login(String(values.get('username')), String(values.get('password')));
      const destination = new URLSearchParams(window.location.search).get('returnTo') ?? '';
      router.replace(/^\/ho-so(\/[a-f0-9-]{36})?$/.test(destination) ? destination : '/ho-so');
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Chưa đăng nhập được. Vui lòng thử lại.');
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="login-layout">
      <section className="login-intro">
        <LockKeyhole size={30} />
        <h1>
          Giữ phần chuẩn bị
          <br />
          của bạn ở một nơi.
        </h1>
        <p>Đăng nhập bằng tài khoản nhóm đã cấp để lưu và mở lại hồ sơ thử nghiệm.</p>
        <Link href="/">
          Tìm hiểu cách chuẩn bị <ArrowRight size={16} />
        </Link>
      </section>
      <form
        className="card login-form"
        onSubmit={(event) => {
          void submit(event);
        }}
      >
        <h2>Đăng nhập bản thử</h2>
        <p className="muted">Chỉ sử dụng thông tin giả định trong giai đoạn này.</p>
        <label htmlFor="username">Tên đăng nhập</label>
        <input
          id="username"
          name="username"
          autoComplete="username"
          defaultValue="demo"
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
        {error && (
          <p className="error-message" role="alert">
            {error}
          </p>
        )}
        <button className="button button-primary" type="submit" disabled={busy}>
          {busy ? 'Đang đăng nhập…' : 'Đăng nhập để chuẩn bị hồ sơ'}
          {!busy && <ArrowRight size={17} />}
        </button>
        <p className="small muted">
          Chưa có tài khoản? Liên hệ trưởng nhóm để được cấp quyền thử nghiệm.
        </p>
      </form>
    </div>
  );
}
