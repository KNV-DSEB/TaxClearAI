'use client';

import { LOGO_WIDTH, WORDMARK_ON_DARK_SVG, WORDMARK_SVG } from './brand-geometry';
import { useMarkMarkup } from './BrandMark';

// Logo ngang: biểu tượng + wordmark vẽ bằng đường vector (không phụ thuộc font)
export function BrandLogo({ height = 36, onDark = false }: { height?: number; onDark?: boolean }) {
  const mark = useMarkMarkup(height <= 32);
  return (
    <svg
      viewBox={`0 0 ${LOGO_WIDTH} 64`}
      height={height}
      width={(height * LOGO_WIDTH) / 64}
      role="img"
      aria-label="Tax Clear"
    >
      {/* Markup sinh sẵn từ build_brand.py, không có dữ liệu người dùng */}
      <g transform="scale(0.5)" dangerouslySetInnerHTML={{ __html: mark }} />
      <g dangerouslySetInnerHTML={{ __html: onDark ? WORDMARK_ON_DARK_SVG : WORDMARK_SVG }} />
    </svg>
  );
}
