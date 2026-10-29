import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

import { Steps } from './Steps';

const items = [
  { title: 'Tải lên', description: 'Chọn file .xlsx' },
  { title: 'Xem trước', description: 'Kiểm tra dữ liệu' },
  { title: 'Xác nhận' },
];

describe('Steps', () => {
  it('renders the title and description of every item', () => {
    render(<Steps items={items} current={0} />);

    expect(screen.getByText('Tải lên')).toBeInTheDocument();
    expect(screen.getByText('Chọn file .xlsx')).toBeInTheDocument();
    expect(screen.getByText('Xem trước')).toBeInTheDocument();
    expect(screen.getByText('Xác nhận')).toBeInTheDocument();
  });

  it('numbers a wait/process step by its position when it has no custom icon', () => {
    render(<Steps items={items} current={1} />);

    expect(screen.getByText('2')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();
  });

  it('lets an explicit per-item status override the position-derived one', () => {
    const withError = [items[0], { ...items[1], status: 'error' as const }, items[2]];
    render(<Steps items={withError} current={1} />);

    expect(screen.getByText('Xem trước')).toHaveClass('text-destructive');
  });

  it('calls onChange with the clicked step index when steps are clickable', () => {
    const onChange = vi.fn();
    render(<Steps items={items} current={1} onChange={onChange} />);

    fireEvent.click(screen.getByRole('button', { name: /xác nhận/i }));

    expect(onChange).toHaveBeenCalledWith(2);
  });

  it('renders steps as plain (non-interactive) content when onChange is not provided', () => {
    render(<Steps items={items} current={1} />);

    expect(screen.queryByRole('button')).not.toBeInTheDocument();
  });
});
