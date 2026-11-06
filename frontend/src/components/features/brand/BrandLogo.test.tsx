import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { AnimatedMark } from './AnimatedMark';
import { BrandLogo } from './BrandLogo';
import { BrandMark } from './BrandMark';

describe('Logo Tax Clear', () => {
  it('logo ngang có tên đọc được cho trình đọc màn hình và đủ khiên, chữ C, dấu tick', () => {
    const { container } = render(<BrandLogo />);
    expect(screen.getByRole('img', { name: 'Tax Clear' })).toBeInTheDocument();
    expect(container.querySelector('.mk-shield')).not.toBeNull();
    expect(container.querySelector('.mk-c')).not.toBeNull();
    expect(container.querySelector('.mk-tick')).not.toBeNull();
  });

  it('mỗi logo trên cùng trang có mã gradient riêng', () => {
    const { container } = render(
      <>
        <BrandMark size={48} />
        <BrandMark size={48} />
      </>,
    );
    const ids = Array.from(container.querySelectorAll('linearGradient')).map((node) => node.id);
    expect(new Set(ids).size).toBe(ids.length);
    expect(container.innerHTML).not.toContain('__ID__');
  });

  it('dùng bản không đổ bóng khi biểu tượng nhỏ hơn hoặc bằng 32 px', () => {
    const { container } = render(<BrandMark size={16} />);
    expect(container.querySelector('.mk-c')).not.toHaveAttribute('filter');
    expect(container.querySelector('svg')).toHaveAttribute('aria-hidden', 'true');
  });

  it('logo động chỉ để trang trí', () => {
    const { container } = render(<AnimatedMark />);
    expect(container.querySelector('svg')).toHaveClass('animated-mark');
    expect(container.querySelector('svg')).toHaveAttribute('aria-hidden', 'true');
  });
});
