import { render, screen, within } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { PricingOverview } from './PricingOverview';

describe('Trang bảng giá', () => {
  it('nói rõ bản thử chưa thu phí và giá là dự kiến', () => {
    render(<PricingOverview />);
    expect(screen.getByRole('note')).toHaveTextContent(/chưa thu phí/);
    expect(screen.getByRole('note')).toHaveTextContent(/dự kiến/);
  });

  it('hiện ba gói theo thứ tự tự làm, có người rà, chuyên gia', () => {
    render(<PricingOverview />);
    const plans = within(screen.getByRole('list', { name: 'Ba mức hỗ trợ' })).getAllByRole(
      'article',
    );
    expect(
      plans.map((plan) => within(plan).getByRole('heading', { level: 2 }).textContent),
    ).toEqual(['Tra cứu cơ bản', 'Hỗ trợ hoàn thiện hồ sơ', 'Kết nối chuyên gia']);
  });

  it('chỉ gói miễn phí có nút dùng thử, gói trả phí không có nút mua', () => {
    render(<PricingOverview />);
    expect(screen.getByRole('link', { name: /Dùng thử miễn phí/ })).toHaveAttribute(
      'href',
      '/khao-sat',
    );
    expect(
      screen.queryByRole('button', { name: /mua|thanh toán|đăng ký gói/i }),
    ).not.toBeInTheDocument();
    expect(screen.getByText(/Chưa mở bán/)).toBeInTheDocument();
  });
});
