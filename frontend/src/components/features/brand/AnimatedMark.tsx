import { FACETS } from './brand-geometry';
import { Facets } from './BrandMark';

// Các mặt cắt ghép lại rồi ánh vàng nghệ lóe lên; tắt khi người dùng chọn giảm chuyển động
export function AnimatedMark({ size = 72 }: { size?: number }) {
  return (
    <svg
      viewBox="0 0 64 64"
      width={size}
      height={size}
      aria-hidden="true"
      className="animated-mark"
    >
      <Facets facets={FACETS} className="facet-in" />
    </svg>
  );
}
