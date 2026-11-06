import { fireEvent, render, screen, within } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { AppShell } from './AppShell';

vi.mock('./UserMenu', () => ({ UserMenu: () => <div data-testid="user-menu" /> }));

const navigationLinks = [
  ['/', 'Trang chủ'],
  ['/khao-sat', 'Chuẩn bị hồ sơ'],
  ['/ho-so', 'Hồ sơ của tôi'],
  ['/cong-dong', 'Cộng đồng'],
  ['/chuyen-gia', 'Chuyên gia'],
  ['/phap-luat', 'Thư viện pháp luật'],
  ['/bang-gia', 'Bảng giá'],
];

function renderShell() {
  return render(
    <AppShell active="legal">
      <main id="main-content">Nội dung trang</main>
    </AppShell>,
  );
}

describe('AppShell navigation', () => {
  beforeEach(() => vi.clearAllMocks());

  it('keeps the seven horizontal links and starts with the mobile drawer closed', () => {
    renderShell();

    const desktopNavigation = screen.getByRole('navigation', { name: 'Điều hướng chính' });
    expect(within(desktopNavigation).getAllByRole('link')).toHaveLength(7);
    expect(screen.getByRole('button', { name: 'Mở menu điều hướng' })).toHaveAttribute(
      'aria-expanded',
      'false',
    );
    expect(screen.getByRole('button', { name: 'Mở menu điều hướng' })).toHaveAttribute(
      'aria-controls',
      'mobile-navigation',
    );
  });

  it('opens the mobile drawer with all seven large navigation targets', () => {
    renderShell();
    fireEvent.click(screen.getByRole('button', { name: 'Mở menu điều hướng' }));

    const drawer = screen.getByRole('navigation', { name: 'Điều hướng di động' });
    expect(screen.getByRole('button', { name: 'Đóng menu điều hướng' })).toHaveAttribute(
      'aria-expanded',
      'true',
    );
    expect(within(drawer).getAllByRole('link')).toHaveLength(7);
    navigationLinks.forEach(([href, label]) => {
      expect(within(drawer).getByRole('link', { name: label })).toHaveAttribute('href', href);
    });
  });

  it('closes from the X toggle and from the backdrop', () => {
    renderShell();
    fireEvent.click(screen.getByRole('button', { name: 'Mở menu điều hướng' }));
    fireEvent.click(screen.getByRole('button', { name: 'Đóng menu điều hướng' }));
    expect(screen.getByRole('button', { name: 'Mở menu điều hướng' })).toHaveAttribute(
      'aria-expanded',
      'false',
    );

    fireEvent.click(screen.getByRole('button', { name: 'Mở menu điều hướng' }));
    fireEvent.click(screen.getByRole('button', { name: 'Đóng menu' }));
    expect(screen.getByRole('button', { name: 'Mở menu điều hướng' })).toHaveAttribute(
      'aria-expanded',
      'false',
    );
  });

  it('closes on Escape and returns focus to the toggle', () => {
    renderShell();
    const toggle = screen.getByRole('button', { name: 'Mở menu điều hướng' });
    fireEvent.click(toggle);
    fireEvent.keyDown(document, { key: 'Escape' });

    expect(screen.getByRole('button', { name: 'Mở menu điều hướng' })).toHaveAttribute(
      'aria-expanded',
      'false',
    );
    expect(document.activeElement).toBe(toggle);
  });

  it('closes after selecting a mobile navigation link', () => {
    renderShell();
    fireEvent.click(screen.getByRole('button', { name: 'Mở menu điều hướng' }));
    const drawer = screen.getByRole('navigation', { name: 'Điều hướng di động' });
    fireEvent.click(within(drawer).getByRole('link', { name: 'Thư viện pháp luật' }));

    expect(screen.getByRole('button', { name: 'Mở menu điều hướng' })).toHaveAttribute(
      'aria-expanded',
      'false',
    );
  });
});
