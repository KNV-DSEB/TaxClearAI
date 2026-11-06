import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

import { PlanDialog } from './PlanDialog';

const counts = { available: 3, missing: 0, needsVerification: 16 };

describe('Cửa sổ gợi ý gói sau khảo sát', () => {
  it('nêu giá trị đã có trước, chỉ hiện nhóm có mục', () => {
    render(<PlanDialog counts={counts} onOpenChange={vi.fn()} open />);
    expect(screen.getByRole('dialog', { name: /Đã có danh mục giấy tờ/ })).toBeInTheDocument();
    expect(screen.getByText('3 đã có')).toBeInTheDocument();
    expect(screen.getByText('16 cần xác minh')).toBeInTheDocument();
    expect(screen.queryByText(/0 còn thiếu/)).not.toBeInTheDocument();
  });

  it('cho tiếp tục miễn phí và hỏi AI, hai gói trả phí ghi rõ chưa thu phí', () => {
    render(<PlanDialog counts={counts} onOpenChange={vi.fn()} open />);
    expect(screen.getByRole('button', { name: 'Xem hồ sơ của tôi' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Hỏi AI tiếp/ })).toHaveAttribute('href', '/hoi-dap');
    expect(screen.getAllByText('Sắp mở, chưa thu phí')).toHaveLength(2);
    expect(screen.getByText('250.000 đ')).toBeInTheDocument();
    expect(screen.getByText('Phí nền tảng 15%')).toBeInTheDocument();
  });

  it('đóng được bằng nút Tiếp tục miễn phí và nút đóng', () => {
    const onOpenChange = vi.fn();
    render(<PlanDialog counts={counts} onOpenChange={onOpenChange} open />);
    fireEvent.click(screen.getByRole('button', { name: 'Xem hồ sơ của tôi' }));
    fireEvent.click(screen.getByRole('button', { name: 'Đóng' }));
    expect(onOpenChange).toHaveBeenCalledTimes(2);
    expect(onOpenChange).toHaveBeenCalledWith(false);
  });

  it('dẫn tới chi tiết gói hỗ trợ và danh sách chuyên gia trong hồ sơ', () => {
    render(<PlanDialog counts={counts} onOpenChange={vi.fn()} open />);
    expect(screen.getByRole('link', { name: 'Xem gói này' })).toHaveAttribute(
      'href',
      '/bang-gia#goi-ho-tro',
    );
    expect(screen.getByRole('link', { name: 'Xem chuyên gia phù hợp' })).toHaveAttribute(
      'href',
      '#experts',
    );
  });

  it('không hiện khi đang đóng', () => {
    render(<PlanDialog counts={counts} onOpenChange={vi.fn()} open={false} />);
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });
});
