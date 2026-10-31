import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { authService } from '@/services/auth.service';

import { LoginForm } from './LoginForm';

const navigation = vi.hoisted(() => ({ replace: vi.fn() }));
vi.mock('next/navigation', () => ({ useRouter: () => navigation }));
vi.mock('@/services/auth.service', () => ({ authService: { login: vi.fn() } }));

beforeEach(() => vi.resetAllMocks());

describe('Đăng nhập bản thử', () => {
  it.each([
    ['/ho-so/11111111-1111-4111-8111-111111111111', '/ho-so/11111111-1111-4111-8111-111111111111'],
    ['/ho-so', '/ho-so'],
    ['https://outside.example/collect', '/ho-so'],
  ])('mở lại đúng hồ sơ và từ chối redirect bên ngoài: %s', async (destination, expected) => {
    window.history.replaceState(null, '', `/dang-nhap?returnTo=${encodeURIComponent(destination)}`);
    vi.mocked(authService.login).mockResolvedValue({
      user: { id: 'u1', username: 'demo' },
      expiresAt: '',
    });
    render(<LoginForm />);
    fireEvent.change(screen.getByLabelText('Mật khẩu'), { target: { value: crypto.randomUUID() } });
    fireEvent.click(screen.getByRole('button', { name: 'Đăng nhập để chuẩn bị hồ sơ' }));
    await waitFor(() => expect(navigation.replace).toHaveBeenCalledWith(expected));
    window.history.replaceState(null, '', '/');
  });

  it('chỉ chuyển sang danh sách hồ sơ sau khi server xác nhận phiên', async () => {
    vi.mocked(authService.login).mockResolvedValue({
      user: { id: 'u1', username: 'demo' },
      expiresAt: '',
    });
    render(<LoginForm />);
    const password = crypto.randomUUID();
    fireEvent.change(screen.getByLabelText('Mật khẩu'), { target: { value: password } });
    fireEvent.click(screen.getByRole('button', { name: 'Đăng nhập để chuẩn bị hồ sơ' }));
    await waitFor(() => expect(authService.login).toHaveBeenCalledWith('demo', password));
    expect(navigation.replace).toHaveBeenCalledWith('/ho-so');
  });

  it('thông báo sai thông tin và cho phép nhập lại', async () => {
    vi.mocked(authService.login).mockRejectedValue(
      new Error('Tên đăng nhập hoặc mật khẩu chưa đúng.'),
    );
    render(<LoginForm />);
    fireEvent.change(screen.getByLabelText('Mật khẩu'), { target: { value: crypto.randomUUID() } });
    fireEvent.click(screen.getByRole('button', { name: 'Đăng nhập để chuẩn bị hồ sơ' }));
    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Tên đăng nhập hoặc mật khẩu chưa đúng.',
    );
    expect(navigation.replace).not.toHaveBeenCalled();
  });
});
