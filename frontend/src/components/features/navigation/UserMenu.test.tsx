import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { ApiError } from '@/services/api.client';
import { authService } from '@/services/auth.service';

import { UserMenu } from './UserMenu';

const navigation = vi.hoisted(() => ({ replace: vi.fn() }));
vi.mock('next/navigation', () => ({ useRouter: () => navigation }));
vi.mock('@/services/auth.service', () => ({
  authService: { current: vi.fn(), logout: vi.fn() },
}));

beforeEach(() => vi.resetAllMocks());

describe('Menu tài khoản', () => {
  it('mời đăng nhập khi chưa có phiên', async () => {
    vi.mocked(authService.current).mockRejectedValue(new ApiError(401, 'Phiên đã hết hạn.'));
    render(<UserMenu />);
    expect(await screen.findByRole('link', { name: /Đăng nhập/ })).toHaveAttribute(
      'href',
      '/dang-nhap',
    );
  });

  it('hiện chữ viết tắt và đăng xuất qua service rồi mở màn đăng nhập', async () => {
    vi.mocked(authService.current).mockResolvedValue({ id: 'u1', username: 'vinh-khanh' });
    vi.mocked(authService.logout).mockResolvedValue(undefined);
    render(<UserMenu />);
    fireEvent.click(await screen.findByRole('button', { name: 'Tài khoản vinh-khanh' }));
    expect(screen.getByText('VK')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('menuitem', { name: /Đăng xuất/ }));
    await waitFor(() => expect(navigation.replace).toHaveBeenCalledWith('/dang-nhap'));
  });

  it('không giả vờ đã đăng xuất khi API lỗi', async () => {
    vi.mocked(authService.current).mockResolvedValue({ id: 'u1', username: 'demo' });
    vi.mocked(authService.logout).mockRejectedValue(new Error('Chưa đăng xuất được.'));
    render(<UserMenu />);
    fireEvent.click(await screen.findByRole('button', { name: 'Tài khoản demo' }));
    fireEvent.click(screen.getByRole('menuitem', { name: /Đăng xuất/ }));
    expect(await screen.findByRole('alert')).toHaveTextContent('Chưa đăng xuất được.');
    expect(navigation.replace).not.toHaveBeenCalled();
  });
});
