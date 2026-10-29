import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

import { Pagination } from './Pagination';

describe('Pagination', () => {
  it('renders the total record count', () => {
    render(<Pagination page={1} size={10} total={42} onPageChange={vi.fn()} onSizeChange={vi.fn()} />);
    expect(screen.getByText('Tổng: 42 bản ghi')).toBeInTheDocument();
  });

  it('disables the previous button on the first page', () => {
    render(<Pagination page={1} size={10} total={42} onPageChange={vi.fn()} onSizeChange={vi.fn()} />);
    expect(screen.getByText('Trước').closest('button')).toBeDisabled();
  });

  it('disables the next button on the last page', () => {
    render(<Pagination page={5} size={10} total={42} onPageChange={vi.fn()} onSizeChange={vi.fn()} />);
    expect(screen.getByText('Sau').closest('button')).toBeDisabled();
  });

  it('calls onPageChange when a page number is clicked', () => {
    const onPageChange = vi.fn();
    render(<Pagination page={1} size={10} total={42} onPageChange={onPageChange} onSizeChange={vi.fn()} />);

    fireEvent.click(screen.getByText('3'));

    expect(onPageChange).toHaveBeenCalledWith(3);
  });

  it('calls onPageChange when jumping to a valid page', () => {
    const onPageChange = vi.fn();
    render(<Pagination page={1} size={10} total={42} onPageChange={onPageChange} onSizeChange={vi.fn()} />);

    fireEvent.change(screen.getByPlaceholderText('Trang'), { target: { value: '4' } });
    fireEvent.click(screen.getByText('Đi tới'));

    expect(onPageChange).toHaveBeenCalledWith(4);
  });

  it('does not call onPageChange when the jump target is out of range', () => {
    const onPageChange = vi.fn();
    render(<Pagination page={1} size={10} total={42} onPageChange={onPageChange} onSizeChange={vi.fn()} />);

    fireEvent.change(screen.getByPlaceholderText('Trang'), { target: { value: '99' } });
    fireEvent.click(screen.getByText('Đi tới'));

    expect(onPageChange).not.toHaveBeenCalled();
  });

  it('does not call onPageChange when the jump target is not a number', () => {
    const onPageChange = vi.fn();
    render(<Pagination page={1} size={10} total={42} onPageChange={onPageChange} onSizeChange={vi.fn()} />);

    fireEvent.change(screen.getByPlaceholderText('Trang'), { target: { value: 'abc' } });
    fireEvent.click(screen.getByText('Đi tới'));

    expect(onPageChange).not.toHaveBeenCalled();
  });

  it('calls onSizeChange when the page size is changed', () => {
    const onSizeChange = vi.fn();
    render(<Pagination page={1} size={10} total={42} onPageChange={vi.fn()} onSizeChange={onSizeChange} pageSizeOptions={[10, 20]} />);

    fireEvent.click(screen.getByRole('combobox'));
    fireEvent.click(screen.getByText('20 / trang'));

    expect(onSizeChange).toHaveBeenCalledWith(20);
  });
});
