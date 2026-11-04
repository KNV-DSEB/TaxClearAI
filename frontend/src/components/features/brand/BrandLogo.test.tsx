import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { AnimatedMark } from './AnimatedMark';
import { FACETS, FACETS_SMALL } from './brand-geometry';
import { BrandLogo } from './BrandLogo';
import { BrandMark } from './BrandMark';

describe('Logo Tax Clear AI', () => {
  it('logo ngang có tên đọc được cho trình đọc màn hình và đủ 14 mặt cắt', () => {
    const { container } = render(<BrandLogo />);
    expect(screen.getByRole('img', { name: 'Tax Clear AI' })).toBeInTheDocument();
    expect(container.querySelectorAll('[data-warm]')).toHaveLength(2);
    expect(FACETS).toHaveLength(14);
  });

  it('dùng bản 7 mặt khi biểu tượng nhỏ hơn hoặc bằng 32 px để không nhòe', () => {
    const { container } = render(<BrandMark size={16} />);
    expect(container.querySelectorAll('path')).toHaveLength(FACETS_SMALL.length);
    expect(container.querySelector('svg')).toHaveAttribute('aria-hidden', 'true');
  });

  it('logo động chỉ trang trí, giãn thời điểm xuất hiện từng mặt', () => {
    const { container } = render(<AnimatedMark />);
    const facets = container.querySelectorAll('path.facet-in');
    expect(facets).toHaveLength(14);
    expect((facets[3] as SVGPathElement).style.animationDelay).toBe('135ms');
    expect(container.querySelector('svg')).toHaveAttribute('aria-hidden', 'true');
  });
});
